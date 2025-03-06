# Install required packages
import subprocess
import time
import requests
import threading
import io
import PyPDF2
import docx
import gradio as gr

# Install required packages using pip
subprocess.run(["pip", "install", "gradio", "libretranslate", "flask", "pypdf2", "python-docx"])

# Clone and setup LibreTranslate
subprocess.run(["rm", "-rf", "LibreTranslate"])
subprocess.run(["git", "clone", "https://github.com/LibreTranslate/LibreTranslate.git"])
subprocess.run(["pip", "install", "-e", "LibreTranslate"])

# Download language models for English and Romanian
subprocess.run(["python", "-m", "libretranslate.download", "--install-all", "--quiet", "en", "ro"])

# Run LibreTranslate API server in the background
def start_libretranslate_server():
    process = subprocess.Popen(
        ["libretranslate", "--host", "0.0.0.0", "--port", "5000", "--load-only", "en,ro"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

# Start the server in a separate thread
server_process = start_libretranslate_server()
print("Starting LibreTranslate server...")
time.sleep(10)  # Give it time to start

# Test if the server is up
try:
    response = requests.get("http://127.0.0.1:5000/languages")
    if response.status_code == 200:
        print("LibreTranslate server is running!")
        print(f"Available languages: {response.json()}")
    else:
        print(f"Server is up but returned status code {response.status_code}")
except requests.exceptions.ConnectionError:
    print("Failed to connect to LibreTranslate server")

# Function to extract text from different file types
def extract_text_from_file(file):
    """
    Extract text from various file types
    Supports .txt, .pdf, .docx files
    """
    filename = file.name
    if filename.endswith('.txt'):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()

    elif filename.endswith('.pdf'):
        with open(filename, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text

    elif filename.endswith('.docx'):
        doc = docx.Document(filename)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs if paragraph.text])

    else:
        return "Unsupported file type. Please upload .txt, .pdf, or .docx files."

# Define translation function using the API
def translate_text(text, source_lang, target_lang):
    if not text:
        return ""
    try:
        response = requests.post(
            "http://127.0.0.1:5000/translate",
            json={
                "q": text,
                "source": source_lang,
                "target": target_lang
            }
        )
        if response.status_code == 200:
            return response.json()["translatedText"]
        else:
            return f"Translation error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Translation error: {str(e)}"

# Function to translate file content
def translate_file(file, source_lang, target_lang):
    """
    Translate the content of an uploaded file
    """
    # Extract text from the file
    text = extract_text_from_file(file)

    # Translate the extracted text
    translated_text = translate_text(text, source_lang, target_lang)

    # Save translated text to a new file
    output_filename = f"translated_{file.name.split('/')[-1]}"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    return output_filename

# Create Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# LibreTranslate - English ↔ Romanian")

    with gr.Tabs():
        with gr.TabItem("Text Translation"):
            with gr.Row():
                with gr.Column():
                    source_text = gr.Textbox(label="Source Text", lines=5, placeholder="Enter text to translate...")
                    source_lang = gr.Dropdown(choices=["en", "ro"], value="en", label="Source Language")

                with gr.Column():
                    target_text = gr.Textbox(label="Translated Text", lines=5)
                    target_lang = gr.Dropdown(choices=["en", "ro"], value="ro", label="Target Language")

            # Text translation buttons
            with gr.Row():
                translate_btn = gr.Button("Translate")
                swap_btn = gr.Button("Swap Languages")

        with gr.TabItem("File Translation"):
            with gr.Row():
                file_input = gr.File(label="Upload File", type="filepath", file_types=['.txt', '.pdf', '.docx'])
                file_source_lang = gr.Dropdown(choices=["en", "ro"], value="en", label="Source Language")
                file_target_lang = gr.Dropdown(choices=["en", "ro"], value="ro", label="Target Language")

            file_translate_btn = gr.Button("Translate File")
            file_output = gr.File(label="Translated File")

    # Set up event handlers for text translation
    translate_btn.click(
        fn=translate_text,
        inputs=[source_text, source_lang, target_lang],
        outputs=target_text
    )

    # Add language swap functionality for text
    def swap_languages(source, target):
        return target, source

    swap_btn.click(
        fn=swap_languages,
        inputs=[source_lang, target_lang],
        outputs=[source_lang, target_lang]
    )

    # Set up event handlers for file translation
    file_translate_btn.click(
        fn=translate_file,
        inputs=[file_input, file_source_lang, file_target_lang],
        outputs=file_output
    )

    gr.Markdown("""
    ### Notes:
    - This is running LibreTranslate locally
    - Only English (en) and Romanian (ro) models are loaded
    - Translation happens entirely on this instance
    - Supports .txt, .pdf, and .docx file translations
    """)

# Launch the application
app.launch(server_name="0.0.0.0", server_port=7860)

# Add instructions for properly cleaning up when done
print("\nIMPORTANT: When you're done, run the following code to properly stop the server:")
print("server_process.terminate()")