# 🌱 AgriSathi AI – AI-Powered Farming Assistant

## Overview

AgriSathi AI is an AI-powered farming assistant designed to help farmers access useful agricultural information and make informed farming decisions.

The project combines Machine Learning, Deep Learning, Computer Vision, NLP and Flask to provide multiple farming-related features through a web application.

## Features

- **Crop Disease Detection:** Uses a YOLO-based PlantDoc model to identify possible crop leaf disease classes from uploaded images.
- **AI Farming Chatbot:** Provides farming-related answers using a keyword-based knowledge database.
- **Crop Recommendation:** Recommends suitable crops based on soil and environmental parameters.
- **Weather Assistance:** Provides weather-related farming information.
- **Farming Knowledge:** Offers information about irrigation, fertilizers, soil health and crop management.
- **Bilingual Support:** Designed to support Hindi and English farming queries.

## Technologies Used

- Python
- Flask
- Machine Learning
- Deep Learning
- YOLO
- Computer Vision
- NLP
- HTML
- CSS
- JavaScript
- JSON

## Project Structure

```text
AgriSathi-AI/
├── app.py
├── farming_knowledge.json
├── requirements.txt
├── models/
├── templates/
├── static/
└── uploads/
```

## Installation and Setup

1. Clone this repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

2. Open the project directory:

```bash
cd AgriSathi-AI
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate it on Windows:

```bash
venv\Scripts\activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Make sure the trained model is available at:

```text
models/best.pt
```

7. Run the Flask application:

```bash
python app.py
```

8. Open your browser:

```text
http://127.0.0.1:5000
```

## Model Information

The crop disease detection component uses a YOLO model trained on PlantDoc data.

Predictions are experimental and should not be treated as confirmed agricultural diagnoses.

## Future Improvements

- Improve crop disease detection accuracy.
- Expand the agricultural knowledge database.
- Integrate reliable live weather information.
- Improve crop recommendation performance.
- Enhance the user interface and multilingual support.

## Author

Developed as an AI and Machine Learning project.
