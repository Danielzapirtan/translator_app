from googletrans import Translator
import gradio as gr

# Initialize the translator
translator = Translator()

def translate_text(text):
    # Translate the text from English to Romanian
    translation = translator.translate(text, src='en', dest='ro')
    return translation.text

# Create a Gradio interface
iface = gr.Interface(
    fn=translate_text,  # Function to call
    inputs="text",      # Input type
    outputs="text",     # Output type
    title="English to Romanian Translator",
    description="A simple translator that converts English text to Romanian using Google Translate."
)

# Launch the app
iface.launch(share=True)