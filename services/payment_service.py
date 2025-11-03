"""
Payment Service - AutopostPro Professional Edition
--------------------------------------------------
Mengatur sistem pembayaran otomatis:
- Pembeli kirim bukti transfer (foto)
- Owner menerima notifikasi verifikasi
- Setelah approve, pembeli otomatis dapat lisensi (limit button sesuai paket)
"""

import logging
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db import db
from utils.license import LicenseManager


class PaymentService:
    def __init__(self, bot: Client, owner_id: int, log_channel: int):
        self.bot = bot
        self.owner_id = owner_id
        self.log_channel = log_channel
        self.license_mgr = LicenseManager()

    async def handle_payment_proof(self, message):
        """Menangani bukti transfer dari pembeli"""
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await message.reply_text("❌ Balas ke foto bukti transfer untuk mengirim pembayaran.")

        user_id = message.from_user.id
        proof_photo = message.reply_to_message.photo.file_id
        caption = message.caption or "Tanpa keterangan"

        # Simpan bukti pembayaran ke database
        await db.log_payment(user_id, 0, proof_photo)

        # Kirim notifikasi ke owner
        text = (
            f"💳 **Bukti pembayaran diterima!**\n\n"
            f"👤 User: [{message.from_user.first_name}](tg://user?id={user_id})\n"
            f"🆔 ID: `{user_id}`\n"
            f"🕒 Waktu: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}\n\n"
            f"📝 Catatan: {caption}\n\n"
            f"Silakan pilih paket untuk approve:"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("3 Button - 30 Hari", callback_data=f"approve_3_{user_id}"),
                InlineKeyboardButton("5 Button - 30 Hari", callback_data=f"approve_5_{user_id}")
            ],
            [
                InlineKeyboardButton("10 Button - 30 Hari", callback_data=f"approve_10_{user_id}")
            ],
            [
                InlineKeyboardButton("❌ Tolak Pembayaran", callback_data=f"reject_{user_id}")
            ]
        ])

        # Kirim ke owner dan log channel
        try:
            await self.bot.send_photo(
                self.owner_id,
                photo=proof_photo,
                caption=text,
                reply_markup=keyboard
            )
            await self.bot.send_photo(
                self.log_channel,
                photo=proof_photo,
                caption=f"📦 Bukti pembayaran baru dari `{user_id}`"
            )
        except Exception as e:
            logging.error(f"Gagal kirim notifikasi pembayaran: {e}")

        await message.reply_text("✅ Bukti sudah dikirim ke owner. Tunggu verifikasi maksimal 24 jam.")

    async def approve_payment(self, user_id: int, package_type: str):
        """Owner approve pembayaran dan set lisensi"""
        button_limit = {
            "approve_3": 3,
            "approve_5": 5,
            "approve_10": 10
        }.get(package_type, 3)

        expiry = datetime.now() + timedelta(days=30)
        await self.license_mgr.add_license(user_id, button_limit, expiry)

        # Kirim notifikasi ke user
        try:
            await self.bot.send_message(
                user_id,
                f"✅ **Pembayaran disetujui!**\n"
                f"Kamu mendapat lisensi aktif 30 hari dengan **{button_limit} button join**.\n\n"
                f"Gunakan /deploy untuk mulai setup bot kamu."
            )
        except Exception:
            pass

        # Notifikasi ke owner
        await self.bot.send_message(
            self.owner_id,
            f"✅ Pembayaran user `{user_id}` berhasil disetujui untuk paket {button_limit} button."
        )

        # Log
        await self.bot.send_message(
            self.log_channel,
            f"🟢 Payment approved — User `{user_id}` | Paket {button_limit} button | Exp: {expiry.strftime('%d-%m-%Y')}"
        )

        logging.info(f"License diberikan ke {user_id} ({button_limit} button).")

    async def reject_payment(self, user_id: int):
        """Owner menolak pembayaran"""
        try:
            await self.bot.send_message(
                user_id,
                "❌ **Pembayaran kamu ditolak oleh owner.**\n"
                "Silakan hubungi owner untuk klarifikasi atau kirim bukti ulang."
            )
        except Exception:
            pass

        try:
            await self.bot.send_message(
                self.owner_id,
                f"❌ Pembayaran user `{user_id}` telah ditolak."
            )
        except Exception:
            pass

        await self.bot.send_message(
            self.log_channel,
            f"🔴 Payment ditolak — User `{user_id}`"
        )

        logging.info(f"Payment user {user_id} ditolak oleh owner.")
