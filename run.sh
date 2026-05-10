#!/bin/bash
# ============================================
# KitchenOS-AI — One-click startup script
# Run:  ./run.sh
# Stop: ./run.sh stop
# ============================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# --- Stop command ---
if [ "$1" = "stop" ]; then
    echo "Stopping KitchenOS-AI..."
    pkill -f "uvicorn main:app" 2>/dev/null
    pkill -f "telegram_bot.py" 2>/dev/null
    pkill -f "next dev" 2>/dev/null
    echo "✅ All services stopped."
    exit 0
fi

echo ""
echo "🍳 =================================="
echo "   KitchenOS-AI — Starting Up"
echo "🍳 =================================="
echo ""

# --- 1. Activate venv ---
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# --- 2. Install Python dependencies ---
echo "[1/5] Installing Python dependencies..."
pip install -q -r requirements.txt 2>/dev/null
echo "✅ Python dependencies ready"

# --- 3. Seed RAG knowledge base ---
echo "[2/5] Seeding RAG knowledge base..."
python seed_knowledge.py
echo "✅ RAG knowledge base ready"

# --- 4. Start Backend ---
echo "[3/5] Starting FastAPI backend on port 8080..."
uvicorn main:app --host 0.0.0.0 --port 8080 &
BACKEND_PID=$!

# Wait for backend to be ready (retry up to 10 seconds)
echo "    Waiting for backend..."
for i in $(seq 1 10); do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Backend API      → http://localhost:8080"
        echo "   Swagger Docs     → http://localhost:8080/docs"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "❌ Backend failed to start. Check errors above."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# --- 5. Start Frontend ---
echo "[4/5] Starting Next.js frontend on port 3030..."
cd web
if [ ! -d "node_modules" ]; then
    npm install --silent 2>/dev/null
fi
npm run dev &
FRONTEND_PID=$!
cd "$PROJECT_DIR"
sleep 3
echo "✅ Web Frontend     → http://localhost:3030"

# --- 6. Start Telegram Bot (optional) ---
if grep -q "TELEGRAM_BOT_TOKEN=" .env 2>/dev/null && ! grep -q "TELEGRAM_BOT_TOKEN=your-" .env 2>/dev/null; then
    echo "[5/5] Starting Telegram Bot..."
    python telegram_bot.py &
    echo "✅ Telegram Bot     → running"
else
    echo "[5/5] Telegram Bot  → skipped (no token configured)"
fi

echo ""
echo "🍳 =================================="
echo "   All services running!"
echo "🍳 =================================="
echo ""
echo "   Web UI:   http://localhost:3030"
echo "   API:      http://localhost:8080"
echo "   Docs:     http://localhost:8080/docs"
echo ""
echo "   Stop all: ./run.sh stop"
echo "   Or press Ctrl+C"
echo ""

# Keep script alive
wait
