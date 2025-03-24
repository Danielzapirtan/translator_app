from deep_translator import GoogleTranslator
import gradio as gr

def translate_text(text):
    # Translate the text from English to Romanian
    translation = GoogleTranslator(source='en', target='ro').translate(text)
    return translation

# Create a Gradio interface
iface = gr.Interface(
    fn=translate_text,  # Function to call
    inputs="text",      # Input type
    outputs="text",     # Output type
    title="English to Romanian Translator",
    description="Enter text in English and get it translated to Romanian."
)

# Launch the Gradio app
iface.launch(debug=True)