# services/license.py
# AutopostPro Professional Edition
# Sistem Manajemen Lisensi Otomatis (LicenseManager)

import logging
from datetime import datetime, timedelta
from utils.db import db


class LicenseManager:
    def __init__(self):
        self.collection = None

    async def init_collection(self):
        if not self.collection:
            self.collection = db.db.licenses

    async def add_license(self, user_id: int, button_limit: int, expiry: datetime):
        """Menambahkan / memperbarui lisensi user"""
        await self.init_collection()
        try:
            await self.collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "button_limit": button_limit,
                        "expiry_date": expiry,
                        "active": True,
                        "updated_at": datetime.utcnow(),
                    }
                },
                upsert=True,
            )
            logging.info(f"✅ Lisensi user {user_id} ditambahkan ({button_limit} button, exp {expiry}).")
        except Exception as e:
            logging.error(f"❌ Gagal menambahkan lisensi: {e}")

    async def get_license(self, user_id: int):
        """Mengambil data lisensi user"""
        await self.init_collection()
        try:
            return await self.collection.find_one({"user_id": user_id})
        except Exception as e:
            logging.error(f"Gagal ambil lisensi {user_id}: {e}")
            return None

    async def is_license_active(self, user_id: int) -> bool:
        """Cek apakah lisensi user masih aktif"""
        license_data = await self.get_license(user_id)
        if not license_data:
            return False
        expiry = license_data.get("expiry_date")
        if expiry and datetime.now() < expiry:
            return True
        return False

    async def get_button_limit(self, user_id: int) -> int:
        """Ambil batas tombol wajib join"""
        license_data = await self.get_license(user_id)
        if license_data and license_data.get("active"):
            return license_data.get("button_limit", 3)
        return 0

    async def deactivate_expired_licenses(self):
        """Menonaktifkan lisensi yang sudah expired"""
        await self.init_collection()
        now = datetime.now()
        try:
            result = await self.collection.update_many(
                {"expiry_date": {"$lt": now}, "active": True},
                {"$set": {"active": False}}
            )
            if result.modified_count:
                logging.info(f"⏰ {result.modified_count} lisensi kedaluwarsa dinonaktifkan.")
        except Exception as e:
            logging.error(f"Gagal menonaktifkan lisensi expired: {e}")
