import logging
import asyncio
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI, OWNER_ID
from utils.database import db
from utils.logger import setup_logger

# setup logging
setup_logger()

logging.info("🚀 Starting Bot...")

# inisialisasi client pyrogram
app = Client(
    "AutoPostProBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="handlers")
)

# fungsi saat bot siap
@app.on_started
async def on_start(client):
    logging.info("✅ Bot sudah aktif dan tersambung ke Telegram.")
    await db.connect(MONGO_URI)
    await db.add_owner(OWNER_ID)
    await client.send_message(OWNER_ID, "🤖 Bot berhasil diaktifkan!\nGunakan /help untuk melihat menu lengkap.")
    logging.info("📦 Database Mongo Atlas sudah siap digunakan.")

async def main():
    await app.start()
    logging.info("📲 Bot sedang berjalan, tekan Ctrl+C untuk stop.")
    await idle()
    await app.stop()
    logging.info("🛑 Bot berhenti dengan aman.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🧹 Proses dihentikan manual.")
