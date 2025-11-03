# main.py
# Telegram FSUB Autopost Bot Professional Edition
# By Garfield Fsub

import asyncio
import logging
import os
from dotenv import load_dotenv
from pyrogram import Client
from utils.db import db
from services.license import LicenseManager

# === Logging setup ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# === Load environment variables ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")  # optional log grup ID

if not all([BOT_TOKEN, API_ID, API_HASH, MONGO_URI]):
    raise SystemExit("❌ Gagal start — Pastikan .env lengkap dan benar!")

# === Inisialisasi Pyrogram Client ===
bot = Client(
    "autopostpro_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,
    plugins=dict(root="handlers")
)

license_manager = LicenseManager()

# === Background Task: auto deactivate expired licenses ===
async def auto_license_checker():
    """Loop background untuk menonaktifkan lisensi kadaluarsa"""
    while True:
        try:
            await license_manager.deactivate_expired_licenses()
        except Exception as e:
            logging.error(f"Gagal menjalankan auto license check: {e}")
        await asyncio.sleep(3600)  # cek setiap 1 jam

# === Startup Function ===
async def startup():
    logging.info("🔁 Menghubungkan ke Mongo Atlas...")
    await db.connect(MONGO_URI)
    await license_manager.init_collection()
    logging.info("✅ MongoDB Atlas Connected.")
    await db.add_owner(OWNER_ID)
    logging.info("👑 Owner terdaftar: %s", OWNER_ID)

    try:
        await bot.send_message(
            OWNER_ID,
            "🚀 **AutopostPro Bot aktif!**\nSemua sistem sudah terkoneksi.\nGunakan /help untuk melihat perintah."
        )
    except Exception as e:
        logging.warning(f"Gagal kirim notifikasi owner: {e}")

    if LOG_GROUP_ID:
        try:
            await bot.send_message(
                int(LOG_GROUP_ID),
                "📋 [LOG] Bot berhasil diaktifkan dan terkoneksi ke database Mongo."
            )
        except Exception as e:
            logging.warning(f"Gagal kirim log ke grup: {e}")

# === Main Runner ===
async def main():
    await startup()
    asyncio.create_task(auto_license_checker())
    logging.info("🤖 Bot siap menerima pesan.")
    await bot.start()
    await asyncio.Event().wait()  # biar bot jalan 24 jam nonstop

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.warning("🛑 Bot dimatikan oleh user.")
