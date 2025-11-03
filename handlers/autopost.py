from pyrogram import Client, filters

@Client.on_message(filters.channel)
async def auto_forward(client, message):
    # Channel ID sumber
    source_id = message.chat.id

    # Misal ambil dari database Mongo:
    # doc = db.channels.find_one({'source_id': source_id})
    # if not doc: return  # tidak termasuk daftar channel yang diawasi

    # Contoh: kirim ulang ke channel tujuan
    target_chat_id = -100123456789  # ganti dengan ID channel kamu
    try:
        await message.copy(target_chat_id)
    except Exception as e:
        print(f"Gagal forward: {e}")
