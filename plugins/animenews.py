import asyncio
import feedparser
from database.database import database  # Ensure you import the database class
from telegram import Bot
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Import configuration variables
from config import TELEGRAM_TOKEN, CHANNEL_ID, RSS_URL

bot = Bot(token=TELEGRAM_TOKEN)

# Global variable to control fetching state
is_fetching = False

async def fetch_and_send_news():
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        print(entry)

        title = entry.title
        link = entry.link

        # Check for duplicates using the link
        if database.check_duplicate(link):
            print(f"Duplicate news found: {link}. Skipping...")
            continue  # Skip sending this news

        # Get the thumbnail image URL
        image_url = get_thumbnail_url(entry)

        # Prepare the message
        caption = f"{title}\n\n💫🌵 - {CHANNEL_ID}"

        if image_url:
            print(f"Sending photo: {image_url}")
            try:
                await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=caption)
            except Exception as e:
                print(f"Failed to send photo: {e}")
        else:
            print("No valid image URL found, sending message only.")
            await bot.send_message(chat_id=CHANNEL_ID, text=caption)

        # Insert the new news link into the database
        database.insert_news(link)

        # Delay between messages to avoid floo
ding
        await asyncio.sleep(5)

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

