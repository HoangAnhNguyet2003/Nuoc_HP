import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
from tensorflow.keras.models import load_model
from datetime import datetime
from bson import ObjectId
import tensorflow as tf

# Bật eager execution
tf.config.run_functions_eagerly(True)

# ==== Cấu hình ====
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "HP_water"
COLLECTION_NAME = "predict_ai"

MODEL_PATH_MIN = "../../model/lstm/lstm_model_morning.h5"
MODEL_PATH_MAX = "../../model/lstm/lstm_model_evening.h5"
FILE_PATH = "../raw_data/luu_luong/Văn_Đẩu8.csv"

# ⚠️ ID đồng hồ tương ứng với bảng `watch_device` (ObjectId dạng string)
WATCH_ID = 1
LOOK_BACK = 14


def prepare_data(values, look_back):
    X, y = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
    return np.array(X).reshape(-1, look_back, 1), np.array(y)


# ==== Kết nối MongoDB ====
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ==== Đọc dữ liệu ====
if not os.path.exists(FILE_PATH):
    print(f"❌ Không tìm thấy file: {FILE_PATH}")
    exit()

data = pd.read_csv(FILE_PATH)
data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]

# Làm sạch dữ liệu
numeric_cols = ['LƯU LƯỢNG TỨC THỜI 1', 'ÁP LỰC 1', 'TỔNG LƯU LƯỢNG 1', 'Tiêu thụ']
for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors='coerce')

# ==== DỮ LIỆU SÁNG (1–4h SA) ====
morning_data = data[
    data['Giờ'].str.contains(':') &
    data['Ngày tháng'].str.contains('SA') &
    data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
]

grouped_morning = morning_data.groupby('Ngày')
morning_dates, morning_avg_list = [], []
for date, group in grouped_morning:
    values = group['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
    if len(values) == 4:
        morning_dates.append(date)
        morning_avg_list.append(np.mean(values))

# ==== DỮ LIỆU TỐI (6–9h CH) ====
evening_data = data[
    data['Giờ'].str.contains(':') &
    data['Ngày tháng'].str.contains('CH') &
    data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
]

grouped_evening = evening_data.groupby('Ngày')
evening_dates, evening_avg_list = [], []
for date, group in grouped_evening:
    values = group['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
    if len(values) == 4:
        evening_dates.append(date)
        evening_avg_list.append(np.mean(values))

# ==== LOAD MODEL ====
model_min = load_model(MODEL_PATH_MIN, compile=False)
model_min.compile(optimizer='adam', loss='mean_squared_error')

model_max = load_model(MODEL_PATH_MAX, compile=False)
model_max.compile(optimizer='adam', loss='mean_squared_error')

# ==== DỰ ĐOÁN SÁNG ====
min_preds, min_pred_dates = [], []
if len(morning_avg_list) >= LOOK_BACK:
    X_morning, _ = prepare_data(morning_avg_list, LOOK_BACK)
    min_preds = model_min.predict(X_morning).flatten().tolist()
    min_pred_dates = morning_dates[LOOK_BACK:]

# ==== DỰ ĐOÁN TỐI ====
max_preds, max_pred_dates = [], []
if len(evening_avg_list) >= LOOK_BACK:
    X_evening, _ = prepare_data(evening_avg_list, LOOK_BACK)
    max_preds = model_max.predict(X_evening).flatten().tolist()
    max_pred_dates = evening_dates[LOOK_BACK:]

# ==== GHI VÀO MONGODB: bảng predict_ai ====
for i in range(min(len(min_pred_dates), len(max_pred_dates))):
    try:
        doc = {
            "name_model": "LSTM",
            "date": datetime.strptime(min_pred_dates[i], "%d/%m/%Y"),
            "min_avg": round(morning_avg_list[i + LOOK_BACK], 3),
            "max_avg": round(evening_avg_list[i + LOOK_BACK], 3),
            "min_pred": round(min_preds[i], 3),
            "max_pred": round(max_preds[i], 3),
            "Watch_id": WATCH_ID
        }
        collection.insert_one(doc)
    except Exception as e:
        print(f"❌ Lỗi khi lưu ngày {min_pred_dates[i]}: {e}")

print("✅ Dự đoán và lưu dữ liệu thành công vào bảng predict_ai.")
