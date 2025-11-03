#!/bin/bash
# ============================================
# 🧩 AutopostPro Telegram Bot Uninstaller
# By Garfield STORE 
# ============================================

echo "⚠️ Proses uninstall AutopostPro dimulai..."
sleep 1

# === 1. Hentikan service jika aktif ===
if systemctl is-active --quiet autopostpro; then
    echo "🛑 Menghentikan service autopostpro..."
    systemctl stop autopostpro
fi

# === 2. Hapus service systemd ===
if [ -f "/etc/systemd/system/autopostpro.service" ]; then
    echo "🧹 Menghapus file service systemd..."
    systemctl disable autopostpro
    rm -f /etc/systemd/system/autopostpro.service
    systemctl daemon-reload
fi

# === 3. Hapus folder project ===
if [ -d "/root/autopostpro" ]; then
    echo "🧺 Menghapus direktori /root/autopostpro..."
    rm -rf /root/autopostpro
fi

# === 4. Bersihkan cache python ===
echo "🧼 Membersihkan cache Python..."
find /root -type d -name "__pycache__" -exec rm -rf {} +

# === 5. Konfirmasi ===
echo ""
echo "✅ AutopostPro berhasil dihapus sepenuhnya."
echo "💡 Jika ingin reinstall, jalankan lagi: bash autoinstall.sh"
