# handlers/__init__.py
"""
Handler Package
---------------
Berisi semua command handler bot:
- owner_handlers.py → Perintah untuk owner / sub-bot (pengaturan, fsub, admin, broadcast)
- user_handlers.py  → Perintah untuk user (akses konten, start, help, kirim bukti pembayaran)
"""

from .owner_handlers import register_owner_handlers
from .user_handlers import register_user_handlers

__all__ = ["register_owner_handlers", "register_user_handlers"]
