import numpy as np
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense

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
        model.add(LSTM(100, activation='relu', return_sequences=True, input_shape=(4, 1)))
        model.add(Dropout(0.2))
        model.add(LSTM(50, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        return model

    def save_model_h5(self, file_path):
        self.model.save(file_path)

# ======================= GỌI LƯU MÔ HÌNH =======================

if __name__ == "__main__":
    model = LSTMModel()
    model.save_model_h5('../models/lstm_model.h5')