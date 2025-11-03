#!/bin/bash
# ============================================
# 🔄 AutopostPro Updater
# By Garfield STORE / Lusiana Kurniawati
# ============================================

echo "🚀 Memulai proses update AutopostPro..."
sleep 1

# === 1. Masuk ke folder project ===
if [ ! -d "/root/autopostpro" ]; then
    echo "❌ Folder /root/autopostpro tidak ditemukan."
    echo "➡️ Pastikan kamu sudah install bot terlebih dahulu."
    exit 1
fi

cd /root/autopostpro

# === 2. Hentikan service sementara ===
if systemctl is-active --quiet autopostpro; then
    echo "🛑 Menghentikan service autopostpro..."
    systemctl stop autopostpro
fi

# === 3. Ambil update terbaru dari Git ===
echo "📦 Menarik pembaruan dari GitHub..."
git reset --hard
git pull origin main || git pull

# === 4. Update dependencies Python ===
echo "📚 Memperbarui dependensi Python..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --upgrade
else
    echo "⚠️ File requirements.txt tidak ditemukan, dilewati."
fi

# === 5. Restart service ===
echo "♻️ Menjalankan ulang service autopostpro..."
systemctl daemon-reload
systemctl start autopostpro
systemctl enable autopostpro

# === 6. Cek status ===
sleep 2
if systemctl is-active --quiet autopostpro; then
    echo "✅ AutopostPro berhasil diperbarui dan dijalankan ulang!"
else
    echo "⚠️ Update selesai, tapi service belum aktif. Cek log dengan:"
    echo "   journalctl -u autopostpro -f"
fi

echo ""
echo "✨ Selesai! AutopostPro sudah pakai versi terbaru."
