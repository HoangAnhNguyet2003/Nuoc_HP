import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
import pandas as pd
import os

folder_path = '../../data/raw_data/luu_luong_clean/'
MODEL_PATH_MORNING = '../lstm/lstm_model_morning.h5'
MODEL_PATH_EVENING = '../lstm/lstm_model_evening.h5'
look_back = 14

def prepare_data(values, look_back):
    X, y = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
    return np.array(X).reshape(-1, look_back, 1), np.array(y)

def average_group(values, group_size):
    return [np.mean(values[i:i + group_size]) for i in range(0, len(values), group_size)]


morning_values = []
evening_values = []
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        data = pd.read_csv(file_path)

        data['Ngày'] = data['Ngày tháng'].str.split(' ').str[0]
        data['Giờ'] = data['Ngày tháng'].str.split(' ').str[1]

        for col in ['LƯU LƯỢNG TỨC THỜI 1', 'ÁP LỰC 1', 'TỔNG LƯU LƯỢNG 1', 'Tiêu thụ']:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        # ===== Xử lý dữ liệu sáng (1h-4h sáng)
        morning_data = data[
            data['Giờ'].str.contains(':') &
            data['Ngày tháng'].str.contains('SA') &
            data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
        ]

        # ===== Xử lý dữ liệu tối (6h-9h tối)
        evening_data = data[
            data['Giờ'].str.contains(':') &
            data['Ngày tháng'].str.contains('CH') &
            data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
        ]

        # === Nhóm theo ngày và tính TB sáng
        for date in morning_data['Ngày'].unique():
            daily_values = morning_data[morning_data['Ngày'] == date]['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
            if len(daily_values) >= 1:
                avg = np.mean(daily_values[:4])
                morning_values.append(avg)

        # === Nhóm theo ngày và tính TB tối
        for date in evening_data['Ngày'].unique():
            daily_values = evening_data[evening_data['Ngày'] == date]['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist()
            if len(daily_values) >= 1:
                avg = np.mean(daily_values[:4])
                evening_values.append(avg)

# Không cần chia nhóm nữa, đã tính TB mỗi ngày rồi
# Tạo tập X, y như thường
morning_X, morning_y = prepare_data(np.array(morning_values), look_back)
evening_X, evening_y = prepare_data(np.array(evening_values), look_back)


class LSTMModel:
    def __init__(self):
        self.set_seed(42)
        self.model = self.build_model()

    def set_seed(self, seed_value):
        np.random.seed(seed_value)
        random.seed(seed_value)
        tf.random.set_seed(seed_value)

    def build_model(self):
        model = Sequential()
        model.add(LSTM(100, activation='tanh', return_sequences=True, input_shape=(look_back, 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(100, activation='tanh'))
        model.add(Dropout(0.2))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def train_model(self, X, y, epochs=150, batch_size=64):
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size)

    def save_model_h5(self, file_path):
        self.model.save(file_path)

if __name__ == "__main__":
    # mô hình sáng
    morning_model = LSTMModel()
    morning_model.train_model(morning_X, morning_y)
    morning_model.save_model_h5(MODEL_PATH_MORNING)

    # mô hình tối
    evening_model = LSTMModel()
    evening_model.train_model(evening_X, evening_y)
    evening_model.save_model_h5(MODEL_PATH_EVENING)