#!/bin/bash
set -e  # Exit on any error

echo "Installing translator_app..."

cd $HOME

# Update and install dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y git python3-pip

# Clone repository
echo "📥 Downloading translation_app..."
if [ -d "translator_app" ]; then
    echo "⚠️  translator_app directory exists, removing old version..."
    rm -rf translator_app
fi
git clone https://github.com/Danielzapirtan/translator_app.git

cd translator_app

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

# Start the application
echo "🚀 Starting translator app..."
python3 translator_app.py &>/dev/null &

# Give it a moment to start
sleep 3

echo ""
echo "✅ Installation complete!"
echo "🌐 Visit http://localhost:7860 in your browser"
echo "💡 To restart later, run: cd ~/translator_app && python3 translator_app.py &"