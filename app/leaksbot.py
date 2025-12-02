import os
import json
import asyncio
import praw
import discord
from discord.ext import commands
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment
load_dotenv()

# ---- Reddit Credentials ----
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

SUBREDDIT = "Genshin_Impact_Leaks"
ALLOWED_FLAIRS = ["Reliable", "UGC Leak"]

# ---- Local DB ----
DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"channel_id": None}, f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# ---- Discord Bot ----
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

executor = ThreadPoolExecutor(max_workers=1)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(start_reddit_thread())
    print(f"🔄 Watching r/{SUBREDDIT} for flairs: {ALLOWED_FLAIRS}")


@bot.command()
async def enable(ctx):
    db["channel_id"] = ctx.channel.id
    save_db(db)
    await ctx.send("Enabled! I will now post new leaks in this channel.")


@bot.command()
async def disable(ctx):
    db["channel_id"] = None
    save_db(db)
    await ctx.send("Disabled. I will stop posting leaks. Type !enable to restart")


# ---- Reddit Thread Runner ----
def reddit_stream(callback):
    """Runs in background thread. Calls callback(post) for each new post."""
    subreddit = reddit.subreddit(SUBREDDIT)
    for post in subreddit.stream.submissions(skip_existing=True):
        callback(post)


async def start_reddit_thread():
    """Starts sync Reddit stream inside executor thread."""
    loop = asyncio.get_running_loop()

    def handle_post(post):
        # Convert sync callback into async coroutine safely
        asyncio.run_coroutine_threadsafe(process_post(post), loop)

    # Start background thread
    await loop.run_in_executor(executor, reddit_stream, handle_post)


# ---- Process Reddit Posts (async-safe) ----
async def process_post(post):
    flair = post.link_flair_text

    if flair not in ALLOWED_FLAIRS:
        print(f"Skipped → {post.title} [{flair}]")
        return

    channel_id = db.get("channel_id")
    if not channel_id:
        print("⚠ No channel selected. Waiting for !enable...")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        print("⚠ Bot cannot access saved channel.")
        return

    url = (
        post.url
        .replace("reddit.com", "rxddit.com")
        .replace("redd.it", "rxdd.it")
    )

    msg = f"**[{flair}] New post in r/{SUBREDDIT}:**\n{post.title}\n{url}"

    await channel.send(msg)
    print(f"Sent → {post.title}  | Flair={flair}")


# ---- Run Bot ----
bot.run(os.getenv("DISCORD_TOKEN"))
