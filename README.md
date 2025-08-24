🧠 NLPxNER – Named Entity Recognition Pipeline

📌 Project Description

NLPxNER is a lightweight web application that performs Named Entity Recognition (NER) on user-provided text. It allows users to paste or upload text and instantly extract key entities such as names, locations, organizations, dates, medical terms, and custom-defined entities.

The project leverages pre-trained NLP models (like SpaCy or Hugging Face transformers) to provide high-accuracy entity recognition without requiring heavy local training.

Built for developers, researchers, and students, the app runs seamlessly on minimal hardware (Linux Mint, low-spec laptops) while providing a clean, intuitive web-based interface.

🚀 Features

Extract entities (Person, Organization, Location, Date, Medical terms, etc.)

Support for multiple pre-trained NLP models

Upload plain text / PDF / image (OCR) for entity recognition

Minimalist WebApp (Flask backend + simple UI)

Lightweight – runs easily on low-spec Linux systems

Easy integration for future domains (healthcare, finance, legal, etc.)

🛠️ Tech Stack

Python 3.10+

Flask – for web backend

SpaCy / Hugging Face Transformers – for NLP models

Pytesseract + Pillow – for OCR (text from images)

2️⃣ Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # Linux/Mac  
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the app
python nlpXner.py <image path with name and extension> ocr_tesseract

📦 requirements.txt
flask
spacy
torch
transformers
pillow
pytesseract
pdfplumber
werkzeug
