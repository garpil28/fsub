import os
from dotenv import load_dotenv

# Load dari file .env
load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Validasi isi
if not all([API_ID, API_HASH, BOT_TOKEN, MONGO_URI, OWNER_ID]):
    raise ValueError("❌ Beberapa variabel .env belum diisi dengan benar!")

# Default setting
BOT_NAME = "AutoPostPro"
VERSION = "3.0 PRO"
