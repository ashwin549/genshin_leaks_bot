import os
import praw
import requests
from datetime import datetime, timedelta, timezone

# Reddit credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")

# Webhook URL (user provides)
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Subreddit
SUBREDDIT = "Genshin_Impact_Leaks"
ALLOWED_FLAIRS = ["Reliable", "UGC Leak"]

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def send(content):
    requests.post(WEBHOOK_URL, json={"content": content[:2000]})

def main():
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)

    send(f"**Daily Genshin Leaks Report ({yesterday.date()} → {now.date()})**")

    count = 0
    subreddit = reddit.subreddit(SUBREDDIT)

    for post in subreddit.new(limit=100):
        post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)

        if post_time < yesterday:
            continue

        flair = post.link_flair_text
        if flair not in ["Reliable", "UGC Leak"]:
            continue

        # Rewrite reddit → rxddit
        url = (
            post.url
            .replace("reddit.com", "rxddit.com")
        )

        msg = f"**[{flair}] {post.title}**\n{url}"
        send(msg)
        count += 1

    if count == 0:
        send("No new Reliable / UGC Leak posts today.")
    else:
        send(f"Done! Sent {count} leak posts.")

if __name__ == "__main__":
    main()
