import os
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.ensemble import IsolationForest
from tensorflow.keras.models import load_model

# ─── 1) Thiết lập seed và đường dẫn ──────────────────────────────
np.random.seed(42)
tf.random.set_seed(42)

FILE_PATH  = '../data/raw_data/Van_Dau8/luu_luong.csv'
MODEL_PATH = './model_config/autoencoder_model.h5'  # đổi thành autoencoder

assert os.path.exists(FILE_PATH),  f"Không tìm thấy dữ liệu tại {FILE_PATH}"
assert os.path.exists(MODEL_PATH), f"Không tìm thấy mô hình tại {MODEL_PATH}"

# ─── 2) Hàm tiện ích ───────────────────────────────────────────────
def prepare_windows(values: np.ndarray, look_back: int = 4):
    """
    Tạo X có shape (n_samples, look_back) từ mảng 1D `values`.
    Mỗi sample là một vector 4 chiều.
    """
    X = [values[i : i + look_back] for i in range(len(values) - look_back)]
    return np.array(X, dtype='float32')

def detect_anomalies(train_err: np.ndarray, test_err: np.ndarray):
    """
    Dùng IsolationForest trên reconstruction-error.
    train_err/test_err: 1D array của MSE mỗi window.
    """
    iso = IsolationForest(contamination='auto', random_state=42)
    iso.fit(train_err.reshape(-1, 1))
    pred = iso.predict(test_err.reshape(-1, 1)) 
    return ["1" if p == -1 else "0" for p in pred]

def process_and_train(
    file_path: str,
    model_path: str,
    look_back: int = 4,
    epochs: int = 100,
    batch_size: int = 16
):
   
    df = pd.read_csv(file_path)
    if 'LƯU LƯỢNG TỨC THỜI 1' not in df.columns:
        return {"error": "Thiếu cột 'LƯU LƯỢNG TỨC THỜI 1'."}

    
    vals = []
    for i in range(0, len(df), look_back):
        block = df['LƯU LƯỢNG TỨC THỜI 1'][i : i + look_back]
        if len(block) == look_back and not block.isnull().any():
            vals.append(block.mean())
    values = np.array(vals, dtype='float32')
    if len(values) < look_back * 3:
        return {"error": "Dữ liệu quá ít để huấn luyện."}

    
    split_idx  = int(len(values) * 0.8)
    train_vals = values[:split_idx]
    test_vals  = values[split_idx:]

    X_train = prepare_windows(train_vals, look_back)
    X_test  = prepare_windows(test_vals,  look_back)

    # 3.4) Load & fine‑tune AutoEncoder
    ae = load_model(model_path, compile=False)
    ae.compile(optimizer='adam', loss='mse')
    ae.fit(
        X_train, X_train,
        epochs=epochs,
        batch_size=batch_size,
        verbose=0
    )
    recon_train  = ae.predict(X_train)
    recon_test   = ae.predict(X_test)
    train_errors = np.mean((X_train - recon_train)**2, axis=1)
    test_errors  = np.mean((X_test  - recon_test )**2, axis=1)

    # 3.6) Phát hiện anomalies
    labels = detect_anomalies(train_errors, test_errors)

    # 3.7) Lấy thời gian cho mỗi window test nếu có cột 'Thời gian'
    if 'Thời gian' in df.columns:
        df = df.reset_index(drop=True)
        start_row = split_idx * look_back + look_back
        times = pd.to_timedelta(df['Thời gian']) \
                  .iloc[start_row : start_row + len(test_errors)]
        times = times.astype(str).str.split(' ').str[0].tolist()
    else:
        times = ["NaN"] * len(test_errors)

    return {
        "reconstruction_error": test_errors.tolist(),
        "anomaly_labels":      labels,
        "times":               times
    }

# ─── 4) Chạy khi file này được gọi trực tiếp ──────────────────────
if __name__ == "__main__":
    result = process_and_train(FILE_PATH, MODEL_PATH)
