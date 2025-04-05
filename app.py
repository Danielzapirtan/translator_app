from flask import Flask, render_template, request, jsonify, flash
import os
import tempfile
from werkzeug.utils import secure_filename
from deep_translator import GoogleTranslator
import PyPDF2
import io

app = Flask(__name__)
app.secret_key = 'translation_app_secret_key'  # Required for flash messages
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text() + "\n\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        text = f"Error extracting text from PDF: {e}"
    return text

def extract_text_from_file(file):
    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ""
    
    if extension == 'pdf':
        return extract_text_from_pdf(file)
    elif extension == 'txt':
        return file.read().decode('utf-8')
    else:
        return "Unsupported file format"

def translate_text(text, source='en', target='ro'):
    # If text is too long, chunk it to avoid translator limitations
    max_chunk_size = 4000  # Google Translator typically has limits around 5000 chars
    translations = []
    
    if len(text) <= max_chunk_size:
        return GoogleTranslator(source=source, target=target).translate(text)
    
    # Split by newlines to maintain some structure
    paragraphs = text.split('\n')
    current_chunk = ""
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 1 <= max_chunk_size:
            current_chunk += paragraph + '\n'
        else:
            # Translate the current chunk if it's not empty
            if current_chunk:
                translations.append(GoogleTranslator(source=source, target=target).translate(current_chunk))
            current_chunk = paragraph + '\n'
    
    # Don't forget the last chunk
    if current_chunk:
        translations.append(GoogleTranslator(source=source, target=target).translate(current_chunk))
    
    return '\n'.join(translations)

@app.route('/', methods=['GET', 'POST'])
def index():
    translation = ""
    original_text = ""
    
    if request.method == 'POST':
        # Check if the post request has a file part
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    original_text = extract_text_from_file(file)
                    translation = translate_text(original_text)
                else:
                    flash('File type not supported. Please upload PDF or TXT files only.')
        else:
            # Handle direct text input
            original_text = request.form.get('text', '')
            if original_text:
                translation = translate_text(original_text)
    
    return render_template('index.html', translation=translation, original_text=original_text)

@app.route('/api/translate', methods=['POST'])
def translate_api():
    if request.is_json:
        data = request.get_json()
        text = data.get('text', '')
        translation = ""
        if text:
            translation = translate_text(text)
        return jsonify({'translation': translation})
    
    # Handle file upload via API
    elif request.files:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            text = extract_text_from_file(file)
            translation = translate_text(text)
            return jsonify({
                'original_text': text,
                'translation': translation
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
    
    return jsonify({'error': 'Invalid request'}), 400

if __name__ == '__main__':
    app.run(debug=True)