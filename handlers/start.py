from pyrogram import Client, filters

@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "Halo! 👋\n\n"
        "Saya bot autopost & wajib join.\n"
        "Gunakan /help untuk melihat menu bantuan."
    )
