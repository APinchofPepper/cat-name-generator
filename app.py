from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import io
import logging

# Initialize the FastAPI app
app = FastAPI()

# Mount the static directory for serving static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the model and label encoder at startup
try:
    model = load_model('cat_name_model.keras')
    label_classes = np.load('label_encoder.npy', allow_pickle=True)
    logging.info("Model and label encoder loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model or label encoder: {e}")
    raise RuntimeError("Failed to load model or label encoder")

# Define a function to predict cat names
def predict_cat_name(img_data, gender, top_n=5):
    try:
        # Preprocess the image
        img = image.load_img(io.BytesIO(img_data), target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        # Prepare gender as input
        gender_array = np.array([0 if gender.lower() == 'male' else 1]).reshape(-1, 1)
        
        # Predict probabilities for each class
        predictions = model.predict([img_array, gender_array])
        
        # Add more randomness
        predictions += np.random.uniform(0, 0.001, predictions.shape)
        
        # Get the indices of the top N predictions
        top_indices = np.argsort(predictions[0])[-top_n:][::-1]
        
        # Map the indices to the corresponding cat names
        top_names = [(label_classes[idx], float(predictions[0][idx])) for idx in top_indices]
        
        return top_names
    
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        raise RuntimeError("Prediction failed")

# Define the route for the main page
@app.get("/", response_class=HTMLResponse)
async def main():
    content = """
    <html>
    <head>
        <title>Cat Name Generator</title>
        <style>
            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                color: #333;
            }
            h1 {
                color: #4A90E2;
                text-align: center;
                margin: 20px 0;
            }
            form {
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                padding: 20px;
                width: 100%;
                max-width: 500px;
                text-align: center;
            }
            label {
                font-weight: bold;
                display: block;
                margin-bottom: 10px;
            }
            input[type="file"],
            select,
            input[type="submit"] {
                padding: 10px;
                font-size: 16px;
                margin: 10px 0;
                width: 100%;
                border: 1px solid #ccc;
                border-radius: 5px;
                box-sizing: border-box;
            }
            input[type="submit"] {
                background-color: #4A90E2;
                color: #fff;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #357ABD;
            }
            .cat-image {
                max-width: 40%;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-top: 20px;
            }
            .predictions {
                margin-top: 20px;
                width: 100%;
                max-width: 500px;
                text-align: center;
            }
            ul {
                list-style-type: none;
                padding: 0;
                margin: 0;
            }
            li {
                background-color: #fff;
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            #inspiration {
                text-align: center;
                margin-top: 40px;
            }
            .separator {
                border-top: 2px solid #ccc;
                margin: 40px 0;
                width: 80%;
            }
        </style>
    </head>
    <body>
        <h1>Cat Name Genius</h1>
        <form id="catForm" action="/upload" enctype="multipart/form-data" method="post">
            <label for="file">Upload a picture of your cat:</label>
            <input name="file" type="file" accept="image/*">
            <label for="gender">Pick a gender:</label>
            <select name="gender">
                <option value="male">Male</option>
                <option value="female">Female</option>
            </select>
            <input type="submit" value="Generate Name">
        </form>

        <div id="results" class="predictions"></div>

        <div class="separator"></div>

        <section id="inspiration">
            <h2>Inspiration Behind the Project</h2>
            <p>This project was inspired by my two cats, Chester and Louie.</p>
            <img src="/static/chester_louie.JPG" alt="Chester and Louie" class="cat-image">
        </section>

        <script>
            document.getElementById("catForm").onsubmit = async function(event) {
                event.preventDefault();
                const formData = new FormData(event.target);
                const response = await fetch("/upload", {
                    method: "POST",
                    body: formData
                });
                const resultHtml = await response.text();
                document.getElementById("results").innerHTML = resultHtml;
            }
        </script>
    </body>
    </html>
    """
    return content

# Define the route for handling uploads and predictions
@app.post("/upload")
async def upload(file: UploadFile = File(...), gender: str = Form(...)):
    try:
        contents = await file.read()

        predictions = predict_cat_name(contents, gender)

        # Format predictions as an HTML list
        formatted_predictions = "<h2>Predicted Names:</h2><ul>"
        for name, probability in predictions:
            formatted_predictions += f"<li>{name} (Probability: {probability:.2%})</li>"
        formatted_predictions += "</ul>"

        # Return the formatted predictions
        return HTMLResponse(content=formatted_predictions)

    except Exception as e:
        logging.error(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the uploaded file")

# Start the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
