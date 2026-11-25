
from flask import Flask, render_template, request, jsonify, session
from ultralytics import YOLO
from pathlib import Path
from werkzeug.utils import secure_filename
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

import uuid
import os
import json
import re


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)
app.secret_key = "change-this-to-a-long-random-secret"


# ==========================================
# PROJECT FOLDERS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
PREDICTION_FOLDER = BASE_DIR / "static" / "predictions"

MODEL_PATH = BASE_DIR / "models" / "best.pt"
DATABASE_FILE = BASE_DIR / "farming_knowledge.json"

UPLOAD_FOLDER.mkdir(exist_ok=True)
PREDICTION_FOLDER.mkdir(parents=True, exist_ok=True)


# ==========================================
# LOAD TRAINED YOLO MODEL
# ==========================================

print("Loading YOLO model...")

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"YOLO model not found: {MODEL_PATH}"
    )

model = YOLO(str(MODEL_PATH))

print("YOLO model loaded successfully!")


# ==========================================
# PLANTDOC DISEASE NAME MAPPING
# ==========================================

DISEASE_INFO = {

    "Apple Scab Leaf": "Apple Scab",
    "Apple rust leaf": "Apple Rust",
    "Bell_pepper leaf spot": "Bell Pepper Leaf Spot",
    "Corn Gray leaf spot": "Corn Gray Leaf Spot",
    "Corn leaf blight": "Corn Leaf Blight",
    "Corn rust leaf": "Corn Rust",
    "Potato leaf early blight": "Potato Early Blight",
    "Potato leaf late blight": "Potato Late Blight",
    "Squash Powdery mildew leaf": "Squash Powdery Mildew",
    "Tomato Early blight leaf": "Tomato Early Blight",
    "Tomato Septoria leaf spot": "Tomato Septoria Leaf Spot",
    "Tomato leaf bacterial spot": "Tomato Bacterial Spot",
    "Tomato leaf late blight": "Tomato Late Blight",
    "Tomato leaf mosaic virus": "Tomato Mosaic Virus",
    "Tomato leaf yellow virus": "Tomato Yellow Leaf Virus",
    "Tomato mold leaf": "Tomato Mold",
    "Tomato two spotted spider mites leaf":
        "Tomato Two-Spotted Spider Mites",
    "grape leaf black rot": "Grape Black Rot"

}


# ==========================================
# GENERAL LEAF CLASSES
# These are not automatically healthy.
# ==========================================

GENERAL_LEAF_CLASSES = {

    "Apple leaf",
    "Bell_pepper leaf",
    "Blueberry leaf",
    "Cherry leaf",
    "Peach leaf",
    "Potato leaf",
    "Raspberry leaf",
    "Soyabean leaf",
    "Strawberry leaf",
    "Tomato leaf",
    "grape leaf"

}


# ==========================================
# DISPLAY MODEL CLASSES
# ==========================================

print("\n========== PLANTDOC MODEL CLASSES ==========")

for class_id, class_name in model.names.items():
    print(f"{class_id}: {class_name}")

print("============================================\n")


# ==========================================
# LOAD FARMING KNOWLEDGE DATABASE
# ==========================================

with open(DATABASE_FILE, "r", encoding="utf-8") as file:
    knowledge = json.load(file)

print("Farming knowledge database loaded!")


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# PLANT DISEASE PREDICTION PAGE
# ==========================================

@app.route("/prediction")
def prediction():

    return render_template("predict.html")


# ==========================================
# YOLO PLANT DISEASE DETECTION
# ==========================================

