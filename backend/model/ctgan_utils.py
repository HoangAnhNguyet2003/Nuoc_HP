import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from scipy.stats import ks_2samp, entropy, wasserstein_distance
from ctgan import CTGAN

# ============ CẤU HÌNH ============
np.random.seed(42)
tf.random.set_seed(42)
MODEL_PATH = './model_config/lstm_model.h5'
CSV_PATH = '../data/raw_data/Van_Dau8/luu_luong.csv'

assert os.path.exists(MODEL_PATH), "Không tìm thấy mô hình!"
assert os.path.exists(CSV_PATH), "Không tìm thấy file dữ liệu!"


model = load_model(MODEL_PATH)
model.compile(optimizer='adam', loss='mean_squared_error')

def prepare_data(values, look_back):
    X, y = [], []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
        y.append(values[i + look_back])
    return np.array(X).reshape(-1, look_back, 1), np.array(y)

def to_tabular_dataset(values, look_back):
    records = []
    for i in range(len(values) - look_back):
        row = list(values[i:i+look_back]) + [values[i+look_back]]
        records.append(row)
    columns = [f"step_{i+1}" for i in range(look_back)] + ["label"]
    return pd.DataFrame(records, columns=columns)

def js_divergence(p, q, bins=50):
    p_hist, _ = np.histogram(p, bins=bins, density=True)
    q_hist, _ = np.histogram(q, bins=bins, density=True)
    m = 0.5 * (p_hist + q_hist)
    epsilon = 1e-8
    return 0.5 * (entropy(p_hist + epsilon, m + epsilon) + entropy(q_hist + epsilon, m + epsilon))


def process_and_train_with_ctgan(file_path, look_back=4):
    print(" Đang xử lý dữ liệu...")
    data = pd.read_csv(file_path)

    if 'LƯU LƯỢNG TỨC THỜI 1' not in data.columns:
        raise ValueError("Thiếu cột 'LƯU LƯỢNG TỨC THỜI 1' trong dữ liệu.")

    avg_values = [
        round(data['LƯU LƯỢNG TỨC THỜI 1'][i:i+look_back].mean(), 3)
        for i in range(0, len(data), look_back)
        if not data['LƯU LƯỢNG TỨC THỜI 1'][i:i+look_back].isnull().any()
    ]
    avg_values = np.array(avg_values)

    if len(avg_values) < 20:
        raise ValueError("Dữ liệu quá ít để huấn luyện hoặc sinh dữ liệu.")

    split_index = int(len(avg_values) * 0.8)
    train_values = avg_values[:split_index]
    test_values = avg_values[split_index:]

    df_ctgan = to_tabular_dataset(train_values, look_back)

    print(" Huấn luyện CTGAN...")
    ctgan = CTGAN(epochs=300)
    ctgan.fit(df_ctgan)
    synthetic_df = ctgan.sample(200)

    if "label" not in synthetic_df.columns:
        raise ValueError("CTGAN không sinh được cột 'label'.")

    print("\n Đánh giá chất lượng dữ liệu sinh:")
    for col in df_ctgan.columns:
        real = df_ctgan[col].values
        synth = synthetic_df[col].values
        ks_stat, p_val = ks_2samp(real, synth)
        js = js_divergence(real, synth)
        wd = wasserstein_distance(real, synth)
        print(f" {col:<7} ➝ KS = {ks_stat:.4f}, p = {p_val:.4f}, JS = {js:.4f}, WD = {wd:.4f}")

    
    X_train_real, y_train_real = prepare_data(train_values, look_back)
    X_synth = synthetic_df.drop("label", axis=1).values.reshape(-1, look_back, 1)
    y_synth = synthetic_df["label"].values

    X_train_full = np.concatenate([X_train_real, X_synth])
    y_train_full = np.concatenate([y_train_real, y_synth])

    print("\n Huấn luyện lại LSTM với dữ liệu mở rộng")
    model.fit(X_train_full, y_train_full, epochs=100, batch_size=16, verbose=1)

    X_test, y_true = prepare_data(test_values, look_back)
    predictions = model.predict(X_test).flatten()

    mse = mean_squared_error(y_true, predictions)
    mae = mean_absolute_error(y_true, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, predictions)

    print("\n Evaluation Metrics (LSTM):")
    print(f"    MSE   = {mse:.4f}")
    print(f"    MAE   = {mae:.4f}")
    print(f"    RMSE  = {rmse:.4f}")
    print(f"    R²    = {r2:.4f}")

    result_df = pd.DataFrame({
        "True": y_true,
        "Predicted": predictions
    })
    result_df.to_csv("prediction_results.csv", index=False)
    print(" Dự đoán đã lưu vào: prediction_results.csv")

    model.save('./model_config/lstm_model_finetuned.h5')
    print(" Mô hình đã lưu vào: lstm_model_finetuned.h5")

# ============ CHẠY ============
if __name__ == "__main__":
    try:
        process_and_train_with_ctgan(CSV_PATH)
    except Exception as e:
        print(" Lỗi khi chạy script:", str(e))
