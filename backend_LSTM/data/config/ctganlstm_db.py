import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from sdv.single_table import CTGANSynthesizer
import joblib
import tensorflow as tf

tf.config.run_functions_eagerly(True)

# ==== Kết nối MongoDB ====
client = MongoClient('mongodb://localhost:27017/')
db = client['HP_water']

# ==== Đường dẫn ====
file_path = '../raw_data/luu_luong/Văn_Đẩu8.csv'
look_back = 14

MODEL_PATH_MIN = '../../model/lstm/lstm_model_morning.h5'
MODEL_PATH_MAX = '../../model/lstm/lstm_model_evening.h5'
CTGAN_PATH_MIN = '../../model/ctgan/pretrainctgan_morning.pkl'
CTGAN_PATH_MAX = '../../model/ctgan/pretrainctgan_evening.pkl'

# ==== Hàm xử lý ====
def prepare_data(values, look_back):
    X, y = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
    return np.array(X).reshape(-1, look_back, 1), np.array(y)

def load_ctgan(path, label):
    if os.path.exists(path):
        print(f"📥 Load CTGAN {label}: {path}")
        return joblib.load(path)
    else:
        print(f"❌ Không tìm thấy CTGAN {label} ({path})")
        return None

# ==== Xử lý chính ====
if os.path.exists(file_path):
    data = pd.read_csv(file_path)
    data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
    data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]
    data['LƯU LƯỢNG TỨC THỜI 1'] = pd.to_numeric(data['LƯU LƯỢNG TỨC THỜI 1'], errors='coerce')

    # Lưu dữ liệu gốc vào MongoDB
    records = [{
        "watch_name": "Văn Đẩu 8",
        "timestamp": row['Ngày tháng'],
        "instant_flow": row['LƯU LƯỢNG TỨC THỜI 1'],
    } for _, row in data.iterrows()]
    watch_result = db.watch_collection.insert_one({"data": records})
    watch_id = watch_result.inserted_id

    # ==== Lọc sáng ====
    morning_data = data[
        data['Giờ'].str.contains(':') &
        data['Ngày tháng'].str.contains('SA') &
        data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
    ]
    morning_avg_list, morning_dates = [], []
    for date, group in morning_data.groupby('Ngày', sort=False):
        values = group['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
        if len(values) == 4:
            morning_avg_list.append(np.mean(values))
            morning_dates.append(date)

    # ==== Lọc tối ====
    evening_data = data[
        data['Giờ'].str.contains(':') &
        data['Ngày tháng'].str.contains('CH') &
        data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
    ]
    evening_avg_list, evening_dates = [], []
    for date, group in evening_data.groupby('Ngày', sort=False):
        values = group['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
        if len(values) == 4:
            evening_avg_list.append(np.mean(values))
            evening_dates.append(date)

    # ==== Load CTGAN và sinh dữ liệu ====
    ctgan_min = load_ctgan(CTGAN_PATH_MIN, "sáng")
    ctgan_max = load_ctgan(CTGAN_PATH_MAX, "tối")

    synthetic_avg_min = ctgan_min.sample(len(morning_avg_list))['label'].values if ctgan_min else []
    synthetic_avg_max = ctgan_max.sample(len(evening_avg_list))['label'].values if ctgan_max else []

    # ==== Huấn luyện & dự đoán LSTM sáng ====
    morning_X, morning_y = prepare_data(np.array(morning_avg_list), look_back)
    synthetic_X_min, synthetic_y_min = prepare_data(synthetic_avg_min, look_back) if len(synthetic_avg_min) >= look_back else (np.empty((0, look_back, 1)), np.empty((0,)))

    X_train_min = np.concatenate([morning_X, synthetic_X_min])
    y_train_min = np.concatenate([morning_y, synthetic_y_min])

    model_min = load_model(MODEL_PATH_MIN, compile=False)
    model_min.compile(optimizer='adam', loss='mse')
    model_min.fit(X_train_min, y_train_min, epochs=100, batch_size=16, verbose=1)

    test_data_min = morning_avg_list[300:]
    test_dates_min = morning_dates[300:]
    if len(test_data_min) >= look_back:
        X_test_min, _ = prepare_data(np.array(test_data_min), look_back)
        min_preds = model_min.predict(X_test_min).flatten().tolist()
        min_pred_dates = test_dates_min[look_back:]
    else:
        min_preds = []
        min_pred_dates = []

    # ==== Huấn luyện & dự đoán LSTM tối ====
    evening_X, evening_y = prepare_data(np.array(evening_avg_list), look_back)
    synthetic_X_max, synthetic_y_max = prepare_data(synthetic_avg_max, look_back) if len(synthetic_avg_max) >= look_back else (np.empty((0, look_back, 1)), np.empty((0,)))

    X_train_max = np.concatenate([evening_X, synthetic_X_max])
    y_train_max = np.concatenate([evening_y, synthetic_y_max])

    model_max = load_model(MODEL_PATH_MAX, compile=False)
    model_max.compile(optimizer='adam', loss='mse')
    model_max.fit(X_train_max, y_train_max, epochs=100, batch_size=16, verbose=1)

    test_data_max = evening_avg_list[300:]
    test_dates_max = evening_dates[300:]
    if len(test_data_max) >= look_back:
        X_test_max, _ = prepare_data(np.array(test_data_max), look_back)
        max_preds = model_max.predict(X_test_max).flatten().tolist()
        max_pred_dates = test_dates_max[look_back:]
    else:
        max_preds = []
        max_pred_dates = []

    # ==== Lưu vào MongoDB ====
    db.ctgan_lstm_models.insert_one({
        "model_type": "CTGAN+LSTM (Pretrained)",
        "watch_id": watch_id,
        "avg_flow": [{
            "date_time": morning_dates,
            "min_avg": morning_avg_list,
            "max_avg": evening_avg_list
        }],
        "flow_CTGAN_LSTM": [{
            "date_LSTM": min_pred_dates,
            "min_LSTM": min_preds,
            "max_LSTM": max_preds
        }]
    })

    print("✅ Đã huấn luyện với CTGAN preload + LSTM và lưu kết quả.")
else:
    print(f"❌ File không tồn tại: {file_path}")
