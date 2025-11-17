import os
import logging
from logging.handlers import RotatingFileHandler

# ------------------------------------------------------------------------------------
# Bot Credentials
# ------------------------------------------------------------------------------------

TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
APP_ID = int(os.environ.get("APP_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# ------------------------------------------------------------------------------------
# Owner / Admin
# ------------------------------------------------------------------------------------

OWNER_ID = int(os.environ.get("OWNER_ID", "5770911041"))

ADMINS = []
try:
    for x in os.environ.get("ADMINS", "5770911041").split():
        ADMINS.append(int(x))
except ValueError:
    raise Exception("ADMINS env variable must contain integer IDs")

# Ensure OWNER is admin
if OWNER_ID not in ADMINS:
    ADMINS.append(OWNER_ID)

# ------------------------------------------------------------------------------------
# MongoDB
# ------------------------------------------------------------------------------------

DB_URI = os.environ.get("DATABASE_URL", "")
DB_NAME = os.environ.get("DATABASE_NAME", "Sensei")

# ------------------------------------------------------------------------------------
# Force Subscribe System
# ------------------------------------------------------------------------------------

FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "YourChannelUsername")
FSUB_PIC = os.environ.get("FSUB_PIC", "https://i.ibb.co/xK56gh8W/photo-2025.jpg")

# Toggle FSUB On/Off
FORCE_SUB = os.environ.get("FORCE_SUB", "True").lower() == "true"

# ------------------------------------------------------------------------------------
# Default Settings
# ------------------------------------------------------------------------------------

TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "4"))
START_MSG = os.environ.get("START_MESSAGE", "")

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = None

# ------------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------------

LOG_FILE_NAME = "links-sharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10),
        logging.StreamHandler()
    ]
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
