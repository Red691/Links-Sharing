import motor.motor_asyncio
import base64
from config import DB_URI, DB_NAME
from datetime import datetime, timedelta

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
channels_collection = database["channels"]
encoded_links_collection = database["links"]

async def add_user(user_id: int):
    existing_user = await user_data.find_one({'_id': user_id})
    if existing_user:
        return 
    
    try:
        await user_data.insert_one({'_id': user_id})
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")

async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def full_userbase():
    user_docs = user_data.find()
    return [doc['_id'] async for doc in user_docs]

async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})

##-------------------------------------------------------------------

async def is_admin(user_id: int):
    return bool(await admins_collection.find_one({'_id': user_id}))

##-------------------------------------------------------------------

async def save_channel(channel_id: int):
    """Save a channel_id to the database with invite link expiration."""
    await channels_collection.update_one(
        {"channel_id": channel_id},
        {"$set": {"channel_id": channel_id, "invite_link_expiry": None}}, 
        upsert=True
    )

async def get_channels():
    """Get all channels from the database (No limit)"""
    channels = await channels_collection.find().to_list(None) 
    return [channel["channel_id"] for channel in channels]


async def delete_channel(channel_id: int):
    """Delete a channel from the database"""
    await channels_collection.delete_one({"channel_id": channel_id})

##-------------------------------------------------------------------

async def save_encoded_link(channel_id: int):
    encoded_link = base64.urlsafe_b64encode(str(channel_id).encode()).decode()
    await channels_collection.update_one(
        {"channel_id": channel_id},
        {"$set": {"encoded_link": encoded_link, "status": "active"}},
        upsert=True
    )
    return encoded_link


async def get_channel_by_encoded_link(encoded_link: str):
    channel = await channels_collection.find_one({"encoded_link": encoded_link, "status": "active"})
    return channel["channel_id"] if channel else None

#----------------------------------------------------------------------------------------------------------------

async def save_encoded_link2(channel_id: int, encoded_link: str):
    await channels_collection.update_one(
        {"channel_id": channel_id},
        {"$set": {"req_encoded_link": encoded_link, "status": "active"}},
        upsert=True
    )
    return encoded_link

async def get_channel_by_encoded_link2(encoded_link: str):
    channel = await channels_collection.find_one({"req_encoded_link": encoded_link, "status": "active"})
    return channel["channel_id"] if channel else None
    
# ===========================
# FORCE SUB DATABASE METHODS
# ===========================

req_channels = database["req_channels"]
req_users = database["req_users"]

# Add channel for Force-Sub
async def add_channel(channel_id: int):
    await req_channels.update_one(
        {"_id": channel_id},
        {"$set": {"_id": channel_id, "mode": "on"}},
        upsert=True
    )

# Remove one channel
async def rem_channel(channel_id: int):
    await req_channels.delete_one({"_id": channel_id})

# Delete channel (old function name support)
async def del_channel(channel_id: int):
    await req_channels.delete_one({"_id": channel_id})

# List all Force-Sub channels
async def show_channels():
    channels = req_channels.find()
    return [doc["_id"] async for doc in channels]

# Toggle mode (on/off)
async def get_channel_mode(channel_id: int):
    data = await req_channels.find_one({"_id": channel_id})
    return data.get("mode", "off") if data else "off"

async def update_channel_mode(channel_id: int, mode: str):
    await req_channels.update_one(
        {"_id": channel_id},
        {"$set": {"mode": mode}},
        upsert=True
    )

# Store users who sent join requests
async def req_user(channel_id: int, user_id: int):
    await req_users.update_one(
        {"chat_id": channel_id, "user_id": user_id},
        {"$set": {"chat_id": channel_id, "user_id": user_id}},
        upsert=True
    )

# Check if this channel exists in req list
async def reqChannel_exist(channel_id: int):
    data = await req_channels.find_one({"_id": channel_id})
    return bool(data)

# Check if user exists in request DB
async def req_user_exist(channel_id: int, user_id: int):
    data = await req_users.find_one({"chat_id": channel_id, "user_id": user_id})
    return bool(data)

# Delete user from req list
async def del_req_user(channel_id: int, user_id: int):
    await req_users.delete_one({"chat_id": channel_id, "user_id": user_id}) 
