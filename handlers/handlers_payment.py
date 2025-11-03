# handlers/payment.py
# AutopostPro Professional Edition
# Handler Pembayaran & Lisensi Otomatis

import logging
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from services.payment_service import PaymentService

# Load variabel dari env
import os
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))
QR_PAYMENT_URL = os.getenv("QR_PAYMENT_URL", "https://files.catbox.moe/tq9d36.jpg")

# Inisialisasi PaymentService
payment_service = None

def init_payment_service(bot: Client):
    global payment_service
    payment_service = PaymentService(bot, OWNER_ID, LOG_CHANNEL)

# === COMMAND: /buy ===
@Client.on_message(filters.command("buy"))
async def buy_license(bot: Client, message):
    text = (
        "💳 **Paket Lisensi AutopostPro**\n\n"
        "🔹 3 Tombol Wajib Join — Rp 20.000 / 30 Hari\n"
        "🔹 5 Tombol Wajib Join — Rp 25.000 / 30 Hari\n"
        "🔹 10 Tombol Wajib Join — Rp 40.000 / 30 Hari\n\n"
        "📸 *Scan QR di bawah untuk bayar via DANA:*\n"
        f"[QR DANA]({QR_PAYMENT_URL})\n\n"
        "📩 Setelah transfer, kirim bukti pembayaran dengan:\n"
        "`Balas foto bukti transfer` lalu ketik /sendproof\n\n"
        "_Tunggu verifikasi dari owner maksimal 24 jam._"
    )

    await message.reply_photo(
        QR_PAYMENT_URL,
        caption=text,
        parse_mode=enums.ParseMode.MARKDOWN
    )

# === COMMAND: /sendproof ===
@Client.on_message(filters.command("sendproof") & filters.reply)
async def send_payment_proof(bot: Client, message):
    if not payment_service:
        init_payment_service(bot)

    await payment_service.handle_payment_proof(message)

# === CALLBACK: Approve / Reject Payment ===
@Client.on_callback_query(filters.regex("^(approve_|reject_)"))
async def handle_payment_callback(bot: Client, callback_query):
    if not payment_service:
        init_payment_service(bot)

    data = callback_query.data.split("_")
    action = data[0]  # approve / reject
    package = data[1] if len(data) > 1 else None
    user_id = int(data[-1])

    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Hanya owner yang dapat verifikasi pembayaran!", show_alert=True)

    if action == "approve":
        await payment_service.approve_payment(user_id, package)
        await callback_query.edit_message_caption(
            caption=f"✅ Pembayaran user `{user_id}` telah disetujui ({package.replace('approve_', '')} tombol).",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    elif action == "reject":
        await payment_service.reject_payment(user_id)
        await callback_query.edit_message_caption(
            caption=f"❌ Pembayaran user `{user_id}` ditolak oleh owner.",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    await callback_query.answer("✅ Aksi diproses.")
