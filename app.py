import ipywidgets as widgets
from IPython.display import display, HTML
import io
import base64
from googletrans import Translator
import os
import tempfile

class EnglishToRomanianTranslator:
    def __init__(self):
        self.translator = Translator()
        self.translated_text = ""
        self.original_filename = ""
        
        # Create widgets
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        # File upload widget
        self.file_upload = widgets.FileUpload(
            accept='.txt',
            multiple=False,
            description='Upload TXT file'
        )
        
        # Translate button
        self.translate_btn = widgets.Button(
            description='Translate to Romanian',
            button_style='primary',
            disabled=True,
            icon='translate'
        )
        
        # Download button
        self.download_btn = widgets.Button(
            description='Download Translation',
            button_style='success',
            disabled=True,
            icon='download'
        )
        
        # Status and preview
        self.status_label = widgets.HTML(
            value="<b>Status:</b> Please upload a TXT file to begin translation"
        )
        
        self.preview_text = widgets.Textarea(
            placeholder='Original English text will appear here...',
            description='English Text:',
            layout=widgets.Layout(width='100%', height='150px'),
            disabled=True
        )
        
        self.translated_preview = widgets.Textarea(
            placeholder='Romanian translation will appear here...',
            description='Romanian Text:',
            layout=widgets.Layout(width='100%', height='150px'),
            disabled=True
        )
        
        # Progress bar
        self.progress_bar = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description='Progress:',
            style={'bar_color': '#0066cc'},
            layout=widgets.Layout(width='100%', visibility='hidden')
        )
        
        # Statistics
        self.stats_label = widgets.HTML(
            value="<i>File statistics will appear here...</i>"
        )
        
    def setup_layout(self):
        # Event handlers
        self.file_upload.observe(self.on_file_upload, names='value')
        self.translate_btn.on_click(self.on_translate_click)
        self.download_btn.on_click(self.on_download_click)
        
        # Create styled layout
        header = widgets.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border-radius: 10px; margin-bottom: 20px;">
            <h1>🇬🇧 ➡️ 🇷🇴 English to Romanian Translator</h1>
            <p>Upload your English text file and get instant Romanian translation</p>
        </div>
        """)
        
        upload_section = widgets.VBox([
            widgets.HTML("<h3>📁 Upload English Text File</h3>"),
            self.file_upload,
            self.status_label,
            self.stats_label
        ], layout=widgets.Layout(margin='10px 0'))
        
        control_section = widgets.VBox([
            widgets.HTML("<h3>🔄 Translation Controls</h3>"),
            widgets.HBox([self.translate_btn, self.download_btn], 
                        layout=widgets.Layout(justify_content='center')),
            self.progress_bar
        ], layout=widgets.Layout(margin='10px 0'))
        
        preview_section = widgets.VBox([
            widgets.HTML("<h3>📄 Text Preview</h3>"),
            self.preview_text,
            widgets.HTML("<div style='margin: 10px 0;'></div>"),
            self.translated_preview
        ], layout=widgets.Layout(margin='10px 0'))
        
        self.main_layout = widgets.VBox([
            header,
            upload_section,
            control_section,
            preview_section
        ], layout=widgets.Layout(padding='20px', max_width='800px'))
        
    def on_file_upload(self, change):
        """Handle file upload"""
        if change['new']:
            uploaded_file = list(change['new'].values())[0]
            self.original_filename = uploaded_file['metadata']['name']
            
            try:
                # Read the file content
                content = uploaded_file['content']
                text_content = content.decode('utf-8')
                
                # Update preview
                self.preview_text.value = text_content
                
                # Calculate statistics
                word_count = len(text_content.split())
                char_count = len(text_content)
                line_count = len(text_content.split('\n'))
                
                self.stats_label.value = f"""
                <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    <strong>📊 File Statistics:</strong><br>
                    • Characters: {char_count:,}<br>
                    • Words: {word_count:,}<br>
                    • Lines: {line_count:,}
                </div>
                """
                
                self.status_label.value = f"<b>Status:</b> ✅ File '{self.original_filename}' loaded successfully"
                
                # Enable translate button
                self.translate_btn.disabled = False
                
                # Clear previous translation
                self.translated_preview.value = ""
                self.download_btn.disabled = True
                
            except Exception as e:
                self.status_label.value = f"<b>Error:</b> ❌ Failed to read file: {str(e)}"
                self.translate_btn.disabled = True
                self.stats_label.value = ""
                
    def on_translate_click(self, button):
        """Handle English to Romanian translation"""
        if not self.preview_text.value:
            self.status_label.value = "<b>Error:</b> ❌ No text to translate"
            return
            
        try:
            # Show progress bar and disable button
            self.progress_bar.layout.visibility = 'visible'
            self.progress_bar.value = 0
            self.translate_btn.disabled = True
            
            # Update status
            self.status_label.value = "<b>Status:</b> 🔄 Translating English text to Romanian..."
            self.progress_bar.value = 20
            
            # Get source text
            source_text = self.preview_text.value
            self.progress_bar.value = 40
            
            # Perform translation in chunks for better handling of large texts
            if len(source_text) > 4000:
                # Split into smaller chunks to avoid API limits
                chunks = []
                sentences = source_text.split('. ')
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk + sentence) < 3500:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Translate each chunk
                translated_chunks = []
                for i, chunk in enumerate(chunks):
                    self.status_label.value = f"<b>Status:</b> 🔄 Translating chunk {i+1}/{len(chunks)}..."
                    
                    translated_chunk = self.translator.translate(
                        chunk, 
                        src='en', 
                        dest='ro'
                    )
                    translated_chunks.append(translated_chunk.text)
                    
                    # Update progress
                    progress = 40 + (40 * (i + 1) / len(chunks))
                    self.progress_bar.value = int(progress)
                
                self.translated_text = ' '.join(translated_chunks)
                
            else:
                # Translate directly for smaller texts
                result = self.translator.translate(
                    source_text, 
                    src='en', 
                    dest='ro'
                )
                self.translated_text = result.text
                self.progress_bar.value = 80
            
            # Update preview
            self.translated_preview.value = self.translated_text
            self.progress_bar.value = 100
            
            # Calculate translation statistics
            original_words = len(source_text.split())
            translated_words = len(self.translated_text.split())
            
            self.status_label.value = f"""
            <b>Status:</b> ✅ Translation completed successfully!<br>
            <small>Original: {original_words} words → Romanian: {translated_words} words</small>
            """
            
            # Enable download button
            self.download_btn.disabled = False
            
        except Exception as e:
            self.status_label.value = f"<b>Error:</b> ❌ Translation failed: {str(e)}"
            self.download_btn.disabled = True
            
        finally:
            self.translate_btn.disabled = False
            # Hide progress bar after completion
            import time
            time.sleep(1)
            self.progress_bar.layout.visibility = 'hidden'
            
    def on_download_click(self, button):
        """Handle download of translated text"""
        if not self.translated_text:
            self.status_label.value = "<b>Error:</b> ❌ No translated text to download"
            return
            
        try:
            # Create download filename
            base_name = os.path.splitext(self.original_filename)[0]
            download_filename = f"{base_name}_translated_romanian.txt"
            
            # Create downloadable file
            self.create_download_link(self.translated_text, download_filename)
            
            self.status_label.value = f"<b>Status:</b> 📥 Download ready for '{download_filename}'"
            
        except Exception as e:
            self.status_label.value = f"<b>Error:</b> ❌ Download failed: {str(e)}"
            
    def create_download_link(self, text_content, filename):
        """Create a download link for the translated text"""
        # Encode the text content
        b64_content = base64.b64encode(text_content.encode('utf-8')).decode()
        
        # Create attractive download link
        download_html = f"""
        <div style="margin-top: 15px; padding: 15px; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                    border-radius: 10px; text-align: center;">
            <p style="color: white; margin: 0 0 10px 0; font-weight: bold;">
                📥 Your Romanian translation is ready!
            </p>
            <a href="data:text/plain;charset=utf-8;base64,{b64_content}" 
               download="{filename}"
               style="background-color: white; color: #28a745; padding: 12px 24px; 
                      text-decoration: none; border-radius: 25px; display: inline-block;
                      font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                📄 Download {filename}
            </a>
        </div>
        """
        
        display(HTML(download_html))
        
    def display(self):
        """Display the app"""
        display(self.main_layout)

# Create and run the app
def run_translator_app():
    """Initialize and run the English to Romanian translator app"""
    print("🇬🇧 ➡️ 🇷🇴 English to Romanian Translator")
    print("=" * 50)
    print("Required packages:")
    print("- pip install ipywidgets googletrans==3.1.0a0")
    print("- For Jupyter: jupyter nbextension enable --py widgetsnbextension")
    print("=" * 50)
    
    app = EnglishToRomanianTranslator()
    app.display()
    return app

# Run the app
if __name__ == "__main__":
    app = run_translator_app()