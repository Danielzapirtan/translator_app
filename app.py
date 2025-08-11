#!/usr/bin/env python3
"""
LibreTranslate Text File Translator
Translates English text files to Romanian using a self-hosted LibreTranslate server.
"""

import argparse
import os
import sys
import requests
import json
from pathlib import Path
from typing import Optional


class LibreTranslateClient:
    """Client for interacting with LibreTranslate API."""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: Optional[str] = None):
        """
        Initialize the LibreTranslate client.
        
        Args:
            base_url: Base URL of the LibreTranslate server
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set up headers
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def check_server_status(self) -> bool:
        """Check if LibreTranslate server is accessible."""
        try:
            response = self.session.get(f"{self.base_url}/languages", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to LibreTranslate server: {e}")
            return False
    
    def get_available_languages(self) -> list:
        """Get list of available languages from the server."""
        try:
            response = self.session.get(f"{self.base_url}/languages", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching languages: {e}")
            return []
    
    def translate_text(self, text: str, source_lang: str = "en", target_lang: str = "ro") -> Optional[str]:
        """
        Translate text using LibreTranslate API.
        
        Args:
            text: Text to translate
            source_lang: Source language code (default: en)
            target_lang: Target language code (default: ro)
            
        Returns:
            Translated text or None if translation failed
        """
        if not text.strip():
            return text
        
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/translate",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("translatedText", "")
            
        except requests.exceptions.RequestException as e:
            print(f"Error during translation: {e}")
            return None
        except json.JSONDecodeError:
            print("Error parsing translation response")
            return None


def read_text_file(file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """Read text file with specified encoding."""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encodings if UTF-8 fails
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                    print(f"Warning: File read with {enc} encoding instead of {encoding}")
                    return content
            except UnicodeDecodeError:
                continue
        print(f"Error: Could not read file {file_path} with any supported encoding")
        return None
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def write_text_file(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
    """Write text to file with specified encoding."""
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        return False


def translate_file(client: LibreTranslateClient, input_file: Path, output_file: Path, 
                  chunk_size: int = 1000) -> bool:
    """
    Translate a text file from English to Romanian.
    
    Args:
        client: LibreTranslate client instance
        input_file: Path to input file
        output_file: Path to output file
        chunk_size: Maximum characters per translation request
        
    Returns:
        True if successful, False otherwise
    """
    print(f"Reading file: {input_file}")
    content = read_text_file(input_file)
    
    if content is None:
        return False
    
    if not content.strip():
        print("Warning: Input file is empty")
        return write_text_file(output_file, content)
    
    print(f"Translating {len(content)} characters...")
    
    # Split content into chunks for better translation quality and API limits
    chunks = []
    lines = content.split('\n')
    current_chunk = ""
    
    for line in lines:
        if len(current_chunk) + len(line) + 1 <= chunk_size:
            if current_chunk:
                current_chunk += '\n'
            current_chunk += line
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line
    
    if current_chunk:
        chunks.append(current_chunk)
    
    print(f"Processing {len(chunks)} chunks...")
    
    translated_chunks = []
    for i, chunk in enumerate(chunks, 1):
        print(f"Translating chunk {i}/{len(chunks)}...")
        
        translated_chunk = client.translate_text(chunk)
        if translated_chunk is None:
            print(f"Failed to translate chunk {i}")
            return False
        
        translated_chunks.append(translated_chunk)
    
    # Combine translated chunks
    translated_content = '\n'.join(translated_chunks)
    
    print(f"Writing translated content to: {output_file}")
    return write_text_file(output_file, translated_content)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Translate English text files to Romanian using LibreTranslate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py input.txt -o output.txt
  python app.py input.txt --server http://192.168.1.100:5000
  python app.py input.txt --api-key YOUR_API_KEY --chunk-size 500
  python app.py input.txt --list-languages
        """
    )
    
    parser.add_argument('input_file', type=str, help='Input text file to translate')
    parser.add_argument('-o', '--output', type=str, help='Output file path (default: input_file_ro.txt)')
    parser.add_argument('-s', '--server', type=str, default='http://localhost:5000',
                       help='LibreTranslate server URL (default: http://localhost:5000)')
    parser.add_argument('-k', '--api-key', type=str, help='API key for authentication')
    parser.add_argument('-c', '--chunk-size', type=int, default=1000,
                       help='Maximum characters per translation request (default: 1000)')
    parser.add_argument('--list-languages', action='store_true',
                       help='List available languages and exit')
    parser.add_argument('--encoding', type=str, default='utf-8',
                       help='File encoding (default: utf-8)')
    
    args = parser.parse_args()
    
    # Initialize client
    client = LibreTranslateClient(base_url=args.server, api_key=args.api_key)
    
    # Check server connectivity
    print(f"Connecting to LibreTranslate server at {args.server}...")
    if not client.check_server_status():
        print("Error: Cannot connect to LibreTranslate server")
        print("Make sure the server is running and accessible")
        return 1
    
    print("✓ Connected to LibreTranslate server")
    
    # List languages if requested
    if args.list_languages:
        languages = client.get_available_languages()
        if languages:
            print("\nAvailable languages:")
            for lang in languages:
                print(f"  {lang['code']}: {lang['name']}")
        return 0
    
    # Validate input file
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist")
        return 1
    
    if not input_path.is_file():
        print(f"Error: {input_path} is not a file")
        return 1
    
    # Determine output file path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_name(f"{input_path.stem}_ro{input_path.suffix}")
    
    # Check if output file already exists
    if output_path.exists():
        response = input(f"Output file {output_path} already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Translation cancelled")
            return 0
    
    # Verify Romanian language support
    languages = client.get_available_languages()
    if languages:
        lang_codes = [lang['code'] for lang in languages]
        if 'en' not in lang_codes:
            print("Warning: English (en) not found in supported languages")
        if 'ro' not in lang_codes:
            print("Error: Romanian (ro) not supported by this LibreTranslate instance")
            print("Available languages:", ', '.join(lang_codes))
            return 1
    
    # Perform translation
    success = translate_file(client, input_path, output_path, args.chunk_size)
    
    if success:
        print(f"✓ Translation completed successfully!")
        print(f"Translated file saved as: {output_path}")
        return 0
    else:
        print("✗ Translation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())