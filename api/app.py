import os
from flask import Flask, render_template, request
from deep_translator import GoogleTranslator

app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET', 'POST'])
def translate_text():
    translation = None
    original_text = ""
    error = None
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == "":
                error = "No file selected."
            else:
 try:
    file = request.files.get('file')
    if not file or not file.filename.lower().endswith('.txt'):
        error = "Only TXT files are allowed."
    else:
        original_text = file.read().decode(errors="ignore")  # More flexible decoding
        try:
            translation = GoogleTranslator(source='en', target='ro').translate(original_text)
        except Exception as e:
            error = f"Translation failed: {str(e)}"
except Exception as e:
    error = f"An unexpected error occurred: {str(e)}"                try:
                    # Ensure it's a TXT file (additional check)
                    if not file.filename.lower().endswith('.txt'):
                        error = "Only TXT files are allowed."
                    else:
                        original_text = file.read().decode("utf-8")
                        # Translate the entire content from English to Romanian
                        translation = GoogleTranslator(source='en', target='ro').translate(original_text)
                except Exception as e:
                    error = f"An error occurred: {str(e)}"
        else:
            error = "File not provided."
    return render_template('index.html', translation=translation, original_text=original_text, error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)