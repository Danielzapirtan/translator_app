from deep_translator import GoogleTranslator
import gradio as gr

def translate_text(text):
    # Check for empty input
    if not text or text.strip() == "":
        return "Please enter some text to translate."
    
    try:
        # Limit text length if needed (Google Translator has limits)
        if len(text) > 5000:
            return "Text is too long. Please enter text with fewer than 5000 characters."
            
        # Translate the text from English to Romanian
        translation = GoogleTranslator(source='en', target='ro').translate(text)
        return translation
    except Exception as e:
        return f"Translation error: {str(e)}"

# Create a Gradio interface
iface = gr.Interface(
    fn=translate_text,  # Function to call
    inputs=gr.Textbox(placeholder="Enter English text here..."),
    outputs=gr.Textbox(),
    title="English to Romanian Translator",
    description="Enter text in English and get it translated to Romanian.",
    examples=["Hello, how are you?", "The weather is nice today."]
)

# Launch the Gradio app
if __name__ == "__main__":
    try:
        iface.launch(debug=True)
    except Exception as e:
        print(f"Failed to launch Gradio interface: {str(e)}")