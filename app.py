#!/usr/bin/env python3
"""
LibreTranslate English-to-Romanian Translator on Google Colab
- Self-hosts LibreTranslate in Docker
- Translates uploaded .txt files
- Saves translations to new files
"""

import os
import time
import requests
from IPython.display import clear_output

def install_and_launch_libretranslate():
    """Install Docker and launch LibreTranslate container"""
    print("⚙️ Setting up LibreTranslate server...")
    
    # Install Docker
    !sudo apt-get update -qq > /dev/null
    !sudo apt-get install -y -qq docker.io > /dev/null
    !sudo systemctl start docker
    
    # Launch LibreTranslate
    !sudo docker pull -q libretranslate/libretranslate
    !sudo docker run -d -p 5000:5000 libretranslate/libretranslate --free-api > /dev/null
    
    # Wait for server to start
    time.sleep(10)
    clear_output()
    print("✅ LibreTranslate server is running at http://localhost:5000")

def translate_text(text, source_lang="en", target_lang="ro"):
    """Translate text using local LibreTranslate API"""
    url = "http://localhost:5000/translate"
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }
    try:
        response = requests.post(url, json=payload).json()
        return response.get("translatedText", "Translation failed")
    except:
        return "Error connecting to translation server"

def process_files():
    """Main workflow: file selection and translation"""
    print("\n📝 English to Romanian Text File Translator")
    print("----------------------------------------")
    
    # Get input file (Colab uploads to /content/)
    input_path = input("Enter English text filename (e.g., 'my_text.txt'): ").strip()
    if not os.path.exists(input_path):
        print(f"❌ Error: File '{input_path}' not found in /content/")
        print("Please upload your file first using Colab's file explorer")
        return
    
    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        english_text = f.read()
    
    if not english_text.strip():
        print("❌ Error: File is empty")
        return
    
    print(f"\n🔤 Original text ({len(english_text)} chars):")
    print("----------------------------------------")
    print(english_text[:200] + ("..." if len(english_text) > 200 else ""))
    
    # Translate
    print("\n🔄 Translating to Romanian...")
    romanian_text = translate_text(english_text)
    
    # Save output
    output_path = f"translated_{os.path.basename(input_path)}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(romanian_text)
    
    print(f"\n✅ Translation saved to: {output_path}")
    print("----------------------------------------")
    print(romanian_text[:200] + ("..." if len(romanian_text) > 200 else ""))

# Main execution
if __name__ == "__main__":
    install_and_launch_libretranslate()
    process_files()
