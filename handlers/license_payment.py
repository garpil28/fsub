from pyrogram import Client, filters

@Client.on_message(filters.command("sendproof") & filters.reply)
async def send_proof(client, message):
    if not message.reply_to_message.photo:
        return await message.reply_text("Reply ke foto bukti transfer.")
    proof_file_id = message.reply_to_message.photo.file_id
    user = message.from_user
    # Simpan ke database kamu
    print(f"Bukti dari {user.id}: {proof_file_id}")
    await message.reply_text("✅ Bukti sudah diterima, tunggu konfirmasi owner.")
