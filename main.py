# main.py
# Telegram FSUB Autopost Bot Professional Edition
# By Garfield Fsub

import asyncio
import logging
import os
from dotenv import load_dotenv
from pyrogram import Client
from utils.db import db

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
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "0"))  # Grup log ID

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

# === Kirim log ke grup ===
async def send_log(text: str):
    """Kirim log ke grup log jika diset."""
    if LOG_GROUP_ID != 0:
        try:
            await bot.send_message(LOG_GROUP_ID, f"🧾 *LOG SYSTEM:*\n{text}")
        except Exception as e:
            logging.warning(f"Gagal kirim log ke grup: {e}")

# === Startup Function ===
async def startup():
    logging.info("🔁 Menghubungkan ke Mongo Atlas...")
    await db.connect(MONGO_URI)

    logging.info("✅ MongoDB Atlas Connected.")
    await db.add_owner(OWNER_ID)
    logging.info("👑 Owner terdaftar: %s", OWNER_ID)

    # Notifikasi ke owner
    try:
        await bot.send_message(
            OWNER_ID,
            "🚀 **AutopostPro Bot aktif!**\nSemua sistem sudah terkoneksi.\nGunakan /help untuk melihat perintah."
        )
    except Exception as e:
        logging.warning(f"Gagal kirim notifikasi owner: {e}")

    await send_log("✅ Bot AutopostPro berhasil aktif dan siap digunakan.")

# === Main Runner ===
async def main():
    await startup()
    logging.info("🤖 Bot siap menerima pesan.")
    await bot.start()
    await asyncio.Event().wait()  # keep running

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.warning("🛑 Bot dimatikan oleh user.")
