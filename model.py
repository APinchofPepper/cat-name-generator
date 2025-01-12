import tensorflow as tf
print(tf.__version__)
from tensorflow.keras import layers, models, Input
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np

# Load the preprocessed data
images = np.load('images.npy')
genders = np.load('genders.npy')
labels = np.load('labels.npy')

# Test label_encoder
print(labels[:10])  # Print the first 10 labels to verify

# Encode the labels (cat names)
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

# Save the actual cat names, not the indices
np.save('label_encoder.npy', label_encoder.classes_)

# Split the data into training, validation, and test sets
X_train_images, X_temp_images, X_train_genders, X_temp_genders, y_train, y_temp = train_test_split(
    images, genders, encoded_labels, test_size=0.3, random_state=42)
X_val_images, X_test_images, X_val_genders, X_test_genders, y_val, y_test = train_test_split(
    X_temp_images, X_temp_genders, y_temp, test_size=0.5, random_state=42)

print(f'Training set: {len(X_train_images)} samples')
print(f'Validation set: {len(X_val_images)} samples')
print(f'Test set: {len(X_test_images)} samples')

# Create a model with two inputs: images and gender
input_image = Input(shape=(224, 224, 3), name='image_input')
input_gender = Input(shape=(1,), name='gender_input')

# Image processing branch
x = layers.Conv2D(32, (3, 3), activation='relu')(input_image)
x = layers.MaxPooling2D((2, 2))(x)
x = layers.Conv2D(64, (3, 3), activation='relu')(x)
x = layers.MaxPooling2D((2, 2))(x)
x = layers.Conv2D(128, (3, 3), activation='relu')(x)
x = layers.MaxPooling2D((2, 2))(x)
x = layers.Flatten()(x)

# Gender processing branch
y = layers.Dense(8, activation='relu')(input_gender)

# Concatenate the processed image and gender data
combined = layers.concatenate([x, y])

# Final dense layers
z = layers.Dense(128, activation='relu')(combined)
output = layers.Dense(len(label_encoder.classes_), activation='softmax')(z)

# Create the model
model = models.Model(inputs=[input_image, input_gender], outputs=output)

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

history = model.fit([X_train_images, X_train_genders], y_train, epochs=10, 
                    validation_data=([X_val_images, X_val_genders], y_val), 
                    batch_size=32)

test_loss, test_acc = model.evaluate([X_test_images, X_test_genders], y_test)
print(f'Test accuracy: {test_acc:.2f}')

# Save the model in the new Keras format
model.save('cat_name_model.keras')

print(np.load('label_encoder.npy', allow_pickle=True))
