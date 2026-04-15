#!/bin/bash
# ============================================================
#  🏛️ RAG-Destroyer — INDUSTRIAL ONE-CLICK LAUNCHER
#  Double-click this file to start the GURU in the box.
# ============================================================

cd "$(dirname "$0")"

clear
echo "╔══════════════════════════════════════════════════════╗"
echo "║       🏛️  RAG-Destroyer: Zero-Vector-DB             ║"
echo "║       Role: GURU in the box                         ║"
echo "║       Controlled by: RAG Slayer                     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 1. Aggressive Zombie Cleanup
echo "🧹 Cleaning up old ghost processes..."
pkill -9 -f app.py 2>/dev/null
pkill -9 -f Monitor.py 2>/dev/null

# 2. Create log directory if missing
mkdir -p logs

# 3. Start Detached Background Service
echo "🚀 Launching GURU in the box (Streamlit Dashboard)..."
nohup python3 -m streamlit run app.py --server.headless true --browser.gatherUsageStats false > logs/system_service.log 2>&1 &
BG_PID=$!

echo "✅ GURU is now ON DUTY (PID: $BG_PID)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 The system will stay active even if you close this window."
echo "📁 Monitoring local storage in real-time."
echo "🔴 To STOP the system: pkill -f app.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Viewing Live Logs (Press Ctrl+C to exit log view):"
echo ""
sleep 3
tail -f logs/system_service.log
