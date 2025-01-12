# AI-Powered Cat Name Generator 🐾

## Overview
The AI-Powered Cat Name Generator is a machine learning-based application designed to predict fun and creative names for your feline friends based on their gender and photo. Leveraging deep learning and web scraping, this project offers a seamless way to generate cat names tailored to individual pets.

## Features
- **Data Scraping**: Collects real-world cat names and images from various adoption sites.
- **Deep Learning Model**: Combines convolutional neural networks and metadata (gender) to predict names.
- **Web Application**: User-friendly interface built with FastAPI for generating cat names in real-time.
- **Customization**: Supports uploading a photo and selecting gender for name suggestions.

## Inspiration
This project was inspired by Chester and Louie, my two mischievous cats. Their personalities inspired me to create an app that gives every cat a unique identity!

![Chester and Louie](static/chester_louie.JPG)

---

## Technologies Used
- **Python**: Core programming language
- **FastAPI**: Framework for building the web app
- **TensorFlow/Keras**: For training and deploying the deep learning model
- **BeautifulSoup & Requests**: For web scraping
- **NumPy & Pandas**: Data preprocessing and handling

---

## Installation and Usage

### Prerequisites
- Python 3.8 or later
- Virtual environment (optional but recommended)

### Steps
1. Clone this repository:
    ```bash
    git clone https://github.com/apinchofpepper/cat-name-generator.git
    cd cat-name-generator
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Prepare the dataset:
    - Run `pet-data-scraper.py` to scrape data from adoption websites.
4. Train the model:
    - Execute `model.py` to train the neural network and save the model files.
5. Start the web app:
    ```bash
    uvicorn app:app --reload
    ```
6. Open your browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Project Structure
- **`pet-data-scraper.py`**: Scrapes cat names, images, and metadata.
- **`name-predict.py`**: Predicts cat names using the trained model.
- **`model.py`**: Handles training of the deep learning model.
- **`app.py`**: Serves the FastAPI application for user interaction.
- **`static/`**: Stores static assets for the web application.
- **`dataset/`**: Contains scraped data (auto-generated).

---

## Future Improvements
- **Multilingual Support**: Extend name predictions to multiple languages.
- **Mobile App Integration**: Build a mobile app for on-the-go name generation.
- **Enhanced Personalization**: Add options for user input like "playful" or "elegant" names.

---

## Contributions
Contributions are welcome! Please open an issue or submit a pull request.

---

## License
This project is licensed under the MIT License.

---

## Contact
Created with ❤️ by Jack.
