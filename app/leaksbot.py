import os
import praw
import requests
import time
from datetime import datetime, timedelta, timezone

# Reddit credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT")

# Multiple webhook URLs (comma-separated)
WEBHOOK_URLS = os.getenv("DISCORD_WEBHOOK_URL").split(",")

# Subreddit
SUBREDDIT = "Genshin_Impact_Leaks"
ALLOWED_FLAIRS = ["Reliable", "UGC Leak"]

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

def send(content):
    """Send a message to all configured webhooks with rate limiting."""
    content = content[:2000]  
    
    for url in WEBHOOK_URLS:
        url = url.strip()
        if not url:
            continue  
        
        try:
            response = requests.post(url, json={"content": content})
            
            # Check for rate limit
            if response.status_code == 429:
                retry_after = response.json().get('retry_after', 1)
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                response = requests.post(url, json={"content": content})
            
            if response.status_code not in [200, 204]:
                print(f"Failed to send to {url}: Status {response.status_code}")
                
        except Exception as e:
            print(f"Failed to send to {url}: {e}")
    
    time.sleep(0.5)  # 500ms between messages=2 per second

def main():
    now = datetime.now(timezone.utc)
    twelve_hours_ago = now - timedelta(hours=12)
    
    send(f"**Genshin Leaks Report (Last 12 Hours)**\n{twelve_hours_ago.strftime('%Y-%m-%d %H:%M UTC')} → {now.strftime('%Y-%m-%d %H:%M UTC')}")
    
    count = 0
    subreddit = reddit.subreddit(SUBREDDIT)
    
    for post in subreddit.new(limit=100):
        post_time = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
        
        if post_time < twelve_hours_ago:
            continue
        
        flair = post.link_flair_text
        if flair not in ALLOWED_FLAIRS:
            continue
        
        url = post.url.replace("reddit.com", "rxddit.com")
        msg = f"**[{flair}] {post.title}**\n{url}"
        send(msg)
        count += 1
    
    if count == 0:
        send("No new Reliable / UGC Leak posts in the last 12 hours.")
    else:
        send(f"Done! Sent {count} leak posts.")

if __name__ == "__main__":
    main()
