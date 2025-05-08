import gradio as gr
from deep_translator import GoogleTranslator

def translate_file(file):
    with open(file.name, "r", encoding="utf-8") as f:
        text = f.read()
    
    translator = GoogleTranslator(source="english", target="romanian")
    translated_text = translator.translate(text)
    
    return translated_text

iface = gr.Interface(
    fn=translate_file,
    inputs=gr.File(label="Upload a TXT file"),
    outputs=gr.Textbox(label="Translated Text"),
    title="TXT File Translator - English to Romanian"
)

iface.launch()