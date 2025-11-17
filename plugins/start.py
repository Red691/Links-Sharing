import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import UserNotParticipant

from bot import Bot
from config import ADMINS, OWNER_ID, FORCE_SUB_CHANNEL, FSUB_PIC
from helper_func import encode, decode
from database.database import add_user, del_user, full_userbase, present_user
from database.database import save_encoded_link, get_channel_by_encoded_link
from database.database import save_encoded_link2, get_channel_by_encoded_link2
from plugins.newpost import revoke_invite_after_10_minutes

# ======================================================================
# 🔐  FSUB SYSTEM
# ======================================================================

async def force_sub(client, message):
    try:
        user = await client.get_chat_member(FORCE_SUB_CHANNEL, message.from_user.id)

        if user.status == "kicked":
            await message.reply("❌ Aap is channel se banned ho.")
            return False

        return True

    except UserNotParticipant:
        await message.reply_photo(
            photo=FSUB_PIC,
            caption="⚠️ **Channel Join Kare Tab Hi Bot Use Kar Payenge!**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
                [InlineKeyboardButton("♻️ Joined", callback_data="check_fsub")]
            ])
        )
        return False

    except Exception as e:
        print(e)
        return False


# ======================================================================
# 🔘 START COMMAND (FSUB + encoded link + full logic)
# ======================================================================

user_message_count = {}
user_banned_until = {}
MAX_MESSAGES = 3
TIME_WINDOW = timedelta(seconds=10)
BAN_DURATION = timedelta(hours=1)


@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Bot, message: Message):

    # 🔐 FSUB Check
    if not await force_sub(client, message):
        return

    user_id = message.from_user.id

    # Ban check
    if user_id in user_banned_until and datetime.now() < user_banned_until[user_id]:
        return await message.reply_text("🚫 You are temporarily banned from using commands due to spamming.")

    await add_user(user_id)

    text = message.text

    # ========== Encoded Link System ==========
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            is_request = base64_string.startswith("req_")

            if is_request:
                base64_string = base64_string[4:]
                channel_id = await get_channel_by_encoded_link2(base64_string)
            else:
                channel_id = await get_channel_by_encoded_link(base64_string)

            if not channel_id:
                return await message.reply_text("⚠️ Invalid or expired invite link.")

            invite = await client.create_chat_invite_link(
                chat_id=channel_id,
                expire_date=datetime.now() + timedelta(minutes=10),
                creates_join_request=is_request
            )

            button_text = "🛎️ Request to Join" if is_request else "🔗 Join Channel"
            btn = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=invite.invite_link)]])

            await message.reply_text("Here is your link!", reply_markup=btn)

            asyncio.create_task(revoke_invite_after_10_minutes(client, channel_id, invite.invite_link, is_request))

        except Exception as e:
            print(e)
            return await message.reply_text("⚠️ Invalid or expired link.")

    else:
        # Normal Start Message
        await message.reply_text(
            f"👋 Hello **{message.from_user.first_name}!**\n\n"
            "Welcome to **File Store Bot**.\n"
            "Yaha aap apne files ko link ke through share kar sakte ho.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Updates Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
                [InlineKeyboardButton("Help", callback_data="help"),
                 InlineKeyboardButton("Close", callback_data="close")]
            ])
        )


# ======================================================================
# CALLBACK BUTTON HANDLERS
# ======================================================================

@Bot.on_callback_query(filters.regex("check_fsub"))
async def recheck_fsub(client, callback_query: CallbackQuery):
    if await force_sub(client, callback_query.message):
        await callback_query.message.edit("✅ **Shukriya! Aap channel join kar chuke ho.**\n\nAb aap bot use kar sakte ho.")
    await callback_query.answer()


@Bot.on_callback_query(filters.regex("help"))
async def help_button(client, callback_query):
    await callback_query.message.edit(
        "<b><i>About Us..\n\n‣ Made for : @Red_999_Yt\n‣ Main Channel: @Anime_Sensei_Official</i></b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close")]])
    )
    await callback_query.answer()


@Bot.on_callback_query(filters.regex("close"))
async def close_button(client, callback_query):
    await callback_query.message.delete()
    await callback_query.answer()


# ======================================================================
# SPAM PROTECTION SYSTEM
# ======================================================================

@Bot.on_message(filters.private)
async def monitor_messages(client: Bot, message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    if user_id in ADMINS:
        return

    if user_id in user_banned_until and now < user_banned_until[user_id]:
        return await message.reply_text("⚠️ You are temporarily banned due to spamming.")

    if user_id not in user_message_count:
        user_message_count[user_id] = []

    user_message_count[user_id].append(now)
    user_message_count[user_id] = [t for t in user_message_count[user_id] if now - t <= TIME_WINDOW]

    if len(user_message_count[user_id]) > MAX_MESSAGES:
        user_banned_until[user_id] = now + BAN_DURATION
        return await message.reply_text("🚫 You have been temporarily banned for spamming. Try again in 1 hour.")
