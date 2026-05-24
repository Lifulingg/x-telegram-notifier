import os
import requests
import json

# 配置
BEARER = os.getenv("TWITTER_BEARER_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ACCOUNTS = [a.strip() for a in os.getenv("ACCOUNTS", "").split(",")]
ONLY_ORIGINAL = os.getenv("ONLY_ORIGINAL", "true").lower() == "true"

headers = {"Authorization": f"Bearer {BEARER}"}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()["data"]["id"]
    return None

def main():
    state_file = "last_seen.json"
    try:
        with open(state_file) as f:
            last_seen = json.load(f)
    except:
        last_seen = {}

    for username in ACCOUNTS:
        user_id = get_user_id(username)
        if not user_id:
            continue

        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at,referenced_tweets"
        r = requests.get(url, headers=headers)
        
        if r.status_code != 200:
            continue

        tweets = r.json().get("data", [])
        
        for tweet in reversed(tweets):
            tweet_id = tweet["id"]
            if last_seen.get(username) and tweet_id in last_seen[username]:
                continue

            if ONLY_ORIGINAL and tweet.get("referenced_tweets"):
                continue

            text = tweet.get("text", "")[:350]
            if len(tweet.get("text", "")) > 350:
                text += "..."

            link = f"https://x.com/{username}/status/{tweet_id}"
            
            message = f"<b>🔔 @{username}</b>\n\n{text}\n\n🔗 <a href='{link}'>查看原文</a>"
            send_telegram(message)
            
            if username not in last_seen:
                last_seen[username] = []
            last_seen[username].append(tweet_id)
            if len(last_seen[username]) > 20:
                last_seen[username] = last_seen[username][-20:]

    with open(state_file, "w") as f:
        json.dump(last_seen, f)

if __name__ == "__main__":
    main()
