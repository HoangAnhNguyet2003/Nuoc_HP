from pymongo import MongoClient
import pandas as pd
import numpy as np
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.ensemble import IsolationForest
import tensorflow as tf

# Kết nối tới MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['HP_water']
file_path = 'data/raw_data/Van_Dau8/luu_luong.csv'
MODEL_PATH = 'model/model_config/autoencoder_model.h5'

look_back = 4

def prepare_data(values: np.ndarray, look_back: int = 4) -> np.ndarray:
    """
    Từ mảng 1D `values`, tạo các window size=look_back.
    Trả về X có shape = (n_samples, look_back), dtype float32.
    """
    X = [values[i : i + look_back] 
         for i in range(len(values) - look_back)]
    return np.array(X, dtype='float32')


def create_autoencoder(input_dim: int,
                       encoding_dim: int = 16,
                       seed: int = 42) -> Sequential:
    """
    Xây dựng AutoEncoder đơn giản:
      - Encoder: Dense(32) -> Dense(encoding_dim)
      - Decoder: Dense(32) -> Dense(input_dim)
    input_dim: số chiều của mỗi sample (ở đây là look_back)
    encoding_dim: kích thước không gian ẩn
    """
    initializer = tf.keras.initializers.GlorotUniform(seed=seed)

    model = Sequential(name="AutoEncoder")
    # Encoder
    model.add(Dense(32,
                    activation='relu',
                    kernel_initializer=initializer,
                    input_shape=(input_dim,),
                    name='encoder_dense1'))
    model.add(Dense(encoding_dim,
                    activation='relu',
                    kernel_initializer=initializer,
                    name='latent_space'))
    # Decoder
    model.add(Dense(32,
                    activation='relu',
                    kernel_initializer=initializer,
                    name='decoder_dense1'))
    model.add(Dense(input_dim,
                    activation='linear',
                    kernel_initializer=initializer,
                    name='reconstruction'))

    model.compile(optimizer='adam', loss='mse')
    return model

