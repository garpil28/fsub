#!/bin/bash
# ============================================
# 🧩 AutopostPro Telegram Bot Auto Installer
# By Garfield STORE / Lusiana Kurniawati
# ============================================

set -e

echo "🚀 Memulai instalasi AutopostPro..."
sleep 2

# === 1. Update sistem dan install dependensi dasar ===
echo "📦 Menginstal dependensi sistem..."
apt update -y && apt upgrade -y
apt install -y python3 python3-pip git curl

# === 2. Clone repo (hapus versi lama jika ada) ===
cd /root
if [ -d "autopostpro" ]; then
    echo "🧹 Menghapus instalasi lama..."
    rm -rf autopostpro
fi

echo "📥 Meng-clone repository AutopostPro..."
read -p "Masukkan URL repo GitHub kamu (contoh: https://github.com/user/autopostpro): " REPO_URL
git clone "$REPO_URL" autopostpro

cd autopostpro

# === 3. Instal requirements ===
echo "⚙️ Menginstal library Python..."
pip install --upgrade pip
pip install -r requirements.txt

# === 4. Buat file .env otomatis ===
echo "🧾 Membuat file konfigurasi (.env)..."
read -p "BOT_TOKEN: " BOT_TOKEN
read -p "API_ID: " API_ID
read -p "API_HASH: " API_HASH
read -p "OWNER_ID (ID Telegram kamu): " OWNER_ID
read -p "LOG_CHANNEL ID (misal -100xxxx): " LOG_CHANNEL
read -p "MONGO_URI (MongoDB Atlas): " MONGO_URI

cat <<EOF > .env
BOT_TOKEN=$BOT_TOKEN
API_ID=$API_ID
API_HASH=$API_HASH
OWNER_ID=$OWNER_ID
LOG_CHANNEL=$LOG_CHANNEL
MONGO_URI=$MONGO_URI
QR_PAYMENT_URL=https://files.catbox.moe/tq9d36.jpg
EOF

echo "✅ File .env berhasil dibuat."

# === 5. Buat start.sh ===
cat <<'EOF' > start.sh
#!/bin/bash
cd /root/autopostpro
python3 main.py
EOF

chmod +x start.sh
echo "✅ File start.sh dibuat & bisa dijalankan."

# === 6. Buat service systemd ===
SERVICE_PATH="/etc/systemd/system/autopostpro.service"

cat <<EOF > $SERVICE_PATH
[Unit]
Description=AutopostPro Telegram Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/root/autopostpro
ExecStart=/bin/bash /root/autopostpro/start.sh
Restart=on-failure
RestartSec=5
StartLimitBurst=5
StartLimitInterval=60
User=root
Environment="PYTHONUNBUFFERED=1"
Environment="TZ=Asia/Jakarta"

[Install]
WantedBy=multi-user.target
EOF

# === 7. Aktifkan service ===
systemctl daemon-reload
systemctl enable autopostpro
systemctl restart autopostpro

echo ""
echo "✅ Instalasi selesai!"
echo "💡 Bot kamu sekarang aktif & otomatis nyala ulang saat VPS restart."
echo "🔍 Cek status dengan: systemctl status autopostpro"
echo "📜 Lihat log real-time: journalctl -fu autopostpro"
