from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Load the model
model = load_model('cat_name_model.keras')

# Load the label encoder classes
label_classes = np.load('label_encoder.npy', allow_pickle=True)

def predict_cat_name(img_path, gender, top_n=5):
    # Preprocess the image
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    
    # Prepare gender as input
    gender_array = np.array([0 if gender.lower() == 'male' else 1]).reshape(-1, 1)
    
    # Predict probabilities for each class
    predictions = model.predict([img_array, gender_array])
    
    # Get the indices of the top N predictions
    top_indices = np.argsort(predictions[0])[-top_n:][::-1]
    
    # Map the indices to the corresponding cat names
    top_names = [(label_classes[idx], predictions[0][idx]) for idx in top_indices]
    
    return top_names

# Example usage
top_5_names = predict_cat_name('IMG_2274.jpg', 'male')
for name, probability in top_5_names:
    print(f"{name}: {probability:.4f}")
