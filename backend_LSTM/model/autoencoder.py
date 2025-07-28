import os
import numpy as np
import pandas as pd
import random
import tensorflow as tf
from datetime import timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense, Input, RepeatVector
from tensorflow.keras.models import load_model

# ========== CẤU HÌNH ==========
np.random.seed(42)
tf.random.set_seed(42)
folder_path = '../data/raw_data/luu_luong_clean/'
MODEL_PATH_MORNING = '../model/lstm/lstm_model_morning.h5'
MODEL_PATH_EVENING = '../model/lstm/lstm_model_evening.h5'
AE_PATH_MORNING = '../model/autoecoder/autoencoder_model_morning.h5'
AE_PATH_EVENING = '../model/autoecoder/autoencoder_model_evening.h5'
RESULT_PATH_MORNING = '../model/autoecoder/results_morning.csv'
RESULT_PATH_EVENING = '../model/autoecoder/results_evening.csv'
look_back = 14

# ========== HÀM TIỆN ÍCH ==========
def prepare_data(values, look_back):
    X, y, dates = [], [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
        dates.append(i + look_back)
    return np.array(X).reshape(-1, look_back, 1), np.array(y), np.array(dates)


def build_denoising_autoencoder(look_back):
    inputs = Input(shape=(look_back, 1))
    encoded = LSTM(64, activation="relu")(inputs)
    repeated = RepeatVector(look_back)(encoded)
    decoded = LSTM(64, activation="relu", return_sequences=True)(repeated)
    outputs = LSTM(1, return_sequences=True)(decoded)
    autoencoder = Model(inputs, outputs)
    autoencoder.compile(optimizer="adam", loss="mse")
    return autoencoder

def train_with_autoencoder_and_lstm(X_real, y_real, date_list, model_path, ae_path, result_path):
    print(" Huấn luyện Autoencoder...")
    autoencoder = build_denoising_autoencoder(look_back)
    autoencoder.fit(X_real, X_real, epochs=100, batch_size=16, verbose=1)
    autoencoder.save(ae_path)
    print(f" Mô hình Autoencoder đã lưu vào: {ae_path}")

    print(" Sinh dữ liệu synthetic từ Autoencoder...")
    noise = np.random.normal(0, 0.05, X_real.shape)
    X_noisy = X_real + noise
    X_synthetic = autoencoder.predict(X_noisy)
    y_synthetic = y_real.copy()[:len(X_synthetic)]

    print(" Đã sinh xong dữ liệu synthetic")

    # Huấn luyện lại LSTM
    model = Sequential()
    model.add(LSTM(100, activation='tanh', return_sequences=True, input_shape=(look_back, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(100, activation='tanh'))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    X_train = np.concatenate([X_real, X_synthetic])
    y_train = np.concatenate([y_real, y_synthetic])

    print(" Huấn luyện lại LSTM...")
    model.fit(X_train, y_train, epochs=150, batch_size=64, verbose=1)
    model.save(model_path)
    print(f" Mô hình đã lưu vào: {model_path}")

    # Dự đoán và lưu kết quả
    predictions = model.predict(X_real).flatten()
    mae = mean_absolute_error(y_real, predictions)
    mse = mean_squared_error(y_real, predictions)
    r2 = r2_score(y_real, predictions)

    print("\n Kết quả dự đoán:")
    for i in range(len(y_real)):
        print(f"  Ngày: {date_list[i]}, Thật: {y_real[i]:.2f}, Dự đoán: {predictions[i]:.2f}")


    print("\n Metrics:")
    print(f"  MAE   = {mae:.4f}")
    print(f"  MSE   = {mse:.4f}")
    print(f"  R²    = {r2:.4f}")

    pd.DataFrame({
        'Ngày': date_list,
        'True': y_real,
        'Predicted': predictions
    }).to_csv(result_path, index=False)
    print(f" Đã lưu kết quả vào: {result_path}")

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

# ========== HUẤN LUYỆN ==========
morning_X, morning_y, morning_d = prepare_data(np.array(morning_values), look_back)
evening_X, evening_y, evening_d = prepare_data(np.array(evening_values), look_back)
morning_date_list = np.array(morning_dates)[morning_d]
evening_date_list = np.array(evening_dates)[evening_d]

if __name__ == "__main__":
    print("=====  Đào tạo mô hình sáng =====")
    train_with_autoencoder_and_lstm(morning_X, morning_y, morning_date_list, MODEL_PATH_MORNING, AE_PATH_MORNING, RESULT_PATH_MORNING)

    print("\n===== Đào tạo mô hình tối =====")
    train_with_autoencoder_and_lstm(evening_X, evening_y, evening_date_list, MODEL_PATH_EVENING, AE_PATH_EVENING, RESULT_PATH_EVENING)
