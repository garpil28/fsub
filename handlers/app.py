from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import db

# === Pesan start & menu utama ===
@Client.on_message(filters.command("start"))
async def start_menu(client, message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if not user:
        await db.add_user(user_id)

    text = (
        f"👋 Halo {message.from_user.mention}!\n"
        f"Selamat datang di **Garfield FSUB Autopost Pro Bot** 🐾\n\n"
        f"💡 Bot ini membantu kamu membuat autopost dengan fitur wajib join channel "
        f"dan limit button sesuai lisensi yang kamu pilih.\n\n"
        f"Silakan pilih menu di bawah:"
    )

    buttons = [
        [InlineKeyboardButton("🛒 Beli Lisensi", callback_data="buy_license")],
        [InlineKeyboardButton("📋 Menu Bantuan", callback_data="help_menu")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/USERNAME_OWNER")],  # ganti
    ]

    await message.reply_photo(
        photo="https://telegra.ph/file/8d373bf2c963d0db6b02a.jpg",  # bisa ganti banner toko kamu
        caption=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# === Callback: Menu Bantuan ===
@Client.on_callback_query(filters.regex("help_menu"))
async def help_callback(client, callback_query):
    text = (
        "📘 **Panduan Penggunaan Bot:**\n\n"
        "1️⃣ Gunakan /start untuk membuka menu utama.\n"
        "2️⃣ Klik 🛒 *Beli Lisensi* untuk memilih paket (3, 5, atau 10 tombol).\n"
        "3️⃣ Setelah pembayaran dikonfirmasi, kamu akan mendapatkan akses sesuai lisensi.\n"
        "4️⃣ Gunakan fitur autopost di menu yang tersedia.\n\n"
        "Jika butuh bantuan, hubungi 👑 owner."
    )
    back_btn = [[InlineKeyboardButton("⬅️ Kembali", callback_data="back_home")]]
    await callback_query.message.edit_caption(
        caption=text, reply_markup=InlineKeyboardMarkup(back_btn)
    )


# === Callback: Beli Lisensi ===
@Client.on_callback_query(filters.regex("buy_license"))
async def buy_license_callback(client, callback_query):
    text = (
        "💳 **Pilih Paket Lisensi:**\n\n"
        "🔹 3 Button — Rp20.000\n"
        "🔹 5 Button — Rp25.000\n"
        "🔹 10 Button — Rp40.000\n\n"
        "Kirim bukti pembayaran ke owner setelah transfer.\n"
        "Klik salah satu tombol di bawah untuk memilih."
    )

    buttons = [
        [InlineKeyboardButton("💠 Paket 3 Button", callback_data="pay_3btn")],
        [InlineKeyboardButton("💎 Paket 5 Button", callback_data="pay_5btn")],
        [InlineKeyboardButton("👑 Paket 10 Button", callback_data="pay_10btn")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="back_home")],
    ]

    await callback_query.message.edit_caption(
        caption=text, reply_markup=InlineKeyboardMarkup(buttons)
    )


# === Callback: Kembali ke home ===
@Client.on_callback_query(filters.regex("back_home"))
async def back_home_callback(client, callback_query):
    text = (
        "👋 Selamat datang kembali!\n\n"
        "Pilih menu utama di bawah ini:"
    )
    buttons = [
        [InlineKeyboardButton("🛒 Beli Lisensi", callback_data="buy_license")],
        [InlineKeyboardButton("📋 Menu Bantuan", callback_data="help_menu")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/USERNAME_OWNER")],  # ganti
    ]
    await callback_query.message.edit_caption(
        caption=text, reply_markup=InlineKeyboardMarkup(buttons)
    )


# === Callback: Paket pembayaran ===
@Client.on_callback_query(filters.regex(r"pay_(3btn|5btn|10btn)"))
async def payment_redirect(client, callback_query):
    package = callback_query.data
    packages = {
        "pay_3btn": ("3 Button", "Rp20.000"),
        "pay_5btn": ("5 Button", "Rp25.000"),
        "pay_10btn": ("10 Button", "Rp40.000"),
    }

    pack_name, price = packages.get(package)
    text = (
        f"💰 **Paket Dipilih:** {pack_name}\n"
        f"💵 Harga: {price}\n\n"
        f"Silakan kirim pembayaran ke:\n"
        f"🏧 *Dana / QRIS / Bank sesuai instruksi owner*\n\n"
        f"📸 Setelah itu kirim bukti pembayaran ke Owner untuk verifikasi."
    )
    buttons = [[InlineKeyboardButton("👑 Chat Owner", url="https://t.me/USERNAME_OWNER")]]  # ganti
    await callback_query.message.edit_caption(
        caption=text, reply_markup=InlineKeyboardMarkup(buttons)
    )
