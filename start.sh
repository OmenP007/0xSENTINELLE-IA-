#!/bin/bash
# ─────────────────────────────────────────────────────
#  0xSentinelle IA — Script de démarrage v2.0
#  Lance backend FastAPI + frontend React Vite
# ─────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "  ██████╗ ██╗  ██╗███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     ██╗     ███████╗"
echo "  0xSentinelle IA — v2.0 — Démarrage..."
echo ""

# ── Vérification .env ──────────────────────────────────
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo "⚠️  Fichier .env manquant. Copie depuis .env.example..."
  cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
  echo "📝 Configurez votre GEMINI_API_KEY dans .env"
fi

# ── Backend FastAPI ────────────────────────────────────
echo "🚀 Démarrage du backend FastAPI..."
cd "$SCRIPT_DIR/backend"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend lancé (PID: $BACKEND_PID) → http://localhost:8000"

# ── Frontend React ─────────────────────────────────────
echo "⚛️  Démarrage du frontend React..."
cd "$SCRIPT_DIR/frontend-react"
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend lancé (PID: $FRONTEND_PID) → http://localhost:3000"

# ── Bot Telegram ───────────────────────────────────────
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
  echo "🤖 Démarrage du Bot Telegram 0xSentinelle..."
  python3 "$SCRIPT_DIR/backend/telegram_bot.py" &
  TELEGRAM_PID=$!
  echo "✅ Bot Telegram lancé (PID: $TELEGRAM_PID) → @deadbeef225bot"
fi

echo ""
echo "────────────────────────────────────────────────────"
echo "  🌐 Frontend React : http://localhost:3000"
echo "  🔧 API Backend    : http://localhost:8000"
echo "  🤖 Bot Telegram   : @deadbeef225bot"
echo "  📖 API Docs       : http://localhost:8000/docs"
echo "────────────────────────────────────────────────────"
echo "  Ctrl+C pour arrêter"
echo ""

# ── Cleanup on exit ────────────────────────────────────
trap "echo ''; echo 'Arrêt...'; kill $BACKEND_PID $FRONTEND_PID $TELEGRAM_PID 2>/dev/null; echo 'Bye! 👋'" EXIT

wait
