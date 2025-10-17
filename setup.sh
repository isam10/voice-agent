#!/bin/bash

# Setup Script for Voice Assistant (Linux/Mac)
# Run this script to set up the development environment

echo "================================"
echo "Voice Assistant Setup Script"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Check .env file
echo ""
echo "Checking .env configuration..."

if [ -f .env ]; then
    echo "✓ .env file found"
    echo ""
    echo "IMPORTANT: Please update the following values in .env file:"
    echo "  - OPENAI_API_KEY"
    echo "  - TWILIO_ACCOUNT_SID"
    echo "  - TWILIO_AUTH_TOKEN"
    echo "  - TWILIO_PHONE_NUMBER"
    echo "  - SERVER_URL"
else
    echo "✗ .env file not found!"
    exit 1
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update .env file with your credentials"
echo "2. For local development, run: ngrok http 8000"
echo "3. Update SERVER_URL in .env with ngrok URL (without https://)"
echo "4. Configure Twilio webhook: https://YOUR_NGROK_URL/incoming-call"
echo "5. Start the server: python app.py"
echo ""
echo "For more information, see README.md"
echo ""
