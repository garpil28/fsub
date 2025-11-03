#!/bin/bash
# ============================================
# Autoinstall Script for AutopostPro Bot
# By Garfield Dev Team
# ============================================

set -e

echo "🚀 Memulai instalasi AutopostPro..."

# --- Update System ---
apt update -y && apt upgrade -y

# --- Install Dependensi Utama ---
apt install -y python3 python3-pip git curl

# --- Clone Repo ---
if [ ! -d "/root/autopostpro" ]; then
    git clone https://github.com/username/autopostpro.git /root/autopostpro
else
    echo "📦 Folder sudah ada, skip clone..."
fi

cd /root/autopostpro

# --- Install Requirements ---
pip3 install --upgrade pip
pip3 install -r requirements.txt

# --- Setup .env jika belum ada ---
if [ ! -f ".env" ]; then
    echo "📝 Membuat file .env baru..."
    cat <<EOF > .env
BOT_TOKEN=ISI_TOKEN_BOT
API_ID=ISI_API_ID
API_HASH=ISI_API_HASH
MONGO_URI=ISI_MONGO_ATLAS
OWNER_ID=ISI_ID_OWNER
LOG_CHANNEL=ISI_ID_LOG_CHANNEL
PAYMENT_QR=https://files.catbox.moe/tq9d36.jpg
EOF
else
    echo "✅ File .env sudah ada, skip..."
fi

# --- Buat start.sh ---
echo "⚙️ Membuat start.sh..."
cat <<'EOL' > start.sh
#!/bin/bash
echo "🚀 Menjalankan AutopostPro Bot..."
python3 main.py
EOL
chmod +x start.sh

# --- Buat Systemd Service ---
echo "🧩 Membuat service systemd..."
cat <<'EOL' > /etc/systemd/system/autopostpro.service
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
EOL

# --- Reload dan Enable Service ---
systemctl daemon-reload
systemctl enable autopostpro
systemctl restart autopostpro

echo "✅ Instalasi selesai!"
echo "📡 Cek status bot dengan: systemctl status autopostpro"
echo "📜 Log bot: journalctl -fu autopostpro"
