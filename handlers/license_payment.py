from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

mongo = MongoClient(os.getenv("MONGO_URL"))
db = mongo["FSubProBot"]
licenses = db["licenses"]
payments = db["payments"]

OWNER_ID = int(os.getenv("OWNER_ID"))
DANA_NUMBER = "081219623569"
OWNER_NAME = "Lusiana Kurniawati"

# --- USER BAYAR LISENSI ---

@Client.on_message(filters.command("buy"))
async def buy_license(client, message):
    text = (
        "💳 *Paket Lisensi FSubBot*\n\n"
        "🔹 3 Tombol Wajib Join — Rp 20.000 / 30 Hari\n"
        "🔹 5 Tombol Wajib Join — Rp 25.000 / 30 Hari\n"
        "🔹 10 Tombol Wajib Join — Rp 40.000 / 30 Hari\n\n"
        f"📲 Kirim pembayaran ke:\n"
        f"• DANA: `{DANA_NUMBER}`\n"
        f"• A/N: {OWNER_NAME}\n\n"
        "Setelah transfer, *reply foto bukti transaksi* dengan perintah:\n"
        "`/sendproof <jumlah tombol>`\n\n"
        "Contoh:\n`/sendproof 5` *(kalau bayar Rp 25.000)*"
    )
    await message.reply_text(text, parse_mode=enums.ParseMode.MARKDOWN)


# --- USER KIRIM BUKTI TRANSFER ---

@Client.on_message(filters.command("sendproof") & filters.reply)
async def send_proof(client, message):
    if not message.reply_to_message.photo:
        return await message.reply_text("❗ Reply ke *foto bukti transfer* agar bisa diproses.", parse_mode=enums.ParseMode.MARKDOWN)

    user_id = message.from_user.id
    username = message.from_user.username or "tanpa_username"
    args = message.text.split()

    if len(args) < 2:
        return await message.reply_text("⚠️ Gunakan format: `/sendproof <jumlah tombol>`\nContoh: `/sendproof 5`")

    try:
        button_count = int(args[1])
        if button_count not in [3, 5, 10]:
            return await message.reply_text("❌ Pilihan tombol tidak valid. Hanya bisa 3, 5, atau 10.")
    except ValueError:
        return await message.reply_text("⚠️ Gunakan angka 3, 5, atau 10 sesuai paket.")

    proof_file_id = message.reply_to_message.photo.file_id
    amount = {3: 20000, 5: 25000, 10: 40000}[button_count]

    payments.insert_one({
        "user_id": user_id,
        "username": username,
        "button_limit": button_count,
        "amount": amount,
        "proof_file_id": proof_file_id,
        "approved": False,
        "created_at": datetime.now()
    })

    await message.reply_text("✅ Bukti pembayaran telah diterima.\nMenunggu verifikasi dari Owner.")

    # Kirim ke owner
    await client.send_photo(
        OWNER_ID,
        proof_file_id,
        caption=(
            f"💸 *Pembayaran Baru Masuk!*\n\n"
            f"👤 User: @{username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"📦 Paket: {button_count} tombol\n"
            f"💰 Nominal: Rp {amount:,}\n\n"
            f"Gunakan tombol di bawah ini untuk konfirmasi."
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_{button_count}"),
             InlineKeyboardButton("❌ Tolak", callback_data=f"reject_{user_id}")]
        ]),
        parse_mode=enums.ParseMode.MARKDOWN
    )


# --- OWNER APPROVE / REJECT ---

@Client.on_callback_query(filters.regex("^approve_"))
async def approve_license(client, callback):
    data = callback.data.split("_")
    user_id = int(data[1])
    button_limit = int(data[2])

    license_data = licenses.find_one({"user_id": user_id})
    exp_date = datetime.now() + timedelta(days=30)

    licenses.update_one(
        {"user_id": user_id},
        {"$set": {"active": True, "button_limit": button_limit, "expire_date": exp_date}},
        upsert=True
    )
    payments.update_one({"user_id": user_id}, {"$set": {"approved": True}})

    await client.send_message(
        user_id,
        f"🎉 *Lisensi Kamu Telah Aktif!*\n\n"
        f"✅ Limit tombol wajib join: {button_limit}\n"
        f"📅 Berlaku hingga: `{exp_date.strftime('%d-%m-%Y')}`\n\n"
        f"Gunakan /help untuk mulai setup bot kamu.",
        parse_mode=enums.ParseMode.MARKDOWN
    )

    await callback.edit_message_caption(
        caption=f"✅ *Pembayaran disetujui untuk user ID* `{user_id}`\nLisensi aktif {button_limit} tombol.",
        parse_mode=enums.ParseMode.MARKDOWN
    )


@Client.on_callback_query(filters.regex("^reject_"))
async def reject_license(client, callback):
    data = callback.data.split("_")
    user_id = int(data[1])

    payments.update_one({"user_id": user_id}, {"$set": {"approved": False, "rejected": True}})
    await client.send_message(
        user_id,
        "❌ Bukti pembayaran kamu ditolak. Pastikan nominal & bukti sesuai lalu kirim ulang."
    )
    await callback.edit_message_caption("❌ Pembayaran ditolak oleh owner.")
