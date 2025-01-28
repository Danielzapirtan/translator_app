from flask import Flask, request, send_file, render_template_string
from googletrans import Translator
from werkzeug.utils import secure_filename
import os
from io import StringIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# HTML template for the upload form
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>English to Romanian Translator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 5px; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>English to Romanian Translator</h1>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        {% if success %}
            <p class="success">{{ success }}</p>
        {% endif %}
        <form method="post" enctype="multipart/form-data">
            <p>Select a .txt file in English:</p>
            <input type="file" name="file" accept=".txt" required>
            <br><br>
            <input type="submit" value="Translate">
        </form>
    </div>
</body>
</html>
'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'txt'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(HTML_TEMPLATE, error='No file selected')
        
        file = request.files['file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, error='No file selected')
        
        if not allowed_file(file.filename):
            return render_template_string(HTML_TEMPLATE, error='Please upload a .txt file')
        
        try:
            # Read the content of the uploaded file
            content = file.read().decode('utf-8')
            
            # Initialize translator
            translator = Translator()
            
            # Translate content
            translated = translator.translate(content, src='en', dest='ro')
            
            # Create a file-like object with the translated content
            translated_file = StringIO(translated.text)
            
            # Generate translated filename
            original_filename = secure_filename(file.filename)
            translated_filename = f"romanian_{original_filename}"
            
            # Save translated content to a temporary file
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], translated_filename)
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(translated.text)
            
            # Send the translated file to the user
            return send_file(
                temp_path,
                as_attachment=True,
                download_name=translated_filename,
                mimetype='text/plain'
            )
            
        except Exception as e:
            return render_template_string(HTML_TEMPLATE, error=f'Error during translation: {str(e)}')
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5055, debug=True)
