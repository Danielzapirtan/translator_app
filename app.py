from flask import Flask, request, render_template, send_file, jsonify
import subprocess
import time
import requests
import PyPDF2
import docx
import os
import uuid
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TRANSLATED_FOLDER'] = 'translated_files'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TRANSLATED_FOLDER'], exist_ok=True)

# Function to extract text from different file types
def extract_text_from_file(file_path):
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_path.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])
    else:
        return "Unsupported file type. Please upload .txt, .pdf, or .docx files."

# Define translation function using the API
def translate_text(text, source_lang, target_lang):
    if not text:
        return ""
    try:
        response = requests.post(
            "http://127.0.0.1:5000/translate",
            json={
                "q": text,
                "source": source_lang,
                "target": target_lang
            }
        )
        if response.status_code == 200:
            return response.json()["translatedText"]
        else:
            return f"Translation error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Translation error: {str(e)}"

# Function to translate file content
def translate_file(file_path, source_lang, target_lang):
    # Extract text from the file
    text = extract_text_from_file(file_path)

    # Translate the extracted text
    translated_text = translate_text(text, source_lang, target_lang)

    # Save translated text to a new file
    output_filename = os.path.join(app.config['TRANSLATED_FOLDER'], f"translated_{os.path.basename(file_path)}")
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    return output_filename

# Route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

# Route to handle file upload and translation
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Save the uploaded file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)

    # Get translation parameters
    source_lang = request.form.get("source_lang", "en")
    target_lang = request.form.get("target_lang", "ro")

    # Simulate processing delay (for demonstration purposes)
    time.sleep(2)

    # Translate the file
    translated_file_path = translate_file(file_path, source_lang, target_lang)

    # Return the translated file for download
    return jsonify({
        "status": "completed",
        "download_url": f"/download/{os.path.basename(translated_file_path)}"
    })

# Route to download translated files
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_file(os.path.join(app.config['TRANSLATED_FOLDER'], filename), as_attachment=True)

# Route to check processing status
@app.route("/status", methods=["GET"])
def check_status():
    return jsonify({"status": "processing"})  # Simulate processing status

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)