if os.path.exists(file_path):
    data = pd.read_csv(file_path)

    # Làm sạch dữ liệu
    data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
    data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]
    
    # Chuyển kiểu dữ liệu
    numeric_cols = ['LƯU LƯỢNG TỨC THỜI 1', 'ÁP LỰC 1', 'TỔNG LƯU LƯỢNG 1', 'Tiêu thụ']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # Xoá các dòng lỗi
    data.dropna(subset=['Ngày tháng'] + numeric_cols, inplace=True)

    # Lưu dữ liệu vào MongoDB
    data_records = []
    for _, row in data.iterrows():
        entry = {
            "watch_name": "Văn Đẩu 8",
            "timestamp": row['Ngày tháng'],
            "pressure": row['ÁP LỰC 1'],
            "total_flow": row['TỔNG LƯU LƯỢNG 1'],
            "consumption": row['Tiêu thụ'],
            "instant_flow": row['LƯU LƯỢNG TỨC THỜI 1'],
        }
        data_records.append(entry)
    
    if data_records:
        watch_result = db.watch_collection.insert_one({"data": data_records})
        watch_id = watch_result.inserted_id
    else:
        print("Không có dữ liệu hợp lệ để lưu trữ.")
        exit()

    # Lọc dữ liệu 1-4h sáng
    morning_data = data[
        data['Giờ'].str.contains(':') &
        data['Ngày tháng'].str.contains('SA') &
        data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
    ]
    morning_avg_list = []
    morning_dates = morning_data['Ngày'].unique().tolist()
    morning_values = morning_data['LƯU LƯỢNG TỨC THỜI 1'].tolist()
    for i in range(0, len(morning_values), 4):
        group = morning_values[i:i + 4]
        avg = np.mean(group) if group else 0
        morning_avg_list.append(avg)

    # Lọc dữ liệu 6-9h tối
    evening_data = data[
        data['Giờ'].str.contains(':') &
        data['Ngày tháng'].str.contains('CH') &
        data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
    ]
    evening_avg_list = []
    evening_dates = evening_data['Ngày'].unique().tolist()
    evening_values = evening_data['LƯU LƯỢNG TỨC THỜI 1'].tolist()
    for i in range(0, len(evening_values), 4):
        group = evening_values[i:i + 4]
        avg = np.mean(group) if group else 0
        evening_avg_list.append(avg)

    # --- CHO MIN (sáng) ---
    test_size_min = 100 if len(morning_avg_list) > 100 else int(len(morning_avg_list) * 0.2)
    train_data_min = morning_avg_list[:-test_size_min]
    test_data_min = morning_avg_list[-test_size_min:]
    test_dates_min = morning_dates[-test_size_min:]

    model_min = create_autoencoder(input_shape=(look_back, 1))
    predictions_min = []

    if len(train_data_min) >= look_back:
        X_train_min, y_train_min = prepare_data(train_data_min, look_back)
        model_min.fit(X_train_min, y_train_min, epochs=50, batch_size=32, verbose=1)

        # Dự đoán
        if len(test_data_min) >= look_back:
            X_test_min, _ = prepare_data(test_data_min, look_back)
            predictions_min = model_min.predict(X_test_min).flatten().tolist()

            # Lấy ngày dự đoán tương ứng (bỏ qua `look_back` ngày đầu)
            predicted_dates_min = test_dates_min[look_back:]
        else:
            predicted_dates_min = []
    else:
        predicted_dates_min = []


    # --- CHO MAX (tối) ---
    test_size_max = 100 if len(evening_avg_list) > 100 else int(len(evening_avg_list) * 0.2)
    train_data_max = evening_avg_list[:-test_size_max]
    test_data_max = evening_avg_list[-test_size_max:]

    model_max = create_autoencoder(input_shape=(look_back, 1))
    if len(train_data_max) >= look_back:
        X_train_max, y_train_max = prepare_data(train_data_max, look_back)
        model_max.fit(X_train_max, y_train_max, epochs=50, batch_size=32, verbose=1)

    # Dự đoán trên dữ liệu test cho min
    predictions_min = []
    if len(test_data_min) >= look_back:
        X_test_min, _ = prepare_data(test_data_min, look_back)
        predictions_min = model_min.predict(X_test_min).flatten().tolist()

    # Dự đoán trên dữ liệu test cho max
    predictions_max = []
    if len(test_data_max) >= look_back:
        X_test_max, _ = prepare_data(test_data_max, look_back)
        predictions_max = model_max.predict(X_test_max).flatten().tolist()

    # Lưu kết quả AutoEncoder vào MongoDB
    db.lstm_models.insert_one({
        "model_type": "AutoEncoder",
        "watch_id": watch_id,
        "avg_flow": [
            {
                "date_time": morning_dates[:len(morning_avg_list)],
                "min_avg": morning_avg_list,
                "max_avg": evening_avg_list[:len(evening_avg_list)],
            }
        ],
        "flow_AutoEncoder": [
            {
                "date_AutoEncoder": predicted_dates_min,
                "min_AutoEncoder": predictions_min,
                "max_AutoEncoder": predictions_max,
            }
        ],
    })

    # Isolation Forest anomaly detection
    min_flow_labels = [0] * len(morning_avg_list)
    max_flow_labels = [0] * len(evening_avg_list)

    if len(morning_avg_list) > 1:
        iso_min = IsolationForest(contamination=0.1, random_state=42)
        min_flow_labels = iso_min.fit_predict(np.array(morning_avg_list).reshape(-1, 1))
        min_flow_labels = [1 if x == -1 else 0 for x in min_flow_labels]

    if len(evening_avg_list) > 1:
        iso_max = IsolationForest(contamination=0.1, random_state=42)
        max_flow_labels = iso_max.fit_predict(np.array(evening_avg_list).reshape(-1, 1))
        max_flow_labels = [1 if x == -1 else 0 for x in max_flow_labels]

    db.isolation_models.insert_one({
        "model_type": "Isolation",
        "watch_id": watch_id,
        "avg_flow": [
            {
                "date_time": morning_dates[:len(morning_avg_list)],
                "min_avg": morning_avg_list,
                "max_avg": evening_avg_list[:len(evening_avg_list)],
            }
        ],
        "flow_iso": [
            {
                "date_Iso": morning_dates[:len(min_flow_labels)],
                "min_flow": min_flow_labels,
                "max_flow": max_flow_labels,
            }
        ],
    })

else:
    print(f"File {file_path} không tồn tại.")