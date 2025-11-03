# utils/license.py
"""
License Manager - AutopostPro Professional Edition
--------------------------------------------------
Mengatur lisensi user:
- Menyimpan batas button join
- Menyimpan masa aktif (30 hari)
- Mengecek validitas lisensi
"""

import logging
from datetime import datetime
from utils.db import db


class LicenseManager:
    def __init__(self):
        self.collection = None

    async def add_license(self, user_id: int, button_limit: int, expiry_date: datetime):
        """Menambahkan lisensi baru untuk user"""
        try:
            await db.db.licenses.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "button_limit": button_limit,
                        "expiry": expiry_date,
                        "status": "active"
                    }
                },
                upsert=True
            )
            logging.info(f"✅ Lisensi disimpan untuk user {user_id} ({button_limit} button, aktif sampai {expiry_date})")
        except Exception as e:
            logging.error(f"❌ Gagal menyimpan lisensi: {e}")

    async def get_license(self, user_id: int):
        """Mengambil data lisensi user"""
        try:
            return await db.db.licenses.find_one({"user_id": user_id})
        except Exception as e:
            logging.error(f"❌ Gagal mengambil lisensi user {user_id}: {e}")
            return None

    async def check_license(self, user_id: int) -> bool:
        """Cek apakah lisensi user masih aktif"""
        license_data = await self.get_license(user_id)
        if not license_data:
            return False

        expiry = license_data.get("expiry")
        if not expiry:
            return False

        # Convert Mongo datetime ke Python datetime
        if isinstance(expiry, str):
            expiry = datetime.fromisoformat(expiry)

        if expiry < datetime.now():
            await self.deactivate_license(user_id)
            return False
        return True

    async def deactivate_license(self, user_id: int):
        """Menonaktifkan lisensi jika masa aktif habis"""
        try:
            await db.db.licenses.update_one(
                {"user_id": user_id},
                {"$set": {"status": "expired"}}
            )
            logging.info(f"⚠️ Lisensi user {user_id} telah kedaluwarsa.")
        except Exception as e:
            logging.error(f"❌ Gagal menonaktifkan lisensi user {user_id}: {e}")

    async def get_button_limit(self, user_id: int) -> int:
        """Ambil jumlah button join maksimal untuk user"""
        license_data = await self.get_license(user_id)
        if not license_data or license_data.get("status") != "active":
            return 0
        return license_data.get("button_limit", 0)
