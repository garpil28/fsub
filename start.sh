#!/bin/bash
# ====================================================
# Start Script - AutopostPro Telegram Bot
# ====================================================

echo "🚀 Starting AutopostPro Bot..."

# --- Ganti ke direktori project ---
cd "$(dirname "$0")"

# --- Cek & aktifkan virtual environment ---
if [ -d "venv" ]; then
  echo "🔹 Virtual environment ditemukan. Mengaktifkan..."
  source venv/bin/activate
else
  echo "⚙️ Membuat virtual environment baru..."
  python3 -m venv venv
  source venv/bin/activate
fi

# --- Install dependencies jika belum ada ---
echo "📦 Mengecek dependencies..."
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1

# --- Jalankan bot ---
echo "🤖 Menjalankan bot (autostart mode)..."
while true; do
  python3 main.py
  echo "❗ Bot crash atau dihentikan. Restart dalam 5 detik..."
  sleep 5
done
