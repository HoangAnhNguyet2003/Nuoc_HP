import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

class AutoEncoderModel:
    def __init__(self, input_dim=4, encoding_dim=16):
        self.set_seed(42)
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.model = self.build_model()

    def set_seed(self, seed_value):
        np.random.seed(seed_value)
        random.seed(seed_value)
        tf.random.set_seed(seed_value)

    def build_model(self):
        """
        Simple AutoEncoder:
        - Encoder: Dense(32) -> Dense(encoding_dim)
        - Decoder: Dense(32) -> Dense(input_dim)
        """
        model = Sequential(name="AutoEncoder")

        # Encoder
        model.add(Dense(32, activation='relu', input_shape=(self.input_dim,), name='encoder_dense1'))
        model.add(Dense(self.encoding_dim, activation='relu', name='latent_space'))

        # Decoder
        model.add(Dense(32, activation='relu', name='decoder_dense1'))
        model.add(Dense(self.input_dim, activation='linear', name='reconstruction'))

        model.compile(optimizer='adam', loss='mse')
        model.summary()
        return model

    def save_model_h5(self, file_path):
        """Lưu cả kiến trúc và trọng số vào file .h5"""
        self.model.save(file_path)
        print(f"Model đã được lưu tại: {file_path}")

# ======================= GỌI LƯU MÔ HÌNH =======================

if __name__ == "__main__":
    ae = AutoEncoderModel(input_dim=4, encoding_dim=16)
    ae.save_model_h5('../model_config/autoencoder_model.h5')
