import os
import requests

print("=== 脚本开始运行 ===")

BEARER = os.getenv("TWITTER_BEARER_TOKEN")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ACCOUNTS = [a.strip() for a in os.getenv("ACCOUNTS", "").split(",") if a.strip()]

print("监控账号:", ACCOUNTS)
print("Chat ID:", CHAT_ID)

headers = {"Authorization": f"Bearer {BEARER}"}

for username in ACCOUNTS:
    print(f"\n处理 @{username}")
    try:
        # 获取用户ID
        resp = requests.get(f"https://api.twitter.com/2/users/by/username/{username}", headers=headers)
        print("用户ID请求状态:", resp.status_code)
        
        if resp.status_code == 200:
            user_id = resp.json()["data"]["id"]
            
            # 获取推文
            resp = requests.get(f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=3", headers=headers)
            print("推文请求状态:", resp.status_code)
            
            if resp.status_code == 200:
                for tweet in resp.json().get("data", []):
                    text = tweet.get("text", "")[:250]
                    link = f"https://x.com/{username}/status/{tweet['id']}"
                    msg = f"🔔 @{username}\n\n{text}\n\n{link}"
                    
                    # 发送Telegram
                    tg_resp = requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={"chat_id": CHAT_ID, "text": msg}
                    )
                    print("Telegram发送状态:", tg_resp.status_code)
    except Exception as e:
        print("错误:", str(e))

print("=== 脚本结束 ===")
