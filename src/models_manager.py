import pandas as pd
import numpy as np
import os
import math
import tensorflow as tf

from keras.models import Sequential
from keras.layers import Dense, BatchNormalization, Activation, Dropout
from keras.regularizers import l2

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def get_model3_1():
    model = Sequential([
        Dense(128, input_shape=(5,), activation='relu'),
        BatchNormalization(),
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dense(512, activation='relu'),
        BatchNormalization(),
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    return model