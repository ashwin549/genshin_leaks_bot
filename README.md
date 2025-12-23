# Genshin Impact Leaks Bot

Automatically sends reliable leaks from r/Genshin_Impact_Leaks to Discord every 12 hours.

## Features

- Runs twice daily at 1 AM and 1 PM UTC
- Only sends "Reliable" and "UGC Leak" posts
- Supports multiple Discord webhooks
- Reports posts from the last 12 hours

## Quick Setup

### 1. Get Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Create a script app
3. Save your Client ID and Client Secret

### 2. Get Discord Webhook

1. Discord channel → Edit Channel → Integrations → Webhooks
2. Create webhook and copy the URL

### 3. Configure Repository

Add these secrets in Settings → Secrets and variables → Actions:
- `CLIENT_ID` - Your Reddit client ID
- `CLIENT_SECRET` - Your Reddit client secret  
- `USER_AGENT` - Any string like "GenshinLeaksBot/1.0"
- `DISCORD_WEBHOOK_URL` - Your Discord webhook URL

For multiple channels, separate webhooks with commas.

### 4. Enable Actions (Private Repos Only)

Settings → Actions → General → Allow all actions (You may need to set up billing, even though i doubt this will ever cross the free threshold. Keep it public if you dont want to do that)

## Usage

The bot runs automatically twice daily. To test manually:
- Go to Actions tab → Run workflow

## Customization

**Change schedule** - Edit `.github/workflows/daily-leaks.yml`:
```yaml
cron: "0 1,13 * * *"  # hour 1 and 13 (1 AM & 1 PM UTC)
```

**Change subreddit/flairs** - Edit `app/leaksbot.py`:
```python
SUBREDDIT = "Genshin_Impact_Leaks"
ALLOWED_FLAIRS = ["Reliable", "UGC Leak"]
```

## Troubleshooting

**Scheduled runs not working?** Make sure Actions are enabled and the repo is active (for private repos). It may not follow schedule perfectly, and there might be delays.

**No posts sent?** Check that posts exist with the correct flairs in the last 12 hours
