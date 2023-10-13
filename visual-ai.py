import os
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.optimizers import Adam



# Konstansok
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10

# Fehér paddinggal való átméretezés
def resize_with_padding(img, target_size=IMG_SIZE):
    original_width, original_height = img.size
    ratio = min(target_size/original_width, target_size/original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    img = img.resize((new_width, new_height), Image.ANTIALIAS)
    new_img = Image.new("RGB", (target_size, target_size), "white")
    y_offset = (target_size - new_height) // 2
    x_offset = (target_size - new_width) // 2
    new_img.paste(img, (x_offset, y_offset))
    return new_img

# Adatok betöltése és előkészítése
def load_data(directory, label):
    images = []
    labels = []
    for filename in os.listdir(directory):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            img_path = os.path.join(directory, filename)
            img = Image.open(img_path)
            img = resize_with_padding(img)
            img_array = np.array(img)
            images.append(img_array)
            labels.append(label)
    return np.array(images), np.array(labels)

good_images, good_labels = load_data('goodScreenshots', 1)
bad_images, bad_labels = load_data('badScreenshots', 0)

# Adatok összefűzése
X = np.concatenate((good_images, bad_images), axis=0)
y = np.concatenate((good_labels, bad_labels), axis=0)

# Adatok szétválasztása tanító és teszt adatokra
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Adat augmentáció
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest',
    rescale=1./255
)

# Modellépítés
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(512, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer=Adam(learning_rate=0.0001), loss='binary_crossentropy', metrics=['accuracy'])

# Tanítás
model.fit(datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
          steps_per_epoch=len(X_train) // BATCH_SIZE,
          epochs=EPOCHS,
          validation_data=(X_test, y_test)
)

# Modell mentése
model.save("visual_testing_model.h5")
