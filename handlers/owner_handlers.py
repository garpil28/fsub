# handlers/owner_handlers.py
# Owner (sub-bot) command handlers — full featured (matches menu in screenshots)
# Usage: call register_owner_handlers(app, db, license_key_or_owner_id) when spinning sub-bot

import time
import asyncio
from datetime import datetime
from bson import ObjectId
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Helper format
def fmt_rp(n): return f"Rp{n:,}"

def register_owner_handlers(app, db, owner_license_or_id):
    """
    Register commands for owner/sub-bot.
    - app: pyrogram Client instance (the sub-bot)
    - db: DB instance (utils.db.DB from earlier)
    - owner_license_or_id: owner identifier used for queries (license_key or owner_id)
    """

    # helper to resolve owner identity record
    def _owner_q():
        # allow passing license_key (string) or owner_id (int)
        try:
            if isinstance(owner_license_or_id, int):
                return {'owner_id': int(owner_license_or_id)}
            # license key -> lookup license doc
            lic = db.get_license(owner_license_or_id) if isinstance(owner_license_or_id, str) else None
            if lic:
                return {'owner_id': int(lic['owner_id'])}
        except Exception:
            pass
        # fallback: none
        return {}

    owner_query = _owner_q()

    # --- /start ---
    @app.on_message(filters.command("start"))
    async def _start(client, message):
        txt = ("Halo, selamat datang!\n\n"
               "Gunakan /help untuk melihat menu pemilik dan perintah bot.")
        await message.reply_text(txt)

    # --- /help ---
    @app.on_message(filters.command("help"))
    async def _help(client, message):
        txt = (
            "📘 *Menu Owner (FSUB)*\n\n"
            "/start - Mulai bot\n"
            "/help - Menu ini\n"
            "/addpic - Mengatur foto untuk auto post konten bot (/addpic reply foto)\n"
            "/users - Mengecek pengguna bot\n"
            "/broadcast <teks> - Kirim siaran ke pengguna bot\n"
            "/addadmin <@user|id> - Menambahkan admin\n            /deladmin <@user|id> - Hapus admin\n"
            "/getadmin - Lihat daftar admin\n"
            "/info - Cek status bot fsup\n"
            "/ping - Cek ping bot\n"
            "/uptime - Cek waktu aktif bot\n"
            "/addbutton <nama>|<url> - Tambah button wajib join\n"
            "/delbutton <button_id> - Hapus button\n"
            "/getbutton - Cek button bot\n"
            "/addkonten <@channel|id> - Tambah channel konten (source)\n"
            "/delkonten <@channel|id> - Hapus channel konten\n"
            "/getkonten - Cek channel konten\n"
            "/limitbutton <angka> - Set limit button wajib join (max 10)\n"
            "/limitkonten <angka> - Set limit konten auto-share\n            /protect on|off - Batasi konten di bot\n"
            "/setdb <key> <value> - Atur config di DB (mis. fsub_channel)\n"
            "/getdb <key> - Ambil value\n"
            "/setmsg <teks> - Atur pesan wajib join\n"
            "/batch - Untuk membuat link lebih dari satu file (reply multiple files lalu /batch)\n"
            "/genlink <post_id> - Buat tautan untuk satu posting\n"
        )
        await message.reply_text(txt)

    # --- /addpic (set thumbnail or auto-post pic) ---
    @app.on_message(filters.command("addpic") & filters.reply)
    async def _addpic(client, message):
        # expects reply to a photo message
        if not message.reply_to_message or not message.reply_to_message.photo:
            await message.reply_text("Reply ke pesan berisi foto dengan perintah /addpic.")
            return
        owner_q = owner_query
        file_id = message.reply_to_message.photo[-1].file_id
        db.db.owners.update_one(owner_q, {'$set': {'auto_pic': file_id}})
        await message.reply_text("Foto auto-post disimpan.")

    # --- /users ---
    @app.on_message(filters.command("users"))
    async def _users(client, message):
        owner_q = owner_query
        owner_doc = db.owners.find_one(owner_q) if owner_q else None
        owner_id = owner_doc.get('owner_id') if owner_doc else None
        count = db.count_users(owner_id) if owner_id else db.count_users()
        await message.reply_text(f"Total pengguna (owner): {count}")

    # --- /broadcast ---
    @app.on_message(filters.command("broadcast") & filters.reply)
    async def _broadcast_reply(client, message):
        # If user replies to a message with /broadcast, send that message to all users
        # Only owner permitted: check license owner
        owner_doc = db.owners.find_one(owner_query) if owner_query else None
        if not owner_doc:
            await message.reply_text("Owner tidak ditemukan / belum aktif.")
            return
        # gather target users for this owner
        targets = list(db.db.users.find({'owner_id': owner_doc['owner_id']}))
        if not targets:
            await message.reply_text("Belum ada pengguna untuk dikirimi broadcast.")
            return
        sent = 0
        failed = 0
        for u in targets:
            try:
                await client.copy_message(u['user_id'], message.chat.id, message.reply_to_message.message_id)
                sent += 1
            except Exception:
                failed += 1
        await message.reply_text(f"Broadcast dikirim: {sent} sukses, {failed} gagal.")

    @app.on_message(filters.command("broadcast") & ~filters.reply)
    async def _broadcast_text(client, message):
        owner_doc = db.owners.find_one(owner_query) if owner_query else None
        if not owner_doc:
            await message.reply_text("Owner tidak ditemukan.")
            return
        text = message.text.split(maxsplit=1)
        if len(text) < 2:
            await message.reply_text("Usage: /broadcast <pesan>")
            return
        msg = text[1]
        targets = list(db.db.users.find({'owner_id': owner_doc['owner_id']}))
        sent = 0
        failed = 0
        for u in targets:
            try:
                await client.send_message(u['user_id'], msg)
                sent += 1
            except Exception:
                failed += 1
        await message.reply_text(f"Broadcast dikirim: {sent} sukses, {failed} gagal.")

    # --- admin management: /addadmin /deladmin /getadmin ---
    @app.on_message(filters.command("addadmin"))
    async def _addadmin(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /addadmin <@username_or_id>")
            return
        who = parts[1]
        owner_doc = db.owners.find_one(owner_query) if owner_query else None
        if not owner_doc:
            await message.reply_text("Owner not found.")
            return
        # store admin in owner admins array
        admins = owner_doc.get('admins', [])
        if who in admins:
            await message.reply_text("User sudah menjadi admin.")
            return
        db.db.owners.update_one({'owner_id': owner_doc['owner_id']}, {'$push': {'admins': who}})
        await message.reply_text("Admin ditambahkan.")

    @app.on_message(filters.command("deladmin"))
    async def _deladmin(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /deladmin <@username_or_id>")
            return
        who = parts[1]
        owner_doc = db.owners.find_one(owner_query) if owner_query else None
        if not owner_doc:
            await message.reply_text("Owner not found.")
            return
        db.db.owners.update_one({'owner_id': owner_doc['owner_id']}, {'$pull': {'admins': who}})
        await message.reply_text("Admin dihapus (jika ada).")

    @app.on_message(filters.command("getadmin"))
    async def _getadmin(client, message):
        owner_doc = db.owners.find_one(owner_query) if owner_query else None
        if not owner_doc:
            await message.reply_text("Owner not found.")
            return
        admins = owner_doc.get('admins', [])
        txt = "Admins:\n" + ("\n".join(admins) if admins else "Tidak ada admin.")
        await message.reply_text(txt)

    # --- /info / /ping / /uptime ---
    start_time = time.time()

    @app.on_message(filters.command("info"))
    async def _info(client, message):
        owner_doc = db.owners.find_one(owner_query) if owner_query else None
        lic = None
        if owner_doc:
            lic = db.get_license(owner_doc.get('license_key'))
        txt = (
            f"Bot Info\nOwner: {owner_doc.get('owner_name') if owner_doc else 'N/A'}\n"
            f"License: {lic.get('license_key') if lic else 'N/A'}\n"
            f"Buttons limit: {owner_doc.get('config',{}).get('limit_buttons', 'unset')}\n"
        )
        await message.reply_text(txt)

    @app.on_message(filters.command("ping"))
    async def _ping(client, message):
        t0 = time.time()
        msg = await message.reply_text("Pong...")
        t1 = time.time()
        await msg.edit_text(f"Pong! {int((t1 - t0)*1000)} ms")

    @app.on_message(filters.command("uptime"))
    async def _uptime(client, message):
        delta = int(time.time() - start_time)
        await message.reply_text(f"Uptime: {delta} detik")

    # --- button management: addbutton / delbutton / getbutton ---
    @app.on_message(filters.command("addbutton"))
    async def _addbutton(client, message):
        # usage: /addbutton <name>|<url>
        parts = message.text.split(None, 1)
        if len(parts) < 2:
            await message.reply_text("Usage: /addbutton <name>|<url>")
            return
        try:
            name, url = parts[1].split("|",1)
        except Exception:
            await message.reply_text("Pisahkan nama dan url pakai | (pipe). Contoh: /addbutton Join|https://t.me/chan")
            return
        owner_doc = db.owners.find_one(owner_query)
        if not owner_doc:
            await message.reply_text("Owner not found.")
            return
        # enforce limit (max 10)
        limit = owner_doc.get('config', {}).get('limit_buttons', int(os.getenv("LIMIT_BUTTON_DEFAULT", 10)))
        cur_count = db.count_buttons(owner_doc['owner_id'])
        if cur_count >= limit:
            await message.reply_text(f"Sudah mencapai limit tombol: {limit}")
            return
        db.add_button(owner_doc['owner_id'], name.strip(), url.strip())
        await message.reply_text("Button ditambahkan.")

    @app.on_message(filters.command("getbutton"))
    async def _getbutton(client, message):
        owner_doc = db.owners.find_one(owner_query)
        if not owner_doc:
            await message.reply_text("Owner not found.")
            return
        btns = db.list_buttons(owner_doc['owner_id'])
        if not btns:
            await message.reply_text("Belum ada button.")
            return
        txt = "Buttons:\n"
        for b in btns:
            txt += f"{b.get('_id')} | {b.get('name')} -> {b.get('url')}\n"
        await message.reply_text(txt)

    @app.on_message(filters.command("delbutton"))
    async def _delbutton(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /delbutton <button_id>")
            return
        bid = parts[1]
        owner_doc = db.owners.find_one(owner_query)
        try:
            db.delete_button(owner_doc['owner_id'], ObjectId(bid))
            await message.reply_text("Button dihapus.")
        except Exception:
            await message.reply_text("Gagal menghapus button. Pastikan ID benar.")

    # --- channel content management: addkonten / delkonten / getkonten ---
    @app.on_message(filters.command("addkonten"))
    async def _addkonten(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /addkonten <@channel_or_id>")
            return
        chat = parts[1]
        try:
            ch = await client.get_chat(chat)
            owner_doc = db.owners.find_one(owner_query)
            db.add_channel(owner_doc['owner_id'], ch.id, ch.title)
            await message.reply_text(f"Channel sumber ditambahkan: {ch.title} ({ch.id})")
        except Exception as e:
            await message.reply_text(f"Gagal menambahkan channel: {e}")

    @app.on_message(filters.command("delkonten"))
    async def _delkonten(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /delkonten <@channel_or_id_or_chat_id>")
            return
        chat = parts[1]
        try:
            ch = await client.get_chat(chat)
            owner_doc = db.owners.find_one(owner_query)
            db.db.channels.delete_one({'owner_id': owner_doc['owner_id'], 'chat_id': ch.id})
            await message.reply_text("Channel sumber dihapus.")
        except Exception as e:
            await message.reply_text(f"Gagal: {e}")

    @app.on_message(filters.command("getkonten"))
    async def _getkonten(client, message):
        owner_doc = db.owners.find_one(owner_query)
        chs = db.list_channels(owner_doc['owner_id'])
        if not chs:
            await message.reply_text("Belum ada channel konten.")
            return
        txt = "Channel konten:\n"
        for c in chs:
            txt += f"{c.get('chat_id')} - {c.get('title','-')}\n"
        await message.reply_text(txt)

    # --- limitbutton / limitkonten ---
    @app.on_message(filters.command("limitbutton"))
    async def _limitbutton(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /limitbutton <angka> (max 10)")
            return
        v = int(parts[1])
        if v > 10:
            await message.reply_text("Max tombol adalah 10.")
            return
        owner_doc = db.owners.find_one(owner_query)
        db.db.owners.update_one({'owner_id': owner_doc['owner_id']}, {'$set': {'config.limit_buttons': v}})
        await message.reply_text(f"Limit tombol di-set ke {v}")

    @app.on_message(filters.command("limitkonten"))
    async def _limitkonten(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /limitkonten <angka>")
            return
        v = int(parts[1])
        owner_doc = db.owners.find_one(owner_query)
        db.db.owners.update_one({'owner_id': owner_doc['owner_id']}, {'$set': {'config.limit_konten': v}})
        await message.reply_text(f"Limit konten di-set ke {v}")

    # --- protect on/off (batasi konten di bot) ---
    @app.on_message(filters.command("protect"))
    async def _protect(client, message):
        parts = message.text.split()
        if len(parts) < 2 or parts[1].lower() not in ("on","off"):
            await message.reply_text("Usage: /protect on|off")
            return
        val = parts[1].lower() == "on"
        owner_doc = db.owners.find_one(owner_query)
        db.db.owners.update_one({'owner_id': owner_doc['owner_id']}, {'$set': {'config.protect': val}})
        await message.reply_text(f"Protect di-set ke {val}")

    # --- setdb / getdb (general owner config) ---
    @app.on_message(filters.command("setdb"))
    async def _setdb(client, message):
        parts = message.text.split(None, 2)
        if len(parts) < 3:
            await message.reply_text("Usage: /setdb <key> <value>")
            return
        key = parts[1]
        val = parts[2]
        owner_doc = db.owners.find_one(owner_query)
        db.db.owners.update_one({'owner_id': owner_doc['owner_id']}, {'$set': {f'config.{key}': val}})
        await message.reply_text(f"Set config {key} = {val}")

    @app.on_message(filters.command("getdb"))
    async def _getdb(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /getdb <key>")
            return
        key = parts[1]
        owner_doc = db.owners.find_one(owner_query)
        val = (owner_doc.get('config') or {}).get(key)
        await message.reply_text(f"{key} = {val}")

    # --- setmsg (pesan wajib join) ---
    @app.on_message(filters.command("setmsg"))
    async def _setmsg(client, message):
        parts = message.text.split(None,1)
        if len(parts) < 2:
            await message.reply_text("Usage: /setmsg <pesan>")
            return
        txt = parts[1]
        owner_doc = db.owners.find_one(owner_query)
        db.db.owners.update_one({'owner_id': owner_doc['owner_id']}, {'$set': {'config.fsub_msg': txt}})
        await message.reply_text("Pesan wajib join disimpan.")

    # --- batch: create multiple links (reply multiple files then /batch) ---
    @app.on_message(filters.command("batch") & filters.reply)
    async def _batch(client, message):
        # expects user reply to a message that contains many media or forwarded group
        reply = message.reply_to_message
        if not reply:
            await message.reply_text("Reply ke pesan yang mengandung file atau beberapa file.")
            return
        owner_doc = db.owners.find_one(owner_query)
        media = []
        # gather media file_ids if present
        if reply.photo:
            media.append(reply.photo[-1].file_id)
        if reply.video:
            media.append(reply.video.file_id)
        # if forwarded multiple messages, platform complexity increases — here we handle basic
        if not media:
            await message.reply_text("Tidak menemukan media untuk di-batch.")
            return
        links = []
        for m in media:
            post_id = rand_short = str(ObjectId())
            db.save_post(post_id, owner_doc['owner_id'], m, m, caption=reply.caption or '')
            bot_username = (await app.get_me()).username
            links.append(f"https://t.me/{bot_username}?start=get_{post_id}")
        out = "Links created:\n" + "\n".join(links)
        await message.reply_text(out)

    # --- genlink <post_id> ---
    @app.on_message(filters.command("genlink"))
    async def _genlink(client, message):
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply_text("Usage: /genlink <post_id>")
            return
        pid = parts[1]
        post = db.get_post(pid)
        if not post:
            await message.reply_text("Post tidak ditemukan.")
            return
        bot_username = (await app.get_me()).username
        link = f"https://t.me/{bot_username}?start=get_{pid}"
        await message.reply_text(link)

    # --- additional helper commands --- e.g., setdb for DB switching, setdb/getdb already above
    # If you need `/setdb` to change where owner DB stored or to set database name, extend accordingly.

    # End register_owner_handlers