@app.route("/predict", methods=["POST"])
def predict():

    print("\n================================")
    print("PLANT DISEASE PREDICTION STARTED")
    print("================================")

    try:

        # ----------------------------------
        # CHECK UPLOADED IMAGE
        # ----------------------------------

        if "image" not in request.files:
            return "No image uploaded. Please select an image."

        file = request.files["image"]

        if file.filename == "":
            return "Please select an image."

        # ----------------------------------
        # VALIDATE IMAGE EXTENSION
        # ----------------------------------

        allowed_extensions = {"jpg", "jpeg", "png"}

        if "." not in file.filename:
            return "Invalid image filename."

        extension = file.filename.rsplit(".", 1)[-1].lower()

        if extension not in allowed_extensions:
            return "Please upload JPG, JPEG, or PNG."

        # ----------------------------------
        # SAVE UPLOADED IMAGE
        # ----------------------------------

        filename = secure_filename(file.filename)

        unique_name = f"{uuid.uuid4().hex}_{filename}"

        image_path = UPLOAD_FOLDER / unique_name

        file.save(str(image_path))

        print("IMAGE UPLOADED:", image_path)

        # ----------------------------------
        # VERIFY IMAGE
        # ----------------------------------

        with Image.open(image_path) as uploaded_image:
            uploaded_image.verify()

        print("IMAGE VERIFIED")

        # ==================================
        # RUN YOLO PREDICTION
        # ==================================

        print("\nRUNNING PLANTDOC MODEL...")
        print("CONFIDENCE THRESHOLD: 0.10")

        results = model.predict(
            source=str(image_path),
            conf=0.10,
            imgsz=416,
            verbose=False
        )

        if not results:
            return "Unable to analyze this image."

        result = results[0]

        print("\nYOLO PREDICTION COMPLETED")

        # ==================================
        # DEBUGGING OUTPUT
        # ==================================

        print("\n========== YOLO DEBUG INFORMATION ==========")

        if result.boxes is not None:

            print("TOTAL DETECTED BOXES:", len(result.boxes))

            for box in result.boxes:

                class_id = int(box.cls[0])

                class_name = model.names[class_id]

                confidence = float(box.conf[0]) * 100

                print("--------------------------------")

                print("CLASS ID:", class_id)

                print("CLASS NAME:", class_name)

                print("CONFIDENCE:", round(confidence, 2), "%")

        else:

            print("YOLO BOXES: None")

        print("============================================\n")

        # ==================================
        # SAVE ANNOTATED IMAGE
        # ==================================

        annotated_image = result.plot()[:, :, ::-1]

        output_name = f"result_{uuid.uuid4().hex}.jpg"

        output_path = PREDICTION_FOLDER / output_name

        Image.fromarray(annotated_image).save(output_path)

        print("RESULT IMAGE SAVED:", output_path)

        # ==================================
        # EXTRACT DISEASE PREDICTIONS
        # ==================================

        predictions = []

        if result.boxes is not None:

            for box in result.boxes:

                class_id = int(box.cls[0])

                confidence = float(box.conf[0]) * 100

                raw_class_name = model.names[class_id]

                # Convert raw label into readable name

                readable_name = DISEASE_INFO.get(
                    raw_class_name,
                    raw_class_name
                )

                # Identify class type

                if raw_class_name in DISEASE_INFO:

                    prediction_type = "Disease Class"

                elif raw_class_name in GENERAL_LEAF_CLASSES:

                    prediction_type = "General Leaf Class"

                else:

                    prediction_type = "Unknown Class"

                predictions.append({

                    "name": readable_name,

                    "raw_name": raw_class_name,

                    "confidence": round(confidence, 2),

                    "type": prediction_type

                })

        # ==================================
        # SORT PREDICTIONS
        # ==================================

        predictions.sort(
            key=lambda x: x["confidence"],
            reverse=True
        )

        # ==================================
        # BEST PREDICTION
        # ==================================

        if predictions:

            best_prediction = predictions[0]

            disease_name = best_prediction["name"]

            confidence = best_prediction["confidence"]

            status = best_prediction["type"]

            print("\nDETECTED CLASS:", disease_name)

            print("CLASS TYPE:", status)

            print("CONFIDENCE:", confidence, "%")

        else:

            disease_name = "No known class detected"

            confidence = None

            status = "No Detection"

            print("\nNO PLANTDOC CLASS DETECTED")

        print("\nALL PREDICTIONS:", predictions)

        # ==================================
        # RENDER RESULT PAGE
        # ==================================

        return render_template(

            "result.html",

            predictions=predictions,

            disease_name=disease_name,

            confidence=confidence,

            status=status,

            image_path=f"predictions/{output_name}"

        )

    except Exception:

        app.logger.exception("CROP PREDICTION ERROR")

        return (
            "An error occurred during crop analysis. "
            "Please check the Flask terminal."
        ), 500


# ==========================================
# AGRISATHI CHATBOT
# ==========================================

def normalize(text):

    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text)

    return " ".join(text.split())


# ==========================================
# FIND CHATBOT ANSWER
# ==========================================

def find_answer(message):

    normalized_message = normalize(message)

    best_category = None

    best_score = 0

    for category, details in knowledge.items():

        score = 0

        for keyword in details["keywords"]:

            normalized_keyword = normalize(keyword)

            if not normalized_keyword:
                continue

            pattern = (
                r"(?<!\w)" +
                re.escape(normalized_keyword) +
                r"(?!\w)"
            )

            if re.search(pattern, normalized_message):

                score += max(
                    1,
                    len(normalized_keyword.split())
                )

        if score > best_score:

            best_score = score

            best_category = category

    if best_category:

        return knowledge[best_category]["answer"]

    return knowledge.get(
        "unknown",
        {}
    ).get(
        "answer",
        "Welcome to AgriSathi AI! Please ask a farming-related question."
    )


# ==========================================
# CHATBOT PAGE
# ==========================================

@app.route("/chatbot")
def chatbot_page():

    return render_template("chatbot.html")


# ==========================================
# CHATBOT API
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True) or {}

        message = data.get("message", "").strip()

        if not message:

            return jsonify({
                "error": "Please enter a message."
            }), 400

        if len(message) > 1500:

            return jsonify({
                "error": "Maximum 1500 characters allowed."
            }), 400

        answer = find_answer(message)

        # Save conversation history

        history = session.get("chat_history", [])

        history.append({

            "role": "user",

            "content": message

        })

        history.append({

            "role": "assistant",

            "content": answer

        })

        session["chat_history"] = history[-20:]

        return jsonify({

            "reply": answer

        })

    except Exception:

        app.logger.exception("Chatbot error")

        return jsonify({

            "error": "Something went wrong. Please try again."

        }), 500


# ==========================================
# CLEAR CHAT HISTORY
# ==========================================

@app.route("/clear-chat", methods=["POST"])
def clear_chat():

    session.pop("chat_history", None)

    return jsonify({

        "message": "Chat cleared successfully."

    })


# ==========================================
# CHAT HISTORY
# ==========================================

@app.route("/history", methods=["GET"])
def history():

    return jsonify({

        "history": session.get("chat_history", [])

    })


# ==========================================
# RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(

        debug=True,

        use_reloader=False

    )
