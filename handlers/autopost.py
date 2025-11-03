from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
import os

mongo = MongoClient(os.getenv("MONGO_URL"))
db = mongo["FSubProBot"]
channels = db["channels"]
licenses = db["licenses"]

# --- REPOST OTOMATIS DARI CHANNEL SUMBER ---

@Client.on_message(filters.channel)
async def auto_repost(client, message: Message):
    # Ambil data channel dari database
    for data in channels.find():
        konten_channel = data.get("konten")
        share_channel = data.get("share")
        user_id = data.get("user_id")

        # Skip kalau channel konten tidak cocok
        if message.chat.username != konten_channel:
            continue

        # Cek lisensi user
        license_data = licenses.find_one({"user_id": user_id})
        if not license_data or not license_data.get("active", False):
            continue  # Skip user tanpa lisensi aktif

        try:
            # Repost berdasarkan tipe pesan
            if message.photo:
                await client.send_photo(
                    chat_id=f"@{share_channel}",
                    photo=message.photo.file_id,
                    caption=message.caption or ""
                )

            elif message.video:
                await client.send_video(
                    chat_id=f"@{share_channel}",
                    video=message.video.file_id,
                    caption=message.caption or ""
                )

            elif message.text:
                await client.send_message(
                    chat_id=f"@{share_channel}",
                    text=message.text
                )

            elif message.document:
                await client.send_document(
                    chat_id=f"@{share_channel}",
                    document=message.document.file_id,
                    caption=message.caption or ""
                )

            print(f"[AUTOPOST] Berhasil repost dari @{konten_channel} ke @{share_channel}")

        except Exception as e:
            print(f"[AUTOPOST ERROR] {e}")
