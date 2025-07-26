import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import load_model
import os
import tensorflow as tf

np.random.seed(42)
tf.random.set_seed(42)
file_path = '../data/raw_data/Van_Dau8/luu_luong.csv'
MODEL_PATH = './model_config/models/lstm_model.h5'
assert os.path.exists(MODEL_PATH), "Không tìm thấy mô hình!"
model = load_model(MODEL_PATH)
model.compile(optimizer='adam', loss='mean_squared_error')

def detect_anomalies(train_preds, test_preds):
    iso_model = IsolationForest(contamination='auto', random_state=42)
    iso_model.fit(np.array(train_preds).reshape(-1, 1))
    preds = iso_model.predict(np.array(test_preds).reshape(-1, 1))
    return ["1" if p == -1 else "0" for p in preds]

def prepare_data(values, look_back):
    X, y = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
    return np.array(X).reshape(-1, look_back, 1), np.array(y)

def process_and_train(file_path):
    data = pd.read_csv(file_path)

    if 'LƯU LƯỢNG TỨC THỜI 1' not in data.columns:
        return {"error": f"Thiếu cột 'LƯU LƯỢNG TỨC THỜI 1' trong {file_path}"}

    if 'Thời gian' in data.columns:
        data['Thời gian'] = pd.to_timedelta(data['Thời gian'])

    avg_values = [
        round(data['LƯU LƯỢNG TỨC THỜI 1'][i:i+4].mean(), 3)
        for i in range(0, len(data), 4)
        if not data['LƯU LƯỢNG TỨC THỜI 1'][i:i+4].isnull().any()
    ]

    avg_values = np.array(avg_values)
    if len(avg_values) < 10:
        return {"error": "Dữ liệu quá ít để huấn luyện và dự đoán."}

    look_back = 4
    split_index = int(len(avg_values) * 0.8)
    train_values = avg_values[:split_index]
    test_values = avg_values[split_index:]

    X_train, y_train = prepare_data(train_values, look_back)
    if len(X_train) > 0:
        model.fit(X_train, y_train, epochs=100, batch_size=16, verbose=0)

    X_test, y_true = prepare_data(test_values, look_back)
    predictions = model.predict(X_test).flatten() if len(X_test) > 0 else []
    train_preds = model.predict(X_train).flatten() if len(X_train) > 0 else []

    total_groups = len(avg_values)
    test_groups = total_groups - split_index
    start_row = len(data) - (test_groups * 4)

    if 'Ngày tháng' not in data.columns:
        data['Ngày tháng'] = pd.to_datetime(data.index, unit='s')

    try:
        dates_raw = data['Ngày tháng'].iloc[start_row:].astype(str).str.split(' ').str[0]
        grouped_dates = dates_raw.groupby((dates_raw != dates_raw.shift()).cumsum()).first().reset_index(drop=True)
        dates = grouped_dates.values.flatten()[look_back:]
    except:
        dates = ["NaN"] * len(y_true)

    labels = detect_anomalies(train_preds, predictions)

    return {
        "true_values": y_true.tolist(),
        "pred_values": predictions.tolist(),
        "times": dates.tolist(),
        "isolation_labels": labels
    }
