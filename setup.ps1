# Setup Script for Voice Assistant
# Run this script to set up the development environment

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Voice Assistant Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check .env file
Write-Host ""
Write-Host "Checking .env configuration..." -ForegroundColor Yellow

if (Test-Path .env) {
    Write-Host "✓ .env file found" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Please update the following values in .env file:" -ForegroundColor Cyan
    Write-Host "  - OPENAI_API_KEY" -ForegroundColor White
    Write-Host "  - TWILIO_ACCOUNT_SID" -ForegroundColor White
    Write-Host "  - TWILIO_AUTH_TOKEN" -ForegroundColor White
    Write-Host "  - TWILIO_PHONE_NUMBER" -ForegroundColor White
    Write-Host "  - SERVER_URL" -ForegroundColor White
} else {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update .env file with your credentials" -ForegroundColor White
Write-Host "2. For local development, run: ngrok http 8000" -ForegroundColor White
Write-Host "3. Update SERVER_URL in .env with ngrok URL (without https://)" -ForegroundColor White
Write-Host "4. Configure Twilio webhook: https://YOUR_NGROK_URL/incoming-call" -ForegroundColor White
Write-Host "5. Start the server: python app.py" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Yellow
Write-Host ""
