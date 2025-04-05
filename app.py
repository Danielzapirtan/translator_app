from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    translation = ""
    if request.method == 'POST':
        text = request.form.get('text', '')
        if text:
            translation = GoogleTranslator(source='en', target='ro').translate(text)
    return render_template('index.html', translation=translation)

@app.route('/api/translate', methods=['POST'])
def translate_api():
    data = request.get_json()
    text = data.get('text', '')
    translation = ""
    if text:
        translation = GoogleTranslator(source='en', target='ro').translate(text)
    return jsonify({'translation': translation})

if __name__ == '__main__':
    app.run(debug=True)