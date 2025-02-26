import gradio as gr
from googletrans import Translator
import unicodedata
import re
import os
import tempfile

# Create a temporary directory for storing files
TEMP_DIR = tempfile.mkdtemp()

def clean_text(text):
    """
    Clean text by:
    1. Converting to NFKD form and removing combining characters
    2. Keeping only ASCII characters, basic punctuation, and whitespace
    3. Removing control characters except basic whitespace
    """
    # Convert to NFKD form and remove combining characters
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    
    # Define allowed characters (English letters, numbers, basic punctuation, whitespace)
    allowed_chars = re.compile(r'[^a-zA-Z0-9\s.,!?"\';:()\-\n]')
    text = allowed_chars.sub('', text)
    
    # Remove control characters while keeping basic whitespace
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t ')
    
    # Normalize whitespace (remove multiple spaces, but keep paragraphs)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()
    
    return text

def translate_file(file):
    """
    Translate a text file from English to Romanian
    """
    if file is None:
        return None, "No file uploaded"
    
    try:
        # Read file content
        with open(file.name, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean the content
        cleaned_content = clean_text(content)
        
        if not cleaned_content.strip():
            return None, "After cleaning non-English characters, the file is empty"
        
        # Split content into smaller chunks if it's large
        max_chunk_size = 5000  # characters
        chunks = [cleaned_content[i:i + max_chunk_size] 
                 for i in range(0, len(cleaned_content), max_chunk_size)]
        
        translator = Translator()
        translated_chunks = []
        
        # Progress tracking
        progress = gr.Progress()
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            progress(i/total_chunks, desc="Translating")
            # Add retry logic for each chunk
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    translated = translator.translate(chunk, src='en', dest='ro')
                    if translated and translated.text:
                        translated_chunks.append(translated.text)
                        break
                except Exception as e:
                    if attempt == max_retries - 1:
                        return None, f"Translation error: {str(e)}"
                    continue
        
        progress(1.0, desc="Finished")
        
        if not translated_chunks:
            return None, "Translation failed to produce any output"
        
        translated_content = ' '.join(translated_chunks)
        
        # Save the translated content to a file
        original_filename = os.path.basename(file.name)
        translated_filename = f"romanian_{original_filename}"
        output_path = os.path.join(TEMP_DIR, translated_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        return output_path, f"Translation complete! File saved as {translated_filename}"
        
    except Exception as e:
        return None, f"Error: {str(e)}"

def translate_text(text):
    """
    Translate text from English to Romanian
    """
    if not text.strip():
        return "No text to translate"
    
    try:
        cleaned_text = clean_text(text)
        
        if not cleaned_text.strip():
            return "After cleaning non-English characters, the text is empty"
        
        translator = Translator()
        translated = translator.translate(cleaned_text, src='en', dest='ro')
        
        if translated and translated.text:
            return translated.text
        else:
            return "Translation failed"
    
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="English to Romanian Translator") as app:
    gr.Markdown("# English to Romanian Translator")
    
    with gr.Tab("Text Translation"):
        with gr.Row():
            with gr.Column():
                input_text = gr.Textbox(label="English Text", placeholder="Enter text to translate", lines=10)
            with gr.Column():
                output_text = gr.Textbox(label="Romanian Translation", lines=10)
        
        translate_btn = gr.Button("Translate Text")
        translate_btn.click(fn=translate_text, inputs=input_text, outputs=output_text)
    
    with gr.Tab("File Translation"):
        input_file = gr.File(label="Upload .txt file in English", file_types=[".txt"])
        output_file = gr.File(label="Download translated file")
        status_text = gr.Textbox(label="Status", interactive=False)
        
        translate_file_btn = gr.Button("Translate File")
        translate_file_btn.click(
            fn=translate_file, 
            inputs=input_file, 
            outputs=[output_file, status_text]
        )
    
    gr.Markdown("""
    ## Notes
    - Maximum file size: 200MB
    - Only ASCII English text with basic punctuation is supported
    - The app will clean non-English characters before translation
    """)

# Launch the app
if __name__ == "__main__":
    app.launch(debug=True)