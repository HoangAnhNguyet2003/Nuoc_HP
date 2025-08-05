import os
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dropout, Dense

# ========== CẤU HÌNH ==========
np.random.seed(42)
tf.random.set_seed(42)
folder_path = '../data/raw_data/luu_luong_clean/'
MODEL_PATH_MORNING = '../lstm/gru_model_morning_real.h5'
MODEL_PATH_EVENING = '../lstm/gru_model_evening_real.h5'
look_back = 14

# ========== HÀM XỬ LÝ ==========
def prepare_data(values, look_back):
    X, y, dates = [], [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
        dates.append(i + look_back)
    return np.array(X).reshape(-1, look_back, 1), np.array(y), np.array(dates)

def train_with_gru_only(values, date_list, model_path):
    X, y, _ = prepare_data(values, look_back)

    print("🤖 Huấn luyện GRU với dữ liệu thực...")
    model = Sequential()
    model.add(GRU(100,  activation='tanh', return_sequences=True, input_shape=(look_back, 1)))
    model.add(Dropout(0.3))
    model.add(GRU(100, activation='tanh'))
    model.add(Dropout(0.3))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    model.fit(X, y, epochs=150, batch_size=64, verbose=1)
    model.save(model_path)
    print(f"✅ Mô hình GRU đã lưu vào: {model_path}")

    predictions = model.predict(X).flatten()
    mae = mean_absolute_error(y, predictions)
    mse = mean_squared_error(y, predictions)
    r2 = r2_score(y, predictions)

    print("\n🎯 Kết quả dự đoán:")
    for i in range(min(10, len(y))):
        print(f"  Ngày: {date_list[i]}, Thật: {y[i]:.2f}, Dự đoán: {predictions[i]:.2f}")

    print("\n📊 Metrics:")
    print(f" 🔸 MAE   = {mae:.4f}")
    print(f" 🔸 MSE   = {mse:.4f}")
    print(f" 🔸 R²    = {r2:.4f}")

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
    print("===== 🚿 Đào tạo mô hình sáng GRU (real only) =====")
    train_with_gru_only(np.array(morning_values), morning_date_list, MODEL_PATH_MORNING)

    print("\n===== 🌙 Đào tạo mô hình tối GRU (real only) =====")
    train_with_gru_only(np.array(evening_values), evening_date_list, MODEL_PATH_EVENING)
