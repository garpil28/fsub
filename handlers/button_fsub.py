from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

JOIN_CHANNELS = ["@contoh1", "@contoh2"]

@Client.on_message(filters.command("checkjoin"))
async def check_join(client, message):
    not_joined = []
    for ch in JOIN_CHANNELS:
        try:
            member = await client.get_chat_member(ch, message.from_user.id)
            if member.status not in ("member", "administrator", "creator"):
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    if not_joined:
        buttons = [[InlineKeyboardButton(f"Gabung {ch}", url=f"https://t.me/{ch[1:]}")] for ch in not_joined]
        await message.reply_text(
            "⚠️ Kamu harus join semua channel berikut dulu:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply_text("✅ Kamu sudah join semua channel wajib.")
