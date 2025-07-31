import os
import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
from sdv.single_table import CTGANSynthesizer
from sdv.metadata import SingleTableMetadata
from scipy.stats import ks_2samp, entropy, wasserstein_distance

np.random.seed(42)
tf.random.set_seed(42)
folder_path = '../data/raw_data/luu_luong_clean/'
MODEL_PATH_MORNING = '../lstm/lstm_model_morning_ctgan.h5'
MODEL_PATH_EVENING = '../lstm/lstm_model_evening_ctgan.h5'
RESULT_PATH_MORNING = '../lstm/results_morning_ctgan.csv'
RESULT_PATH_EVENING = '../lstm/results_evening_ctgan.csv'
look_back = 14


def prepare_data(values, look_back):
    X, y, dates = [], [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
        dates.append(i + look_back)
    return np.array(X).reshape(-1, look_back, 1), np.array(y), np.array(dates)

def to_tabular_dataset(values, look_back):
    records = []
    for i in range(len(values) - look_back):
        row = list(values[i:i+look_back]) + [values[i+look_back]]
        records.append(row)
    columns = [f"step_{i+1}" for i in range(look_back)] + ["label"]
    return pd.DataFrame(records, columns=columns)

def build_ctgan_synthesizer(df):
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)
    synthesizer = CTGANSynthesizer(
        metadata=metadata,
        enforce_rounding=False,
        epochs=500,
        verbose=True
    )
    return synthesizer

def js_divergence(p, q, bins=50):
    p_hist, _ = np.histogram(p, bins=bins, density=True)
    q_hist, _ = np.histogram(q, bins=bins, density=True)
    m = 0.5 * (p_hist + q_hist)
    epsilon = 1e-8
    return 0.5 * (entropy(p_hist + epsilon, m + epsilon) + entropy(q_hist + epsilon, m + epsilon))

# ========== TRAIN CTGAN + LSTM ========== #
def train_with_ctgan_and_lstm(values, date_list, model_path, result_path):
    df_ctgan = to_tabular_dataset(values, look_back)
    print(" Huấn luyện CTGAN...")

    synthesizer = build_ctgan_synthesizer(df_ctgan)
    synthesizer.fit(df_ctgan)
    synthetic_df = synthesizer.sample(200)

    print(" Đánh giá dữ liệu synthetic:")
    for col in df_ctgan.columns:
        real = df_ctgan[col].values
        synth = synthetic_df[col].values
        ks_stat, p_val = ks_2samp(real, synth)
        js = js_divergence(real, synth)
        wd = wasserstein_distance(real, synth)
        print(f"  {col:<8} ➝ KS={ks_stat:.4f}, p={p_val:.4f}, JS={js:.4f}, WD={wd:.4f}")

    X_real, y_real, indices = prepare_data(values, look_back)
    X_synth = synthetic_df.drop("label", axis=1).values.reshape(-1, look_back, 1)
    y_synth = synthetic_df["label"].values

    X_train = np.concatenate([X_real, X_synth])
    y_train = np.concatenate([y_real, y_synth])

    model = Sequential()
    model.add(LSTM(100, activation='tanh', return_sequences=True, input_shape=(look_back, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(100, activation='tanh'))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    print(" Huấn luyện lại LSTM...")
    model.fit(X_train, y_train, epochs=200, batch_size=64, verbose=1)
    model.save(model_path)
    print(f" Mô hình đã lưu vào: {model_path}")

    predictions = model.predict(X_real).flatten()
    mae = mean_absolute_error(y_real, predictions)
    mse = mean_squared_error(y_real, predictions)
    r2 = r2_score(y_real, predictions)

    print("\n Kết quả dự đoán:")
    for i in range(min(10, len(y_real))):
        print(f"  Ngày: {date_list[i]}, Thật: {y_real[i]:.2f}, Dự đoán: {predictions[i]:.2f}")

    print("\n Metrics:")
    print(f" 🔸 MAE   = {mae:.4f}")
    print(f" 🔸 MSE   = {mse:.4f}")
    print(f" 🔸 R²    = {r2:.4f}")

# ========== TIỀN XỬ LÝ DỮ LIỆU ========== #
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

# ========== HUẤN LUYỆN ========== #
morning_X, morning_y, morning_d = prepare_data(np.array(morning_values), look_back)
evening_X, evening_y, evening_d = prepare_data(np.array(evening_values), look_back)
morning_date_list = np.array(morning_dates)[morning_d]
evening_date_list = np.array(evening_dates)[evening_d]

if __name__ == "__main__":
    print("=====  Đào tạo mô hình sáng với CTGAN =====")
    train_with_ctgan_and_lstm(np.array(morning_values), morning_date_list, MODEL_PATH_MORNING, RESULT_PATH_MORNING)

    print("\n=====  Đào tạo mô hình tối với CTGAN =====")
    train_with_ctgan_and_lstm(np.array(evening_values), evening_date_list, MODEL_PATH_EVENING, RESULT_PATH_EVENING)
