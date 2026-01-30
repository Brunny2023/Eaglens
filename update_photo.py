import asyncio
from telegram import Bot
from config import TELEGRAM_TOKEN

async def set_profile_photo():
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        with open("eaglens_logo.png", "rb") as photo:
            await bot.set_chat_photo(chat_id="@EaglensBot", photo=photo) # Note: This usually requires the bot to be an admin or using set_my_name/set_my_description style logic for personal bots
            # Actually, for a bot's own profile photo, the standard way is via BotFather or set_chat_photo if it's in a group.
            # However, the Telegram API has `set_my_name`, `set_my_description`, but NOT `set_my_photo` directly in the same way.
            # Profile photos for bots are typically set via @BotFather.
            # I will try to use the `set_chat_photo` on a dummy call or explain to the user.
            print("Note: Bot profile photos are typically set via @BotFather.")
            print("I have generated the logo for you to upload to @BotFather.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Since I can't easily 'log in' as the user to BotFather, I will provide the image for the user.
    pass
