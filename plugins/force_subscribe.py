from pyrogram import Client, filters
from pymongo import MongoClient
from config import DB_URI, DB_NAME, ADMINS

# ------------------- Database Connection -------------------
db = MongoClient(DB_URI)[DB_NAME]
force_col = db["force_sub"]  # Collection for force subscribe channels
ADMIN = ADMINS[0]  # Main admin

# ------------------- Add Force Channel -------------------
@Client.on_message(filters.command("addforce") & filters.user(ADMIN))
async def add_force_channel(client, message):
    if len(message.command) < 2:
        return await message.reply("Use: /addforce -1001234567890")

    channel_id = message.command[1]

    if force_col.count_documents({}) >= 4:
        return await message.reply("❌ Max 4 channels allowed.")

    force_col.insert_one({"channel": channel_id})
    await message.reply(f"Added Force Channel:\n`{channel_id}`")

# ------------------- Remove Force Channel -------------------
@Client.on_message(filters.command("removeforce") & filters.user(ADMIN))
async def remove_force_channel(client, message):
    if len(message.command) < 2:
        return await message.reply("Use: /removeforce -1001234567890")

    channel_id = message.command[1]
    force_col.delete_one({"channel": channel_id})
    await message.reply(f"Removed:\n`{channel_id}`")

# ------------------- List Channels -------------------
@Client.on_message(filters.command("forcechannels") & filters.user(ADMIN))
async def list_channels(client, message):
    channels = list(force_col.find({}))
    if not channels:
        return await message.reply("No force channels set.")

    text = "Force Subscribe Channels:\n\n"
    for x in channels:
        text += f"• `{x['channel']}`\n"

    await message.reply(text)

# ------------------- Force Subscribe Checker -------------------
@Client.on_message(filters.private)
async def check_sub(client, message):
    channels = list(force_col.find({}))
    if not channels:
        return  # No force channels set

    for ch in channels:
        try:
            member = await client.get_chat_member(ch["channel"], message.from_user.id)
            if member.status in ["left"]:
                raise Exception()
        except:
            # If user hasn't joined, send invite link
            invite = await client.create_chat_invite_link(ch["channel"])
            return await message.reply(
                f"You must join this channel first:\n{invite.invite_link}"
            )
