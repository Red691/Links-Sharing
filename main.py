import asyncio
from bot import Bot

async def main():
    bot = Bot()
    await bot.start()               # No run(), no use_qr crash
    await asyncio.Event().wait()    # Python async idle

if __name__ == "__main__":
    asyncio.run(main())
