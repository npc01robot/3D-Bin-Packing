import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

class GAN:
    def __init__(self):
        self.generator = self.build_generator()
        self.discriminator = self.build_discriminator()

    def build_generator(self):
        model = tf.keras.Sequential()
        model.add(layers.Dense(128, activation='relu', input_dim=100))
        model.add(layers.Dense(256, activation='relu'))
        model.add(layers.Dense(3, activation='sigmoid'))  # Output 3 values for width, height, depth
        return model

    def build_discriminator(self):
        model = tf.keras.Sequential()
        model.add(layers.Dense(256, activation='relu', input_dim=3))
        model.add(layers.Dense(1, activation='sigmoid'))
        return model

    def train(self, data, epochs=10000):
        for epoch in range(epochs):
            noise = np.random.normal(0, 1, (data.shape[0], 100))
            generated_data = self.generator.predict(noise)

            combined_data = np.concatenate([data, generated_data])
            labels = np.concatenate([np.ones(data.shape[0]), np.zeros(data.shape[0])])
            indices = np.arange(combined_data.shape[0])
            np.random.shuffle(indices)

            combined_data, labels = combined_data[indices], labels[indices]

            self.discriminator.train_on_batch(combined_data, labels)

            noise = np.random.normal(0, 1, (data.shape[0], 100))
            labels_gan = np.ones(data.shape[0])
            self.generator.train_on_batch(noise, labels_gan)

        return self.generator