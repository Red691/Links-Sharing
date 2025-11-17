import base64
import re
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import ADMINS
from pyrogram.errors import UserNotParticipant, FloodWait


# ---------------------- BASE64 ENCODE / DECODE ---------------------- #

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string


async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")


# ---------------------- UPTIME FORMATTER ---------------------- #

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)

        if seconds == 0 and remainder == 0:
            break

        time_list.append(int(result))
        seconds = int(remainder)

    hmm = len(time_list)

    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]

    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "

    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time


# ---------------------- ADMIN CHECK FILTER ---------------------- #
# THIS IS THE FIXED VERSION 🔥

def admin_filter():
    async def _check(_, __, message):
        return message.from_user and message.from_user.id in ADMINS
    return filters.create(_check)

# Now you can use:
# @app.on_message(admin_filter())
# async def my_admin_cmd(client, message):
#     ...
