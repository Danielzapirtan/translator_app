#!/usr/bin/env python3
"""
English-to-Romanian File Translator
Uses LibreTranslate's public API (no Docker required)
"""

import os
import requests
from pathlib import Path

# Configuration
LIBRETRANSLATE_URL = "https://libretranslate.com"
SOURCE_LANG = "en"
TARGET_LANG = "ro"
MAX_CHARS = 5000  # LibreTranslate public API limit

def translate_text(text: str) -> str:
    """Translate text using LibreTranslate API"""
    endpoint = f"{LIBRETRANSLATE_URL}/translate"
    payload = {
        "q": text,
        "source": SOURCE_LANG,
        "target": TARGET_LANG,
        "format": "text"
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        return response.json().get("translatedText", "Translation failed")
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

def process_file(input_path: str, output_path: str) -> None:
    """Handle file translation workflow"""
    try:
        # Read input
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        if not text:
            raise ValueError("File is empty")
        
        # Check length limit
        if len(text) > MAX_CHARS:
            raise ValueError(f"Text exceeds {MAX_CHARS} character limit")
        
        # Translate
        print(f"Translating {len(text)} characters...")
        translated = translate_text(text)
        
        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        
        print(f"Success! Translation saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("English to Romanian Text Translator")
    print("----------------------------------")
    
    # Get file paths
    input_file = input("Enter input file path: ").strip()
    output_file = f"translated_{Path(input_file).name}"
    
    # Run translation
    process_file(input_file, output_file)

if __name__ == "__main__":
    main()
