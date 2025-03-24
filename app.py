# app.py
import gradio as gr
from googletrans import Translator
import PyPDF2

# Initialize the translator
translator = Translator()

def translate_text(text, src_lang='en', dest_lang='ro'):
    """Translate text from source language to destination language."""
    try:
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        return translated.text
    except Exception as e:
        return f"Error in translation: {e}"

def extract_text_from_pdf(file):
    """Extract text from a PDF file."""
    reader = PyPDF2.PdfFileReader(file)
    text = ''
    for page_num in range(reader.numPages):
        page = reader.getPage(page_num)
        text += page.extract_text()
    return text

def translate_file(file):
    """Translate the content of a file."""
    if file.name.endswith('.txt'):
        with open(file.name, 'r') as f:
            text = f.read()
    elif file.name.endswith('.pdf'):
        text = extract_text_from_pdf(file)
    else:
        return "Unsupported file format. Please upload a TXT or PDF file."

    return translate_text(text)

# Gradio interface
iface = gr.Interface(
    fn=translate_file,
    inputs=gr.components.File(label="Upload a TXT or PDF file"),
    outputs=gr.components.Textbox(label="Translated Text"),
    title="English to Romanian File Translator",
    description="Upload a TXT or PDF file to translate its content from English to Romanian."
)

# Launch the app
iface.launch(debug=True)