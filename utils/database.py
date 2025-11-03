# utils/db.py
# Full professional MongoDB (Atlas) handler for FSUB autopost bot system
# Support: owners, users, buttons, channels, posts, licenses, payments

import motor.motor_asyncio
from datetime import datetime, timedelta
import logging
from bson import ObjectId

class DB:
    def __init__(self):
        self.client = None
        self.db = None

    # === CONNECT ===
    async def connect(self, mongo_uri: str, db_name: str = "autopostpro"):
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
            self.db = self.client[db_name]
            logging.info(f"✅ Mongo Atlas connected to {db_name}")
        except Exception as e:
            logging.error(f"❌ Mongo connect error: {e}")
            raise e

    # === OWNERS ===
    async def add_owner(self, owner_id: int, owner_name: str = None):
        await self.db.owners.update_one(
            {"owner_id": owner_id},
            {"$set": {"owner_id": owner_id, "owner_name": owner_name, "created_at": datetime.utcnow()}},
            upsert=True
        )

    async def get_owner(self, owner_id: int):
        return await self.db.owners.find_one({"owner_id": owner_id})

    async def list_owners(self):
        return [o async for o in self.db.owners.find({})]

    async def count_owners(self):
        return await self.db.owners.count_documents({})

    # === USERS ===
    async def add_user(self, user_id: int, owner_id: int):
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "owner_id": owner_id, "joined_at": datetime.utcnow()}},
            upsert=True
        )

    async def get_user(self, user_id: int):
        return await self.db.users.find_one({"user_id": user_id})

    async def count_users(self, owner_id: int = None):
        q = {"owner_id": owner_id} if owner_id else {}
        return await self.db.users.count_documents(q)

    # === BUTTONS (Wajib Join) ===
    async def add_button(self, owner_id: int, name: str, url: str):
        await self.db.buttons.insert_one({
            "owner_id": owner_id,
            "name": name,
            "url": url,
            "created_at": datetime.utcnow()
        })

    async def list_buttons(self, owner_id: int):
        return [b async for b in self.db.buttons.find({"owner_id": owner_id})]

    async def delete_button(self, owner_id: int, _id):
        await self.db.buttons.delete_one({"_id": ObjectId(_id), "owner_id": owner_id})

    async def count_buttons(self, owner_id: int):
        return await self.db.buttons.count_documents({"owner_id": owner_id})

    # === CHANNELS (Konten AutoPost) ===
    async def add_channel(self, owner_id: int, chat_id: int, title: str):
        await self.db.channels.update_one(
            {"owner_id": owner_id, "chat_id": chat_id},
            {"$set": {"owner_id": owner_id, "chat_id": chat_id, "title": title}},
            upsert=True
        )

    async def list_channels(self, owner_id: int):
        return [c async for c in self.db.channels.find({"owner_id": owner_id})]

    async def delete_channel(self, owner_id: int, chat_id: int):
        await self.db.channels.delete_one({"owner_id": owner_id, "chat_id": chat_id})

    # === POSTS ===
    async def save_post(self, post_id: str, owner_id: int, file_id: str, media_type: str, caption: str = ""):
        await self.db.posts.update_one(
            {"post_id": post_id},
            {"$set": {
                "post_id": post_id,
                "owner_id": owner_id,
                "file_id": file_id,
                "media_type": media_type,
                "caption": caption,
                "created_at": datetime.utcnow()
            }},
            upsert=True
        )

    async def get_post(self, post_id: str):
        return await self.db.posts.find_one({"post_id": post_id})

    # === LICENSE SYSTEM ===
    async def add_license(self, owner_id: int, max_buttons: int, days: int = 30):
        expire_at = datetime.utcnow() + timedelta(days=days)
        lic_doc = {
            "owner_id": owner_id,
            "max_buttons": max_buttons,
            "expire_at": expire_at,
            "status": "active"
        }
        await self.db.licenses.update_one({"owner_id": owner_id}, {"$set": lic_doc}, upsert=True)
        return lic_doc

    async def get_license(self, owner_id: int):
        return await self.db.licenses.find_one({"owner_id": owner_id})

    async def check_license_valid(self, owner_id: int):
        lic = await self.get_license(owner_id)
        if not lic: return False
        return lic.get("expire_at") > datetime.utcnow() and lic.get("status") == "active"

    # === PAYMENTS ===
    async def log_payment(self, user_id: int, amount: int, proof_file_id: str, plan: str):
        await self.db.payments.insert_one({
            "user_id": user_id,
            "amount": amount,
            "plan": plan,
            "proof_file_id": proof_file_id,
            "timestamp": datetime.utcnow()
        })

    async def list_payments(self):
        return [p async for p in self.db.payments.find({}).sort("timestamp", -1)]

    # === GENERAL UTIL ===
    async def set_config(self, owner_id: int, key: str, value):
        await self.db.owners.update_one(
            {"owner_id": owner_id},
            {"$set": {f"config.{key}": value}},
            upsert=True
        )

    async def get_config(self, owner_id: int, key: str):
        owner = await self.get_owner(owner_id)
        return (owner.get("config") or {}).get(key)

# Global instance
db = DB()
