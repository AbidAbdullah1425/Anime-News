import asyncio
import feedparser
from telegram import Bot
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import configuration variables
from config import TELEGRAM_TOKEN, CHANNEL_ID, RSS_URL

bot = Bot(token=TELEGRAM_TOKEN)

# Global variable to control fetching state
is_fetching = False

async def fetch_and_send_news():
    global is_fetching
    while is_fetching:
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            image_url = get_thumbnail_url(entry)
            caption = f"{title}\n\n💫🌵 - {CHANNEL_ID}"

            if image_url:
                try:
                    await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption)
                except Exception as e:
                    print(f"Failed to send photo: {e}")
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=caption)

            await asyncio.sleep(5)  # Delay between messages

def get_thumbnail_url(entry):
    if hasattr(entry, 'media_thumbnail'):
        return entry.media_thumbnail[0]['url']
    return None

@Client.on_message(filters.command('animenewson'))
async def start_fetching(client: Client, message):
    global is_fetching
    if not is_fetching:
        is_fetching = True
        await message.reply_text("Fetching anime news started!")
        asyncio.create_task(fetch_and_send_news())
    else:
        await message.reply_text("Already fetching anime news.")

@Client.on_message(filters.command('animenewsoff'))
async def stop_fetching(client: Client, message):
    global is_fetching
    if is_fetching:
        is_fetching = False
        await message.reply_text("Fetching anime news stopped.")
    else:
        await message.reply_text("Not currently fetching anime news.")

