import asyncio
import csv
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import discord
import feedparser
import html2text
from discord import TextChannel
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read environment variables
TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["CHANNEL_ID"])
DB_FILE = "data/latest_entries.json"

# Create data directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# Read RSS feeds from a file
with open("feeds.csv", "r") as f:
    reader = csv.reader(f)
    FEED_URLS = [row for row in reader][1:]  # Skip the header row

logger.info(f"Loaded {len(FEED_URLS)} feeds from feeds.csv")


# Load the latest entries from the database
def load_latest_entries():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        return {}


def save_latest_entries(data: dict):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)


latest_entries = load_latest_entries()

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content

bot = commands.Bot(command_prefix="!", intents=intents)


def safe_parse_feed(name: str, url: str):
    try:
        return name, feedparser.parse(url)
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return name, feedparser.FeedParserDict()


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user.name}")  # type: ignore
    check_feeds.start()


@tasks.loop(seconds=30)
async def check_feeds():
    loop = asyncio.get_event_loop()
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        logger.error(f"Channel with ID {CHANNEL_ID} not found.")
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks_list = [
            loop.run_in_executor(executor, safe_parse_feed, name, url)
            for name, url in FEED_URLS
        ]
        feeds = await asyncio.gather(*tasks_list)

    for name, feed in feeds:
        url = feed.href
        if not feed.entries:
            continue

        latest_feed_entry = feed.entries[0]  # Get the most recent entry
        entry_id = (
            latest_feed_entry.get("id")
            or latest_feed_entry.get("guid")
            or latest_feed_entry.get("link")
            or latest_feed_entry.get("title")
        )

        if not entry_id:
            logger.warning(f"Could not find unique ID for entry in feed {url}")
            continue

        stored_entry_id = latest_entries.get(url)

        if stored_entry_id is None:
            # First time seeing this feed; send the latest entry
            latest_entries[url] = entry_id
            logger.info(f"First run for feed {url}, sending latest entry")
            await send_entry_to_discord(name, latest_feed_entry, channel)  # type: ignore
            logger.info(f"Sent entry: {latest_feed_entry.get('title', 'No Title')}")
        elif stored_entry_id != entry_id:
            # Check to see if the entry contains the text THIS IS A SCHEDULED EVENT
            if (
                "this is a scheduled event"
                in str((latest_feed_entry.get("title", "") or "")).lower()
            ):
                logger.info(
                    f"Skipping scheduled event: {latest_feed_entry.get('title', 'No Title')}"
                )
                continue
            # New entry found; send it and update the stored entry ID
            latest_entries[url] = entry_id
            logger.info(f"New entry found for feed {url}, sending it")
            await send_entry_to_discord(name, latest_feed_entry, channel)  # type: ignore
            logger.info(f"Sent entry: {latest_feed_entry.get('title', 'No Title')}")
        else:
            # No new entry
            logger.info(f"No new entries for feed {url}")

    # Save the updated latest entries to the database after processing all feeds
    save_latest_entries(latest_entries)


async def send_entry_to_discord(name: str, entry: dict, channel: TextChannel):
    title = f'{name} - {entry.get("title", "No Title")}'
    description = entry.get("description", "No Description")
    link = entry.get("link", "No Link")
    timestamp = entry.get("pubDate") or entry.get("published") or entry.get("updated")

    # Convert HTML description to Markdown
    markdown_description = html2text.html2text(description)

    embed = discord.Embed(title=title, url=link, description=markdown_description)
    if timestamp:
        embed.set_footer(text=timestamp)
    await channel.send(embed=embed)


bot.run(TOKEN)
