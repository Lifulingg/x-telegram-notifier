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
        r = requests.post(url, json=payload, timeout=10)
        print(f"Telegram 发送状态: {r.status_code}")
    except Exception as e:
        print(f"Telegram 发送失败: {e}")

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    r = requests.get(url, headers=headers)
    print(f"获取用户 @{username}: {r.status_code}")
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

    # 测试时加上自己的账号
    test_accounts = ACCOUNTS + ["lifulin123"]

    for username in test_accounts:
        user_id = get_user_id(username)
        if not user_id:
            continue

        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at,referenced_tweets"
        r = requests.get(url, headers=headers)
        print(f"获取 @{username} 推文状态: {r.status_code}")

        if r.status_code != 200:
            continue

        tweets = r.json().get("data", [])
        print(f"@{username} 共获取到 {len(tweets)} 条推文")

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

    print("本次运行结束")

if __name__ == "__main__":
    main()
