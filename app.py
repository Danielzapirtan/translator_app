# Install required packages
import subprocess
import time
import requests
import threading
import io
import PyPDF2
import docx
from flask import Flask, request, render_template, send_file

# Install required packages using pip
subprocess.run(["pip", "install", "flask", "libretranslate", "pypdf2", "python-docx"])

# Clone and setup LibreTranslate
subprocess.run(["rm", "-rf", "LibreTranslate"])
subprocess.run(["git", "clone", "https://github.com/LibreTranslate/LibreTranslate.git"])
subprocess.run(["pip", "install", "-e", "LibreTranslate"])

# Download language models for English and Romanian
subprocess.run(["python", "-m", "libretranslate.download", "--install-all", "--quiet", "en", "ro"])

# Run LibreTranslate API server in the background
def start_libretranslate_server():
    process = subprocess.Popen(
        ["libretranslate", "--host", "0.0.0.0", "--port", "5000", "--load-only", "en,ro"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

# Start the server in a separate thread
server_process = start_libretranslate_server()
print("Starting LibreTranslate server...")
time.sleep(10)  # Give it time to start

# Test if the server is up
try:
    response = requests.get("http://127.0.0.1:5000/languages")
    if response.status_code == 200:
        print("LibreTranslate server is running!")
        print(f"Available languages: {response.json()}")
    else:
        print(f"Server is up but returned status code {response.status_code}")
except requests.exceptions.ConnectionError:
    print("Failed to connect to LibreTranslate server")

# Function to extract text from different file types
def extract_text_from_file(file):
    """
    Extract text from various file types
    Supports .txt, .pdf, .docx files
    """
    filename = file.filename
    if filename.endswith('.txt'):
        return file.read().decode('utf-8')

    elif filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

    elif filename.endswith('.docx'):
        doc = docx.Document(file)
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
def translate_file(file, source_lang, target_lang):
    """
    Translate the content of an uploaded file
    """
    # Extract text from the file
    text = extract_text_from_file(file)

    # Translate the extracted text
    translated_text = translate_text(text, source_lang, target_lang)

    # Save translated text to a new file
    output_filename = f"translated_{file.filename}"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    return output_filename

# Create Flask application
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "text" in request.form:
            # Handle text translation
            source_text = request.form["source_text"]
            source_lang = request.form["source_lang"]
            target_lang = request.form["target_lang"]
            translated_text = translate_text(source_text, source_lang, target_lang)
            return render_template("index.html", translated_text=translated_text)
        elif "file" in request.files:
            # Handle file translation
            file = request.files["file"]
            source_lang = request.form["file_source_lang"]
            target_lang = request.form["file_target_lang"]
            output_filename = translate_file(file, source_lang, target_lang)
            return send_file(output_filename, as_attachment=True)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)

# Add instructions for properly cleaning up when done
print("\nIMPORTANT: When you're done, run the following code to properly stop the server:")
print("server_process.terminate()")