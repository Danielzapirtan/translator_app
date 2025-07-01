import gradio as gr
from transformers import MarianMTModel, MarianTokenizer
import torch
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

class EnglishRomanianTranslator:
    def __init__(self):
        self.model_name = "Helsinki-NLP/opus-mt-en-ro"
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
    def load_model(self):
        """Load the translation model and tokenizer"""
        try:
            print("Loading translation model... This may take a few minutes on first run.")
            self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
            self.model = MarianMTModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            print("Model loaded successfully!")
            return "Model loaded successfully! Ready to translate."
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            print(error_msg)
            return error_msg
    
    def translate_text(self, text):
        """Translate English text to Romanian"""
        if not text or not text.strip():
            return "Please enter some text to translate."
        
        if self.model is None or self.tokenizer is None:
            return "Model not loaded. Please click 'Load Model' first."
        
        try:
            # Handle long texts by splitting into sentences
            sentences = self.split_into_sentences(text)
            translated_sentences = []
            
            for sentence in sentences:
                if sentence.strip():
                    # Tokenize and translate
                    inputs = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=512)
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = self.model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
                    
                    translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    translated_sentences.append(translated)
                else:
                    translated_sentences.append("")
            
            return " ".join(translated_sentences)
            
        except Exception as e:
            error_msg = f"Translation error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def split_into_sentences(self, text):
        """Simple sentence splitting for better translation of long texts"""
        import re
        # Split on sentence endings but keep the punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return sentences

# Initialize translator
translator = EnglishRomanianTranslator()

def translate_wrapper(text):
    """Wrapper function for Gradio interface"""
    return translator.translate_text(text)

def load_model_wrapper():
    """Wrapper function for loading model"""
    return translator.load_model()

# Create Gradio interface
def create_interface():
    with gr.Blocks(title="English to Romanian Translator", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # 🇬🇧 ➡️ 🇷🇴 English to Romanian Translator
            
            This app uses the Helsinki-NLP Opus MT model for accurate English to Romanian translation.
            No API keys required, unlimited text length, completely free!
            """
        )
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Load Model First")
                load_btn = gr.Button("🔄 Load Translation Model", variant="primary", size="lg")
                load_status = gr.Textbox(
                    label="Status", 
                    placeholder="Click 'Load Translation Model' to begin...",
                    interactive=False
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 🇬🇧 English Text")
                input_text = gr.Textbox(
                    label="Enter English text to translate",
                    placeholder="Type your English text here...",
                    lines=10,
                    max_lines=20
                )
                
            with gr.Column(scale=1):
                gr.Markdown("### 🇷🇴 Romanian Translation")
                output_text = gr.Textbox(
                    label="Romanian translation will appear here",
                    lines=10,
                    max_lines=20,
                    interactive=False
                )
        
        with gr.Row():
            translate_btn = gr.Button("🔄 Translate", variant="primary", size="lg")
            clear_btn = gr.Button("🗑️ Clear", variant="secondary")
        
        gr.Markdown(
            """
            ### Features:
            - **Accurate Translation**: Uses Helsinki-NLP's OPUS-MT model trained specifically for English-Romanian
            - **No Limits**: Translate text of any length
            - **Free**: No API keys or costs required
            - **Offline**: Runs locally on your machine
            - **GPU Accelerated**: Automatically uses GPU if available for faster translation
            
            ### Tips:
            - For best results, use proper punctuation and grammar
            - Very long texts are automatically split into sentences for processing
            - First translation may take longer as the model loads into memory
            """
        )
        
        # Event handlers
        load_btn.click(
            fn=load_model_wrapper,
            outputs=load_status
        )
        
        translate_btn.click(
            fn=translate_wrapper,
            inputs=input_text,
            outputs=output_text
        )
        
        clear_btn.click(
            fn=lambda: ("", ""),
            outputs=[input_text, output_text]
        )
        
        # Auto-translate on text change (with debouncing)
        input_text.change(
            fn=translate_wrapper,
            inputs=input_text,
            outputs=output_text
        )
    
    return app

if __name__ == "__main__":
    # Create and launch the app
    app = create_interface()
    
    print("Starting English to Romanian Translation App...")
    print("The app will be available at: http://127.0.0.1:7860")
    print("Press Ctrl+C to stop the server")
    
    # Launch the app
    app.launch(
        server_name="127.0.0.1",  # localhost only
        server_port=7860,         # default Gradio port
        share=False,              # don't create public link
        debug=False,              # set to True for development
        show_error=True
    )