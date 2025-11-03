#!/bin/bash
# ============================================
# 🔄 AutopostPro Updater (Hybrid Edition)
# By Garfield STORE 
# ============================================

PROJECT_DIR="/root/autopostpro"
SERVICE_NAME="autopostpro"
BACKUP_DIR="/root/autopostpro/backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

echo "🚀 Memulai proses update AutopostPro..."
sleep 1

# === 1. Pastikan folder project ada ===
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Folder $PROJECT_DIR tidak ditemukan."
    echo "➡️ Pastikan kamu sudah menginstall bot terlebih dahulu."
    exit 1
fi

cd "$PROJECT_DIR"

# === 2. Backup MongoDB (jika tersedia) ===
echo "🗄️ Membuat backup MongoDB..."
mkdir -p "$BACKUP_DIR"

if command -v mongodump &> /dev/null; then
    mongodump --uri="$(grep MONGO_URI .env | cut -d '=' -f2)" --out "$BACKUP_DIR/backup_$DATE"
    echo "✅ Backup tersimpan di $BACKUP_DIR/backup_$DATE"
else
    echo "⚠️ Perintah mongodump tidak ditemukan. Lewati backup MongoDB."
fi

# === 3. Hapus backup lebih dari 7 hari ===
find "$BACKUP_DIR" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null
echo "🧹 Backup lama (>7 hari) dibersihkan."

# === 4. Hentikan service sementara ===
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "🛑 Menghentikan service $SERVICE_NAME..."
    systemctl stop "$SERVICE_NAME"
fi

# === 5. Tarik update dari Git ===
echo "📦 Menarik pembaruan dari GitHub..."
git reset --hard
git pull origin main || git pull

# === 6. Update dependencies Python ===
echo "📚 Memperbarui dependensi Python..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --upgrade
else
    echo "⚠️ File requirements.txt tidak ditemukan, dilewati."
fi

# === 7. Jalankan ulang service ===
echo "♻️ Menjalankan ulang service $SERVICE_NAME..."
systemctl daemon-reload
systemctl start "$SERVICE_NAME"
systemctl enable "$SERVICE_NAME"

# === 8. Cek status service ===
sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "✅ AutopostPro berhasil diperbarui dan dijalankan ulang!"
else
    echo "⚠️ Update selesai, tapi service belum aktif. Cek log dengan:"
    echo "   journalctl -u $SERVICE_NAME -f"
fi

echo ""
echo "✨ Selesai! AutopostPro sekarang pakai versi terbaru."
