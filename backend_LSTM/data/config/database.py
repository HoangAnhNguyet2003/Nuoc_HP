from pymongo import MongoClient
import pandas as pd
import numpy as np
import os
from tensorflow.keras.models import load_model
import tensorflow as tf

# Bật eager execution
tf.config.run_functions_eagerly(True)

# Kết nối tới MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['HP_water']
file_path = '../raw_data/luu_luong/Văn_Đẩu8.csv'
MODEL_PATH_MIN = '../../model/lstm/lstm_model_morning.h5'
MODEL_PATH_MAX = '../../model/lstm/lstm_model_evening.h5'

look_back = 14

def prepare_data(values, look_back):
    X, y = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
    return np.array(X).reshape(-1, look_back, 1), np.array(y)

if os.path.exists(file_path):
    data = pd.read_csv(file_path)

    # Làm sạch dữ liệu
    data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
    data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]
    
    # Chuyển kiểu dữ liệu
    numeric_cols = ['LƯU LƯỢNG TỨC THỜI 1', 'ÁP LỰC 1', 'TỔNG LƯU LƯỢNG 1', 'Tiêu thụ']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

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


    # === DỮ LIỆU SÁNG (1-4h SA) ===
    morning_data = data[
        data['Giờ'].str.contains(':') &
        data['Ngày tháng'].str.contains('SA') &
        data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
    ]

    morning_avg_list = []
    morning_dates = []

    grouped_morning = morning_data.groupby('Ngày', sort=False)

    print("===== 10 ngày đầu tiên có đủ 4 giá trị 1-4h sáng (SA) =====")
    count_morning = 0
    for date, group in grouped_morning:
        values = group['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
        if len(values) == 4:
            avg = np.mean(values)
            morning_avg_list.append(avg)
            morning_dates.append(date)


    # === DỮ LIỆU TỐI (6-9h CH) ===
    evening_data = data[
        data['Giờ'].str.contains(':') &
        data['Ngày tháng'].str.contains('CH') &
        data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
    ]

    evening_avg_list = []
    evening_dates = []

    grouped_evening = evening_data.groupby('Ngày', sort=False)

    print("===== 10 ngày đầu tiên có đủ 4 giá trị 6-9h tối (CH) =====")
    count_evening = 0
    for date, group in grouped_evening:
        values = group['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
        if len(values) == 4:
            avg = np.mean(values)
            evening_avg_list.append(avg)
            evening_dates.append(date)

    # === CHIA DỮ LIỆU TRAIN/TEST ===
    train_data_min = morning_avg_list[:300]
    test_data_min = morning_avg_list[300:]
    test_dates_min = morning_dates[300:]  # giữ đúng thứ tự gốc

    train_data_max = evening_avg_list[:300]
    test_data_max = evening_avg_list[300:]
    test_dates_max = evening_dates[300:]

    # === LOAD MODEL & TRAIN ===
    model_min = load_model(MODEL_PATH_MIN, compile=False)
    model_min.compile(optimizer='adam', loss='mean_squared_error')
    model_max = load_model(MODEL_PATH_MAX, compile=False)
    model_max.compile(optimizer='adam', loss='mean_squared_error')

    predictions_min, predictions_max = [], []
    predicted_dates_min, predicted_dates_max = [], []

    # ==== DỰ ĐOÁN SÁNG ====
    if len(train_data_min) >= look_back:
        X_train_min, y_train_min = prepare_data(train_data_min, look_back)
        model_min.fit(X_train_min, y_train_min, epochs=100, batch_size=16, verbose=1)

        if len(test_data_min) >= look_back:
            X_test_min, _ = prepare_data(test_data_min, look_back)
            predictions_min = model_min.predict(X_test_min).flatten().tolist()
            predicted_dates_min = test_dates_min[look_back:]

    # ==== DỰ ĐOÁN TỐI ====
    if len(train_data_max) >= look_back:
        X_train_max, y_train_max = prepare_data(train_data_max, look_back)
        model_max.fit(X_train_max, y_train_max, epochs=100, batch_size=16, verbose=1)

        if len(test_data_max) >= look_back:
            X_test_max, _ = prepare_data(test_data_max, look_back)
            predictions_max = model_max.predict(X_test_max).flatten().tolist()
            predicted_dates_max = test_dates_max[look_back:]

    # === LƯU KẾT QUẢ VÀO MONGO ===
    db.lstm_models.insert_one({
        "model_type": "LSTM",
        "watch_id": watch_id,
        "avg_flow": [
            {
                "date_time": morning_dates,
                "min_avg": morning_avg_list,
                "max_avg": evening_avg_list,
            }
        ],
        "flow_LSTM": [
            {
                "date_LSTM": predicted_dates_min,
                "min_LSTM": predictions_min,
                "max_LSTM": predictions_max,
            }
        ],
    })
else:
    print(f"File {file_path} không tồn tại.")
# import numpy as np
# from pymongo import MongoClient
# import pandas as pd
# import os
# from tensorflow.keras.models import load_model
# from sklearn.preprocessing import MinMaxScaler
# import tensorflow as tf
# from tensorflow.keras.layers import Layer

# # ✅ Khai báo lớp Sampling nếu dùng trong encoder
# class Sampling(Layer):
#     def call(self, inputs):
#         z_mean, z_log_var = inputs
#         epsilon = tf.random.normal(shape=tf.shape(z_mean))
#         return z_mean + tf.exp(0.5 * z_log_var) * epsilon

# # ✅ Kết nối MongoDB
# client = MongoClient("mongodb://localhost:27017/")
# db = client['HP_water']
# collection = db['vae_models']

# # ✅ File dữ liệu và tham số
# file_path = '../raw_data/luu_luong/Văn_Đẩu8.csv'
# look_back = 4

# # ✅ Load encoder & decoder (khai báo custom_objects cho Sampling)
# encoder_morning = load_model("../../model/model_config/vae/encoder_morning.h5", compile=False, custom_objects={"Sampling": Sampling})
# decoder_morning = load_model("../../model/model_config/vae/decoder_morning.h5", compile=False)
# encoder_evening = load_model("../../model/model_config/vae/encoder_evening.h5", compile=False, custom_objects={"Sampling": Sampling})
# decoder_evening = load_model("../../model/model_config/vae/decoder_evening.h5", compile=False)

# # ✅ Hàm chuẩn bị dữ liệu cho VAE
# def prepare_data(values, look_back):
#     X, y = [], []
#     for i in range(len(values) - look_back):
#         X.append(values[i:i + look_back])
#         y.append(values[i + look_back])
#     return np.array(X).reshape(-1, look_back, 1), np.array(y)

# # ✅ Đọc và xử lý file CSV
# if os.path.exists(file_path):
#     data = pd.read_csv(file_path)
#     data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
#     data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]

#     numeric_cols = ['LƯU LƯỢNG TỨC THỜI 1', 'ÁP LỰC 1', 'TỔNG LƯU LƯỢNG 1', 'Tiêu thụ']
#     for col in numeric_cols:
#         data[col] = pd.to_numeric(data[col], errors='coerce')

#     data.dropna(subset=['Ngày tháng'] + numeric_cols, inplace=True)

#     # ✅ Lưu dữ liệu gốc vào MongoDB
#     data_records = [{
#         "watch_name": "Văn Đẩu 8",
#         "timestamp": row['Ngày tháng'],
#         "pressure": row['ÁP LỰC 1'],
#         "total_flow": row['TỔNG LƯU LƯỢNG 1'],
#         "consumption": row['Tiêu thụ'],
#         "instant_flow": row['LƯU LƯỢNG TỨC THỜI 1']
#     } for _, row in data.iterrows()]

#     watch_result = db.watch_collection.insert_one({"data": data_records})
#     watch_id = watch_result.inserted_id

#     # ✅ Xử lý dữ liệu sáng (1–4h SA)
#     morning_data = data[
#         data['Giờ'].str.contains(':') &
#         data['Ngày tháng'].str.contains('SA') &
#         data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
#     ]
#     morning_dates = morning_data['Ngày'].unique().tolist()
#     morning_values = morning_data['LƯU LƯỢNG TỨC THỜI 1'].tolist()
#     morning_avg_list = [np.mean(morning_values[i:i + 4]) for i in range(0, len(morning_values), 4)]

#     # ✅ Xử lý dữ liệu tối (6–9h CH)
#     evening_data = data[
#         data['Giờ'].str.contains(':') &
#         data['Ngày tháng'].str.contains('CH') &
#         data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
#     ]
#     evening_dates = evening_data['Ngày'].unique().tolist()
#     evening_values = evening_data['LƯU LƯỢNG TỨC THỜI 1'].tolist()
#     evening_avg_list = [np.mean(evening_values[i:i + 4]) for i in range(0, len(evening_values), 4)]

#     # ✅ Chuẩn hóa và chia tập train/test
#     morning_X, morning_y = prepare_data(morning_avg_list, look_back)
#     evening_X, evening_y = prepare_data(evening_avg_list, look_back)

#     morning_X_scaled = morning_X  # Không scale
#     evening_X_scaled = evening_X  # Không scale


#     # Train từ 100 mẫu đầu, test trên phần còn lại
#     morning_X_train, morning_y_train = morning_X_scaled[:100], morning_y[:100]
#     morning_X_test, morning_y_test = morning_X_scaled[100:], morning_y[100:]
#     morning_test_dates = morning_dates[look_back + 100:]

#     evening_X_train, evening_y_train = evening_X_scaled[:100], evening_y[:100]
#     evening_X_test, evening_y_test = evening_X_scaled[100:], evening_y[100:]
#     evening_test_dates = evening_dates[look_back + 100:]

#     # ✅ Lấy latent vector từ encoder
#     z_morning = encoder_morning.predict(morning_X_test)
#     z_evening = encoder_evening.predict(evening_X_test)

#     z_morning = z_morning[2] if isinstance(z_morning, (list, tuple)) else z_morning
#     z_evening = z_evening[2] if isinstance(z_evening, (list, tuple)) else z_evening

#     # ✅ Sinh 1 giá trị dự đoán từ decoder (chọn giá trị cuối cùng)
#     vae_morning_generated = decoder_morning.predict(z_morning)[:, -1, 0].tolist()
#     vae_evening_generated = decoder_evening.predict(z_evening)[:, -1, 0].tolist()

#     # ✅ Lưu kết quả sinh vào MongoDB
#     db.vae_models.insert_one({
#         "model_type": "VAE",
#         "watch_id": watch_id,
#         "avg_flow": [
#             {
#                 "date_time": morning_dates[:len(morning_avg_list)],
#                 "min_avg": morning_avg_list,
#                 "max_avg": evening_avg_list[:len(evening_avg_list)],
#             }
#         ],
#         "flow_VAE": [
#             {
#                 "date_VAE": morning_test_dates[:len(vae_morning_generated)],
#                 "min_VAE": vae_morning_generated,
#                 "max_VAE": vae_evening_generated,
#             }
#         ],
#     })

#     print("✅ Dữ liệu VAE đã được sinh và lưu vào MongoDB")

# else:
#     print(f"❌ File {file_path} không tồn tại.")
