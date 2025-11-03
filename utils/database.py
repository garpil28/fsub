import motor.motor_asyncio
import logging

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self, mongo_uri: str):
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
            self.db = self.client['autopostpro']
            logging.info("✅ Koneksi Mongo Atlas berhasil.")
        except Exception as e:
            logging.error(f"❌ Gagal konek ke Mongo Atlas: {e}")

    async def add_owner(self, owner_id: int):
        await self.db.owners.update_one(
            {"owner_id": owner_id},
            {"$set": {"owner_id": owner_id}},
            upsert=True
        )

    async def get_owner(self):
        return await self.db.owners.find_one()

    async def add_user(self, user_id: int):
        await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True
        )

    async def get_user(self, user_id: int):
        return await self.db.users.find_one({"user_id": user_id})

    async def set_join_channels(self, owner_id: int, channels: list):
        await self.db.join_settings.update_one(
            {"owner_id": owner_id},
            {"$set": {"channels": channels}},
            upsert=True
        )

    async def get_join_channels(self, owner_id: int):
        data = await self.db.join_settings.find_one({"owner_id": owner_id})
        return data["channels"] if data else []

    async def log_payment(self, user_id: int, amount: int, proof_url: str):
        await self.db.payments.insert_one({
            "user_id": user_id,
            "amount": amount,
            "proof": proof_url
        })

db = Database()
