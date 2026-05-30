#!/usr/bin/env bash
# =====================================================
#  Shopee Tools Bot - One-Command Runner (Linux/macOS)
#  Cara pakai:
#    ./run.sh                 -> jalankan bot (pakai token di .env)
#    ./run.sh <BOT_TOKEN>     -> set token sekali, lalu jalankan
# =====================================================
set -e

# Pindah ke folder script ini
cd "$(dirname "$0")"

# 1. Cari interpreter python
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "❌ Python tidak ditemukan. Install Python 3.10+ dulu: https://www.python.org/downloads/"
  exit 1
fi
echo "✅ Menggunakan $($PY --version)"

# 2. Buat virtual environment kalau belum ada
if [ ! -d ".venv" ]; then
  echo "📦 Membuat virtual environment (.venv)..."
  "$PY" -m venv .venv
fi

# 3. Aktifkan venv
# shellcheck disable=SC1091
source .venv/bin/activate

# 4. Install dependencies
echo "📥 Menginstall dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "✅ Dependencies siap."

# 5. Siapkan file .env
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "📝 File .env dibuat dari template."
fi

# 6. Kalau token dikirim sebagai argumen, tulis ke .env
if [ -n "$1" ]; then
  if grep -q '^BOT_TOKEN=' .env; then
    # ganti baris BOT_TOKEN
    sed -i.bak "s|^BOT_TOKEN=.*|BOT_TOKEN=$1|" .env && rm -f .env.bak
  else
    echo "BOT_TOKEN=$1" >> .env
  fi
  echo "🔐 BOT_TOKEN tersimpan di .env."
fi

# 7. Cek token sudah diisi
if ! grep -q '^BOT_TOKEN=.\+' .env || grep -q '^BOT_TOKEN=your_telegram_bot_token_here' .env; then
  echo ""
  echo "⚠️  BOT_TOKEN belum diisi!"
  echo "   Jalankan: ./run.sh <TOKEN_DARI_BOTFATHER>"
  echo "   atau edit file .env secara manual."
  exit 1
fi

# 8. Jalankan bot
echo "🚀 Menjalankan Shopee Tools Bot..."
echo "   (Tekan Ctrl+C untuk berhenti)"
echo ""
python bot.py
