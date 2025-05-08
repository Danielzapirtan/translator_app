import os
from flask import Flask, render_template, request
from googletrans import Translator

app = Flask(__name__, template_folder='templates')
translator = Translator()

@app.route('/', methods=['GET', 'POST'])
def translate_text():
    translation = None
    original_text = ''
    if request.method == 'POST':
        original_text = request.form.get('text', '')
        if original_text:
            # Translate from English ('en') to Romanian ('ro')
            translation = translator.translate(original_text, src='en', dest='ro')
    return render_template('index.html', translation=translation, original_text=original_text)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)