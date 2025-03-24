# app.py
import gradio as gr
from googletrans import Translator
import PyPDF2
from google.colab import files

def translate_file(file_obj):
    if file_obj is None:
        return "Please upload a file first!"
    
    # Initialize translator
    translator = Translator()
    
    # Get file extension
    file_name = file_obj.name.lower()
    translated_text = ""
    
    try:
        if file_name.endswith('.txt'):
            # Read TXT file
            with open(file_obj.name, 'r', encoding='utf-8') as f:
                text = f.read()
            # Translate
            translated = translator.translate(text, src='en', dest='ro')
            translated_text = translated.text
            
        elif file_name.endswith('.pdf'):
            # Read PDF file
            pdf_reader = PyPDF2.PdfReader(file_obj)
            num_pages = len(pdf_reader.pages)
            text = ""
            # Extract text from all pages
            for page in range(num_pages):
                text += pdf_reader.pages[page].extract_text()
            # Translate
            translated = translator.translate(text, src='en', dest='ro')
            translated_text = translated.text
            
        else:
            return "Please upload a TXT or PDF file!"
            
        return translated_text
    
    except Exception as e:
        return f"Error processing file: {str(e)}"

# Create Gradio interface
interface = gr.Interface(
    fn=translate_file,
    inputs=gr.File(label="Upload TXT or PDF file"),
    outputs=gr.Textbox(label="Translated Text (Romanian)"),
    title="English to Romanian File Translator",
    description="Upload a TXT or PDF file in English to translate it to Romanian",
    allow_flagging="never"
)

# Launch the interface
interface.launch(debug=True)