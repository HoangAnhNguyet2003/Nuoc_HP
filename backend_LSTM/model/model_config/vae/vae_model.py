import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, Model

# ===== Xử lý dữ liệu =====

def prepare_data(values, look_back):
    X = []
    for i in range(len(values) - look_back):
        X.append(values[i:i + look_back])
    return np.array(X).reshape(-1, look_back, 1)

def average_group(values, group_size):
    return [np.mean(values[i:i + group_size]) for i in range(0, len(values), group_size)]

folder_path = '../../../data/raw_data/luu_luong_clean/'
look_back = 4

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

        morning_data = data[
            data['Giờ'].str.contains(':') &
            data['Ngày tháng'].str.contains('SA') &
            data['Giờ'].str.split(':').str[0].astype(int).between(1, 4)
        ]
        morning_values.extend(morning_data['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist())

        evening_data = data[
            data['Giờ'].str.contains(':') &
            data['Ngày tháng'].str.contains('CH') &
            data['Giờ'].str.split(':').str[0].astype(int).between(6, 9)
        ]
        evening_values.extend(evening_data['LƯU LƯỢNG TỨC THỜI 1'].dropna().tolist())

# Trung bình theo nhóm 4 giá trị
morning_avg_values = average_group(morning_values, 4)
evening_avg_values = average_group(evening_values, 4)

# Chuẩn bị dữ liệu cho mô hình VAE
morning_X = prepare_data(np.array(morning_avg_values), look_back)
evening_X = prepare_data(np.array(evening_avg_values), look_back)

# ===== Định nghĩa mô hình VAE =====

class Sampling(layers.Layer):
    def call(self, inputs):
        z_mean, z_log_var = inputs
        epsilon = tf.random.normal(shape=tf.shape(z_mean))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

def build_encoder(input_shape, latent_dim=16):
    inputs = layers.Input(shape=input_shape)
    x = layers.Dense(32, activation='relu')(inputs)
    x = layers.GlobalAveragePooling1D()(x)
    z_mean = layers.Dense(latent_dim, name='z_mean')(x)
    z_log_var = layers.Dense(latent_dim, name='z_log_var')(x)
    z = Sampling()([z_mean, z_log_var])
    return Model(inputs, [z_mean, z_log_var, z], name='encoder')

def build_decoder(timesteps, latent_dim=16):
    inputs = layers.Input(shape=(latent_dim,))
    x = layers.RepeatVector(timesteps)(inputs)
    x = layers.Dense(32, activation='relu')(x)
    outputs = layers.TimeDistributed(layers.Dense(1))(x)
    return Model(inputs, outputs, name='decoder')

class VAE(Model):
    def __init__(self, input_shape, latent_dim=16):
        super(VAE, self).__init__()
        self.timesteps = input_shape[0]
        self.encoder = build_encoder(input_shape, latent_dim)
        self.decoder = build_decoder(self.timesteps, latent_dim)

    def compile(self, optimizer):
        super(VAE, self).compile()
        self.optimizer = optimizer
        self.total_loss_tracker = tf.keras.metrics.Mean(name="loss")
        self.reconstruction_loss_tracker = tf.keras.metrics.Mean(name="reconstruction_loss")
        self.kl_loss_tracker = tf.keras.metrics.Mean(name="kl_loss")

    def train_step(self, data):
        if isinstance(data, tuple):
            data = data[0]

        with tf.GradientTape() as tape:
            z_mean, z_log_var, z = self.encoder(data)
            reconstruction = self.decoder(z)
            reconstruction_loss = tf.reduce_mean(tf.square(data - reconstruction))
            kl_loss = -0.5 * tf.reduce_mean(1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var))
            loss = reconstruction_loss + kl_loss

        grads = tape.gradient(loss, self.trainable_weights)
        self.optimizer.apply_gradients(zip(grads, self.trainable_weights))

        self.total_loss_tracker.update_state(loss)
        self.reconstruction_loss_tracker.update_state(reconstruction_loss)
        self.kl_loss_tracker.update_state(kl_loss)

        return {
            "loss": self.total_loss_tracker.result(),
            "reconstruction_loss": self.reconstruction_loss_tracker.result(),
            "kl_loss": self.kl_loss_tracker.result(),
        }

    @property
    def metrics(self):
        return [self.total_loss_tracker, self.reconstruction_loss_tracker, self.kl_loss_tracker]

# ===== Huấn luyện mô hình VAE =====

input_shape = (look_back, 1)

vae_morning = VAE(input_shape=input_shape)
vae_morning.compile(optimizer=tf.keras.optimizers.Adam())
print("\n▶️ Training morning VAE...")
vae_morning.fit(morning_X, epochs=100, batch_size=32)
vae_morning.encoder.save("encoder_morning.h5")
vae_morning.decoder.save("decoder_morning.h5")

vae_evening = VAE(input_shape=input_shape)
vae_evening.compile(optimizer=tf.keras.optimizers.Adam())
print("\n▶️ Training evening VAE...")
vae_evening.fit(evening_X, epochs=100, batch_size=32)
vae_evening.encoder.save("encoder_evening.h5")
vae_evening.decoder.save("decoder_evening.h5")

print("\n✅ Mô hình VAE sáng/tối đã được huấn luyện và lưu thành công.")
