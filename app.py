from flask import Flask, render_template, request, jsonify, send_file
from deep_translator import GoogleTranslator
import os
import uuid
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max file size

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def translate_text(text):
    """Translate text from English to Romanian"""
    if not text:
        return ""
    try:
        return GoogleTranslator(source='en', target='ro').translate(text)
    except Exception as e:
        return f"Translation error: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    translation = ""
    download_link = None
    
    if request.method == 'POST':
        submit_type = request.form.get('submit', '')
        
        if submit_type == 'text':
            # Handle text input
            text = request.form.get('text', '')
            translation = translate_text(text)
            
        elif submit_type == 'file':
            # Handle file upload
            if 'file' not in request.files:
                return render_template('index.html', error="No file part")
                
            file = request.files['file']
            if file.filename == '':
                return render_template('index.html', error="No file selected")
                
            if file and file.filename.endswith('.txt'):
                # Read and translate file content
                content = file.read().decode('utf-8')
                translation = translate_text(content)
                
                # Save translation to a temporary file
                filename = f"{uuid.uuid4()}.txt"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(translation)
                    
                download_link = f"/download/{filename}"
                
                # Format translation for display (preserve newlines)
                translation = translation.replace('\n', '<br>')
    
    return render_template('index.html', translation=translation, download_link=download_link)

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name="translation.txt")
    return "File not found", 404

@app.route('/api/translate', methods=['POST'])
def translate_api():
    data = request.get_json()
    text = data.get('text', '')
    translation = translate_text(text)
    return jsonify({'translation': translation})

if __name__ == '__main__':
    app.run(debug=True)