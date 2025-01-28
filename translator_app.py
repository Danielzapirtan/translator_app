from flask import Flask, request, send_file, render_template_string, jsonify
from googletrans import Translator
from werkzeug.utils import secure_filename
import os
from io import StringIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>English to Romanian Translator</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .container { 
            background: #f5f5f5; 
            padding: 20px; 
            border-radius: 5px; 
            position: relative; 
        }
        .error { color: red; }
        .success { color: green; }
        
        .spinner-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #3498db;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        .timer {
            margin-top: 20px;
            font-size: 1.2em;
            font-family: monospace;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .submit-btn, .cancel-btn {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        .cancel-btn {
            background-color: #e74c3c;
        }
        .submit-btn:hover {
            background-color: #2980b9;
        }
        .cancel-btn:hover {
            background-color: #c0392b;
        }
        
        .file-input-container {
            margin: 20px 0;
        }

        .buttons-container {
            display: flex;
            gap: 10px;
        }
    </style>
</head>
<body>
    <div class="spinner-overlay">
        <div class="spinner"></div>
        <div class="timer">00:00.000</div>
        <button class="cancel-btn" onclick="cancelTranslation()">Cancel</button>
    </div>
    
    <div class="container">
        <h1>English to Romanian Translator</h1>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        {% if success %}
            <p class="success">{{ success }}</p>
        {% endif %}
        <form method="post" enctype="multipart/form-data" id="uploadForm">
            <div class="file-input-container">
                <p>Select a .txt file in English:</p>
                <input type="file" name="file" accept=".txt" required>
            </div>
            <div class="buttons-container">
                <input type="submit" value="Translate" class="submit-btn">
            </div>
        </form>
    </div>

    <script>
        let startTime;
        let timerInterval;
        let controller = null;
        const form = document.getElementById('uploadForm');
        const spinnerOverlay = document.querySelector('.spinner-overlay');
        const timerDisplay = document.querySelector('.timer');

        function updateTimer() {
            const currentTime = new Date();
            const elapsedTime = currentTime - startTime;
            const minutes = Math.floor(elapsedTime / 60000);
            const seconds = Math.floor((elapsedTime % 60000) / 1000);
            const milliseconds = elapsedTime % 1000;
            
            timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${milliseconds.toString().padStart(3, '0')}`;
        }

        function hideSpinner() {
            spinnerOverlay.style.display = 'none';
            if (timerInterval) {
                clearInterval(timerInterval);
            }
            timerDisplay.textContent = '00:00.000';
            if (controller) {
                controller = null;
            }
        }

        function cancelTranslation() {
            if (controller) {
                controller.abort();
                controller = null;
            }
            hideSpinner();
        }

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const fileInput = document.querySelector('input[type="file"]');
            
            if (fileInput.files.length > 0) {
                spinnerOverlay.style.display = 'flex';
                startTime = new Date();
                timerInterval = setInterval(updateTimer, 10);

                const formData = new FormData(form);
                controller = new AbortController();

                try {
                    const response = await fetch('/', {
                        method: 'POST',
                        body: formData,
                        signal: controller.signal
                    });

                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = response.headers.get('Content-Disposition').split('filename=')[1];
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                    } else {
                        const errorData = await response.text();
                        throw new Error(errorData);
                    }
                } catch (error) {
                    if (error.name === 'AbortError') {
                        console.log('Translation cancelled');
                    } else {
                        console.error('Error:', error);
                    }
                } finally {
                    hideSpinner();
                }
            }
        });

        // Clean up when leaving the page
        window.addEventListener('beforeunload', function() {
            if (timerInterval) {
                clearInterval(timerInterval);
            }
        });
    </script>
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
            content = file.read().decode('utf-8')
            translator = Translator()
            translated = translator.translate(content, src='en', dest='ro')
            
            original_filename = secure_filename(file.filename)
            translated_filename = f"romanian_{original_filename}"
            
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], translated_filename)
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(translated.text)
            
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
    app.run(debug=True, port=5055)