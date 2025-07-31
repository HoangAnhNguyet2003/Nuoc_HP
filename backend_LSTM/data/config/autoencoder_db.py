from pymongo import MongoClient
import pandas as pd
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, RepeatVector
from tensorflow.keras.models import load_model

tf.config.run_functions_eagerly(True)

# ==== Kết nối MongoDB ====
client = MongoClient('mongodb://localhost:27017/')
db = client['HP_water']

# ==== Đường dẫn & cấu hình ====
file_path = '../raw_data/luu_luong/Văn_Đẩu8.csv'
AE_MODEL_PATH_MIN = '../../model/autoencoder/autoencoder_morning.h5'
AE_MODEL_PATH_MAX = '../../model/autoencoder/autoencoder_evening.h5'
look_back = 14

# ==== Hàm xử lý ====
def prepare_data(values, look_back):
    X, dates = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        dates.append(i + look_back)
    return np.array(X).reshape(-1, look_back, 1), np.array(dates)

def build_autoencoder(look_back):
    inputs = Input(shape=(look_back, 1))
    encoded = LSTM(64, activation="relu")(inputs)
    repeated = RepeatVector(look_back)(encoded)
    decoded = LSTM(64, activation="relu", return_sequences=True)(repeated)
    outputs = LSTM(1, return_sequences=True)(decoded)
    autoencoder = Model(inputs, outputs)
    autoencoder.compile(optimizer="adam", loss="mse")
    return autoencoder

# ==== Đọc dữ liệu ====
if os.path.exists(file_path):
    data = pd.read_csv(file_path)
    data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
    data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]

    numeric_cols = ['LƯU LƯỢNG TỨC THỜI 1', 'ÁP LỰC 1', 'TỔNG LƯU LƯỢNG 1', 'Tiêu thụ']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # === Lưu bản gốc vào Mongo ===
    records = []
    for _, row in data.iterrows():
        records.append({
            "watch_name": "Văn Đẩu 8",
            "timestamp": row['Ngày tháng'],
            "pressure": row['ÁP LỰC 1'],
            "total_flow": row['TỔNG LƯU LƯỢNG 1'],
            "consumption": row['Tiêu thụ'],
            "instant_flow": row['LƯU LƯỢNG TỨC THỜI 1']
        })
    watch_result = db.watch_collection.insert_one({"data": records})
    watch_id = watch_result.inserted_id

    # === Lọc dữ liệu sáng ===
    morning_data = data[
        data['Giờ'].str.contains(':') &
        data['Ngày tháng'].str.contains('SA') &
        data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
    ]
    morning_avg_list = []
    morning_dates = []
    for date, group in morning_data.groupby('Ngày', sort=False):
        values = group['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
        if len(values) == 4:
            morning_avg_list.append(np.mean(values))
            morning_dates.append(date)

    # === Lọc dữ liệu tối ===
    evening_data = data[
        data['Giờ'].str.contains(':') &
        data['Ngày tháng'].str.contains('CH') &
        data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
    ]
    evening_avg_list = []
    evening_dates = []
    for date, group in evening_data.groupby('Ngày', sort=False):
        values = group['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
        if len(values) == 4:
            evening_avg_list.append(np.mean(values))
            evening_dates.append(date)

    # === Xử lý Autoencoder (sáng) ===
    morning_X, morning_idx = prepare_data(np.array(morning_avg_list), look_back)
    morning_date_aligned = np.array(morning_dates)[morning_idx]
    ae_min = build_autoencoder(look_back)
    ae_min.fit(morning_X, morning_X, epochs=100, batch_size=16, verbose=1)
    ae_min.save(AE_MODEL_PATH_MIN)

    reconstructed_min = ae_min.predict(morning_X)
    recon_loss_min = np.mean((morning_X - reconstructed_min)**2, axis=(1, 2))

    # === Xử lý Autoencoder (tối) ===
    evening_X, evening_idx = prepare_data(np.array(evening_avg_list), look_back)
    evening_date_aligned = np.array(evening_dates)[evening_idx]
    ae_max = build_autoencoder(look_back)
    ae_max.fit(evening_X, evening_X, epochs=100, batch_size=16, verbose=1)
    ae_max.save(AE_MODEL_PATH_MAX)

    reconstructed_max = ae_max.predict(evening_X)
    recon_loss_max = np.mean((evening_X - reconstructed_max)**2, axis=(1, 2))

    # === Lưu kết quả vào Mongo ===
    db.autoencoder_models.insert_one({
        "model_type": "Autoencoder",
        "watch_id": watch_id,
        "avg_flow": [
            {
                "date_time": morning_dates,
                "min_avg": morning_avg_list,
                "max_avg": evening_avg_list
            }
        ],
        "flow_AE": [
            {
                "date_AE_min": morning_date_aligned.tolist(),
                "min_recon_loss": recon_loss_min.tolist(),
                "date_AE_max": evening_date_aligned.tolist(),
                "max_recon_loss": recon_loss_max.tolist()
            }
        ]
    })
    print("✅ Lưu Autoencoder và kết quả xong.")
else:
    print(f"❌ Không tìm thấy file {file_path}")
