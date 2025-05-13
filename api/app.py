import os
from flask import Flask, render_template, request
from deep_translator import GoogleTranslator

app = Flask(__name__, template_folder='templates')

def translate_large_text(text, source='en', target='ro', chunk_size=4000):
    """
    Translate large text by breaking it into chunks.
    """
    translator = GoogleTranslator(source=source, target=target)
    translated_chunks = []
    
    # Split the text into chunks
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    for chunk in chunks:
        try:
            translated_chunk = translator.translate(chunk)
            translated_chunks.append(translated_chunk)
        except Exception as e:
            # If a chunk fails, return the error
            return None, f"Translation error: {str(e)}"
    
    return ''.join(translated_chunks), None

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
                    if not file.filename.lower().endswith('.txt'):
                        error = "Only TXT files are allowed."
                    else:
                        original_text = file.read().decode("utf-8")
                        if len(original_text) > 4000:
                            # Use chunked translation for large files
                            translation, chunk_error = translate_large_text(original_text)
                            if chunk_error:
                                error = chunk_error
                        else:
                            # Direct translation for small files
                            try:
                                translation = GoogleTranslator(source='en', target='ro').translate(original_text)
                            except Exception as e:
                                error = f"Translation error: {str(e)}"
                except Exception as e:
                    error = f"File processing error: {str(e)}"
        else:
            error = "File not provided."
    
    return render_template('index.html', 
                         translation=translation, 
                         original_text=original_text, 
                         error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)