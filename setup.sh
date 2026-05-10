#!/bin/bash
# KitchenOS-AI — Full Setup Script for CachyOS (Arch-based)
# Run: chmod +x setup.sh && ./setup.sh

set -e

echo "🍳 KitchenOS-AI Setup — CachyOS"
echo "================================"

# 1. System dependencies
echo "[1/6] Installing system packages..."
sudo pacman -S --needed --noconfirm python python-pip tesseract tesseract-data-eng opencv pango gdk-pixbuf2 nodejs npm

# 2. Python virtual environment
echo "[2/6] Creating Python venv..."
cd ~/Downloads/CHATBOT/kitchenos-ai
python -m venv venv
source venv/bin/activate

# 3. Python dependencies
echo "[3/6] Installing Python packages..."
pip install -r requirements.txt

# 4. Playwright browser
echo "[4/6] Installing Playwright Chromium..."
playwright install chromium

# 5. Web dashboard dependencies
echo "[5/6] Installing Node.js packages..."
cd web
npm install
cd ..

# 6. Create .env if not exists
echo "[6/6] Setting up .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  EDIT .env SEKARANG — masukkan API key kamu:"
    echo "   nano ~/Downloads/CHATBOT/kitchenos-ai/.env"
    echo ""
fi

echo ""
echo "✅ Setup selesai!"
echo ""
echo "Jalankan sistem dengan:"
echo "  cd ~/Downloads/CHATBOT/kitchenos-ai"
echo "  source venv/bin/activate"
echo ""
echo "  # Terminal 1: Backend"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  # Terminal 2: Telegram Bot"
echo "  python telegram_bot.py"
echo ""
echo "  # Terminal 3: Web Dashboard"
echo "  cd web && npm run dev"
