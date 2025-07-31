import os
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import timedelta
from tensorflow.keras.models import Model
from tensorflow.keras.layers import LSTM, Input, RepeatVector
from tensorflow.keras.callbacks import EarlyStopping

# ========== CẤU HÌNH ==========
np.random.seed(42)
tf.random.set_seed(42)

folder_path = '../data/raw_data/luu_luong_clean/'

AE_PATH_MORNING = '../model/autoecoder/autoencoder_model_morning.h5'
AE_PATH_EVENING = '../model/autoecoder/autoencoder_model_evening.h5'
RESULT_PATH_MORNING = '../model/autoecoder/results_morning.csv'
RESULT_PATH_EVENING = '../model/autoecoder/results_evening.csv'
look_back = 14

# ========== HÀM TIỆN ÍCH ==========
def prepare_data(values, look_back):
    X, dates = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        dates.append(i + look_back)
    return np.array(X).reshape(-1, look_back, 1), np.array(dates)


def build_denoising_autoencoder(look_back):
    inputs = Input(shape=(look_back, 1))
    encoded = LSTM(64, activation="relu")(inputs)
    repeated = RepeatVector(look_back)(encoded)
    decoded = LSTM(64, activation="relu", return_sequences=True)(repeated)
    outputs = LSTM(1, return_sequences=True)(decoded)
    autoencoder = Model(inputs, outputs)
    autoencoder.compile(optimizer="adam", loss="mse")
    return autoencoder


def train_autoencoder_only(X_real, date_list, ae_path, result_path):
    print("🔧 Huấn luyện Autoencoder...")
    autoencoder = build_denoising_autoencoder(look_back)
    history = autoencoder.fit(
        X_real, X_real,
        epochs=200,
        batch_size=64,
        verbose=1,
        validation_split=0.1,
        callbacks=[EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)]
    )
    autoencoder.save(ae_path)
    print(f"✅ Mô hình Autoencoder đã lưu vào: {ae_path}")

    print("🧪 Dự đoán đầu ra tái tạo...")
    reconstructed = autoencoder.predict(X_real)

    print("📊 Tính reconstruction loss...")
    mse_per_sample = np.mean((X_real - reconstructed) ** 2, axis=(1, 2))

    pd.DataFrame({
        'Ngày': date_list,
        'Reconstruction_Loss': mse_per_sample
    }).to_csv(result_path, index=False)
    print(f"📁 Đã lưu kết quả loss từng ngày vào: {result_path}")

# ========== TIỀN XỬ LÝ DỮ LIỆU ==========
morning_values = []
evening_values = []
morning_dates = []
evening_dates = []

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        data = pd.read_csv(file_path)

        data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
        data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]

        for col in ['LƯU LƯỢNG TỨC THỜI 1', 'ÁP LỰC 1', 'TỔNG LƯU LƯỢNG 1', 'Tiêu thụ']:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        morning_data = data[
            data['Giờ'].str.contains(':') &
            data['Ngày tháng'].str.contains('SA') &
            data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
        ]

        evening_data = data[
            data['Giờ'].str.contains(':') &
            data['Ngày tháng'].str.contains('CH') &
            data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
        ]

        for date in morning_data['Ngày'].unique():
            daily_values = morning_data[morning_data['Ngày'] == date]['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
            if len(daily_values) >= 1:
                avg = np.mean(daily_values[:4])
                morning_values.append(avg)
                morning_dates.append(date)

        for date in evening_data['Ngày'].unique():
            daily_values = evening_data[evening_data['Ngày'] == date]['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
            if len(daily_values) >= 1:
                avg = np.mean(daily_values[:4])
                evening_values.append(avg)
                evening_dates.append(date)

# ========== CHUẨN BỊ DỮ LIỆU ==========
morning_X, morning_d = prepare_data(np.array(morning_values), look_back)
evening_X, evening_d = prepare_data(np.array(evening_values), look_back)
morning_date_list = np.array(morning_dates)[morning_d]
evening_date_list = np.array(evening_dates)[evening_d]

# ========== HUẤN LUYỆN AUTOENCODER ==========
if __name__ == "__main__":
    print("=====  Đào tạo Autoencoder sáng =====")
    train_autoencoder_only(morning_X, morning_date_list, AE_PATH_MORNING, RESULT_PATH_MORNING)

    print("\n===== Đào tạo Autoencoder tối =====")
    train_autoencoder_only(evening_X, evening_date_list, AE_PATH_EVENING, RESULT_PATH_EVENING)
