# utils/helpers.py
# Professional utility helpers for FSUB autopost system
# Handle formatting, license checks, date/time, and inline utils

from datetime import datetime
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.db import db

# === TIME & DATE ===
def format_date(dt: datetime):
    return dt.strftime("%d/%m/%Y %H:%M")

def now_utc():
    return datetime.utcnow()

# === LICENSE / LIMIT ===
async def check_license_limit(owner_id: int):
    """
    Check if owner still within button limit based on license
    """
    license_data = await db.get_license(owner_id)
    if not license_data:
        return False, "❌ Belum punya lisensi aktif."

    expire_at = license_data.get("expire_at")
    if expire_at < datetime.utcnow():
        return False, "⚠️ Lisensi kamu sudah expired."

    max_buttons = license_data.get("max_buttons", 0)
    total_buttons = await db.count_buttons(owner_id)

    if total_buttons >= max_buttons:
        return False, f"❌ Limit tombol tercapai ({total_buttons}/{max_buttons})."

    return True, None


# === INLINE BUTTONS ===
def make_main_menu(owner_id: int):
    """
    Generate main menu for owner dashboard
    """
    buttons = [
        [InlineKeyboardButton("📣 Kelola Channel", callback_data=f"owner_channels_{owner_id}")],
        [InlineKeyboardButton("📎 Wajib Join", callback_data=f"owner_fsub_{owner_id}")],
        [InlineKeyboardButton("💳 License", callback_data=f"owner_license_{owner_id}")],
        [InlineKeyboardButton("👥 Pengguna", callback_data=f"owner_users_{owner_id}")],
        [InlineKeyboardButton("⚙️ Bantuan", callback_data=f"owner_help_{owner_id}")]
    ]
    return InlineKeyboardMarkup(buttons)


def make_user_menu():
    """
    Generate menu for user
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel Kami", callback_data="join_channels")],
        [InlineKeyboardButton("💬 Bantuan", callback_data="help_user")]
    ])


# === TEXT FORMATTERS ===
def format_license_info(license_data):
    if not license_data:
        return "❌ Tidak ada lisensi aktif."
    expire = format_date(license_data.get("expire_at"))
    max_buttons = license_data.get("max_buttons")
    return f"""
🧾 **Informasi Lisensi**
├ Status: ✅ Aktif
├ Maks. Tombol: {max_buttons}
└ Berlaku sampai: `{expire}`
"""

def format_payment_plan():
    """
    Generate payment plan text
    """
    return """
💳 **Pilih Paket Lisensi Autopost Bot**

1️⃣ **3 Button** — Rp20.000  
2️⃣ **5 Button** — Rp25.000  
3️⃣ **10 Button** — Rp40.000  

Kirim bukti transfer melalui perintah:
`/sendproof` (balas foto bukti tf)

Owner akan memverifikasi dan mengaktifkan lisensi kamu.
"""

def format_help_text():
    return """
🆘 **Bantuan Pengguna**

• Kirim postingan ke channel autopost.
• Pastikan kamu sudah join semua channel wajib.
• Jika tombol limit penuh, upgrade lisensi.
• Untuk bantuan hubungi owner.
"""

def format_owner_help():
    return """
⚙️ **Panduan Owner**

1️⃣ /addbutton — Tambah tombol wajib join  
2️⃣ /delbutton — Hapus tombol wajib join  
3️⃣ /addchannel — Tambah channel posting  
4️⃣ /delchannel — Hapus channel posting  
5️⃣ /license — Cek lisensi aktif  
6️⃣ /sendproof — Kirim bukti pembayaran  

📌 Semua data otomatis tersimpan di MongoDB Atlas.
"""

# === CHECKER UTILS ===
async def verify_user_join(client, user_id: int, required_channels: list):
    """
    Check if user has joined all required channels
    """
    missing = []
    for channel in required_channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                missing.append(channel)
        except Exception:
            missing.append(channel)
    return missing

# === OTHER HELPERS ===
def currency(amount: int):
    return f"Rp{amount:,.0f}".replace(",", ".")

def line():
    return "━━━━━━━━━━━━━━━"
