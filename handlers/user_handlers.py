from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from pymongo import MongoClient
import os

# Koneksi MongoDB
mongo = MongoClient(os.getenv("MONGO_URL"))
db = mongo["FSubProBot"]

users = db["users"]
licenses = db["licenses"]
buttons = db["buttons"]
channels = db["channels"]

# Start command
@Client.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    user_data = users.find_one({"user_id": user_id})

    if not user_data:
        users.insert_one({
            "user_id": user_id,
            "username": message.from_user.username,
            "created_at": datetime.now(),
            "license_active": False
        })
        await message.reply_text(
            "👋 Selamat datang di *FSubBot Profesional!*\n\n"
            "Kamu belum punya lisensi aktif.\n"
            "Silakan kirim bukti transfer dulu agar Owner mengaktifkan aksesmu.\n\n"
            "Gunakan perintah /help untuk melihat fitur lengkap.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return

    license = licenses.find_one({"user_id": user_id})
    if license and license.get("active", False):
        exp_date = license.get("expire_date").strftime("%d-%m-%Y")
        await message.reply_text(
            f"✅ Lisensimu aktif sampai `{exp_date}`.\n"
            "Gunakan menu /help untuk mulai setup bot kamu.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text(
            "❌ Lisensimu belum aktif atau sudah kadaluarsa.\n"
            "Silakan hubungi owner untuk perpanjangan.",
            parse_mode=enums.ParseMode.MARKDOWN
        )

# Help menu
@Client.on_message(filters.command("help"))
async def help_menu(client, message):
    text = (
        "📖 *Panduan Lengkap FSubBot Profesional*\n\n"
        "🧩 *Menu Utama:*\n"
        "• /settoken - Daftarkan bot token milikmu\n"
        "• /addjoin - Tambahkan channel wajib join (max sesuai limit)\n"
        "• /addkonten - Tambah channel sumber konten\n"
        "• /addshare - Tambah channel tujuan repost otomatis\n"
        "• /status - Lihat status lisensi & limit join\n"
        "• /renew - Perpanjang lisensi\n\n"
        "💡 *Cara Kerja:*\n"
        "1️⃣ Setelah lisensi aktif, masukkan bot token.\n"
        "2️⃣ Tambahkan channel wajib join (maks 10 sesuai paket).\n"
        "3️⃣ Tambahkan channel konten dan channel share.\n"
        "4️⃣ Bot akan otomatis repost foto/video ke channel share.\n\n"
        "🧾 *Info Lisensi:*\n"
        "- 30 Hari | 3 Button: Rp 20.000\n"
        "- 30 Hari | 5 Button: Rp 25.000\n"
        "- 30 Hari | 10 Button: Rp 40.000\n\n"
        "Hubungi Owner jika ingin perpanjang atau beli bot baru."
    )
    await message.reply_text(text, parse_mode=enums.ParseMode.MARKDOWN)

# Set bot token
@Client.on_message(filters.command("settoken"))
async def set_token(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("🔑 Gunakan format: `/settoken <token_bot>`", parse_mode=enums.ParseMode.MARKDOWN)
    token = message.command[1]
    users.update_one({"user_id": user_id}, {"$set": {"bot_token": token}})
    await message.reply_text("✅ Token bot berhasil disimpan.")

# Tambah channel wajib join
@Client.on_message(filters.command("addjoin"))
async def add_join_channel(client, message):
    user_id = message.from_user.id
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("📎 Gunakan format: `/addjoin <username_channel>`")

    channel = args[1].replace("@", "")
    limit_data = licenses.find_one({"user_id": user_id})
    max_buttons = limit_data.get("button_limit", 3)

    button_count = buttons.count_documents({"user_id": user_id})
    if button_count >= max_buttons:
        return await message.reply_text("⚠️ Kamu sudah mencapai batas maksimal tombol wajib join.")

    buttons.insert_one({"user_id": user_id, "channel": channel})
    await message.reply_text(f"✅ Channel @{channel} ditambahkan ke tombol wajib join.")

# Tambah channel konten sumber
@Client.on_message(filters.command("addkonten"))
async def add_konten(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("🗂 Gunakan format: `/addkonten <username_channel>`")
    konten_channel = message.command[1].replace("@", "")
    channels.update_one({"user_id": user_id}, {"$set": {"konten": konten_channel}}, upsert=True)
    await message.reply_text(f"✅ Channel konten @{konten_channel} disimpan.")

# Tambah channel repost
@Client.on_message(filters.command("addshare"))
async def add_share(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply_text("📤 Gunakan format: `/addshare <username_channel>`")
    share_channel = message.command[1].replace("@", "")
    channels.update_one({"user_id": user_id}, {"$set": {"share": share_channel}}, upsert=True)
    await message.reply_text(f"✅ Channel repost @{share_channel} disimpan.")

# Status lisensi
@Client.on_message(filters.command("status"))
async def status(client, message):
    user_id = message.from_user.id
    user = users.find_one({"user_id": user_id})
    license = licenses.find_one({"user_id": user_id})
    button_count = buttons.count_documents({"user_id": user_id})

    if not license:
        return await message.reply_text("🚫 Kamu belum punya lisensi aktif.")
    
    exp = license.get("expire_date")
    limit = license.get("button_limit", 3)
    text = (
        f"📊 *Status Lisensi*\n\n"
        f"👤 User: @{message.from_user.username}\n"
        f"📅 Expired: `{exp.strftime('%d-%m-%Y')}`\n"
        f"🔘 Tombol aktif: {button_count}/{limit}\n"
        f"🔑 Token: {'✅' if user.get('bot_token') else '❌ Belum diatur'}"
    )
    await message.reply_text(text, parse_mode=enums.ParseMode.MARKDOWN)

# Perpanjang lisensi
@Client.on_message(filters.command("renew"))
async def renew(client, message):
    await message.reply_text(
        "🔄 Untuk perpanjang lisensi, kirim bukti transfer ke owner.\n"
        "Setelah dikonfirmasi, lisensimu otomatis diperpanjang 30 hari."
    )
