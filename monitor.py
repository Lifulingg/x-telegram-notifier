import os
import requests
import json

print("=== X to Telegram 脚本开始运行 ===")

BEARER = os.getenv("TWITTER_BEARER_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ACCOUNTS = [a.strip() for a in os.getenv("ACCOUNTS", "").split(",") if a.strip()]

print(f"监控账号: {ACCOUNTS}")
print(f"Chat ID: {CHAT_ID}")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print(f"Telegram 发送结果: {r.status_code}")
    except Exception as e:
        print(f"Telegram 发送异常: {e}")

headers = {"Authorization": f"Bearer {BEARER}"}

for username in ACCOUNTS:
    print(f"\n--- 处理账号: @{username} ---")
    # 获取用户ID
    r = requests.get(f"https://api.twitter.com/2/users/by/username/{username}", headers=headers)
    print(f"获取用户ID 状态: {r.status_code}")
    if r.status_code != 200:
        continue
    
    user_id = r.json()["data"]["id"]
    
    # 获取最新推文
    r = requests.get(f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=3", headers=headers)
    print(f"获取推文 状态: {r.status_code}")
    
    if r.status_code == 200:
        tweets = r.json().get("data", [])
        print(f"获取到 {len(tweets)} 条推文")
        for tweet in tweets:
            text = tweet.get("text", "")[:300]
            link = f"https://x.com/{username}/status/{tweet['id']}"
            message = f"<b>🔔 @{username}</b>\n\n{text}\n\n🔗 <a href='{link}'>查看</a>"
            send_telegram(message)

print("=== 脚本运行结束 ===")
