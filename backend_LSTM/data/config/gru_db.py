import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
import tensorflow as tf
from tensorflow.keras.models import load_model

# === Cấu hình TensorFlow ===
tf.config.run_functions_eagerly(True)

# ==== Kết nối MongoDB ====
client = MongoClient('mongodb://localhost:27017/')
db = client['HP_water']

# ==== Đường dẫn và thông số ====
file_path = '../raw_data/luu_luong/Văn_Đẩu8.csv'
look_back = 14
MODEL_PATH_MIN = '../../model/lstm/gru_model_morning.h5'
MODEL_PATH_MAX = '../../model/lstm/gru_model_evening.h5'

# ==== Hàm xử lý dữ liệu ====
def prepare_data(values, look_back):
    X, y = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
    return np.array(X).reshape(-1, look_back, 1), np.array(y)

# ==== Bắt đầu xử lý ====
if os.path.exists(file_path):
    data = pd.read_csv(file_path)
    data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
    data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]
    data['LƯU LƯỢNG TỨC THỜI 1'] = pd.to_numeric(data['LƯU LƯỢNG TỨC THỜI 1'], errors='coerce')

    # ==== Lưu dữ liệu gốc vào MongoDB ====
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

    # ==== Load model GRU đã huấn luyện ====
    model_min = load_model(MODEL_PATH_MIN, compile=False)
    model_min.compile(optimizer='adam', loss='mean_squared_error')

    model_max = load_model(MODEL_PATH_MAX, compile=False)
    model_max.compile(optimizer='adam', loss='mean_squared_error')

    # ==== Dự đoán sáng ====
    test_data_min = morning_avg_list[300:]
    test_dates_min = morning_dates[300:]
    if len(test_data_min) >= look_back:
        X_test_min, _ = prepare_data(np.array(test_data_min), look_back)
        min_preds = model_min.predict(X_test_min).flatten().tolist()
        min_pred_dates = test_dates_min[look_back:]
    else:
        min_preds = []
        min_pred_dates = []

    # ==== Dự đoán tối ====
    test_data_max = evening_avg_list[300:]
    test_dates_max = evening_dates[300:]
    if len(test_data_max) >= look_back:
        X_test_max, _ = prepare_data(np.array(test_data_max), look_back)
        max_preds = model_max.predict(X_test_max).flatten().tolist()
        max_pred_dates = test_dates_max[look_back:]
    else:
        max_preds = []
        max_pred_dates = []

    # ==== Lưu kết quả vào MongoDB ====
    db.gru_models.insert_one({
        "model_type": "GRU (Real Data Only)",
        "watch_id": watch_id,
        "avg_flow": [{
            "date_time": morning_dates,
            "min_avg": morning_avg_list,
            "max_avg": evening_avg_list
        }],
        "flow_GRU": [{
            "date_GRU": min_pred_dates,
            "min_GRU": min_preds,
            "max_GRU": max_preds
        }]
    })

    print("✅ Đã load mô hình GRU pretrained và lưu kết quả dự đoán.")
else:
    print(f"❌ Không tìm thấy file: {file_path}")
