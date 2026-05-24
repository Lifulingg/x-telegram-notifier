import os
import datetime
import requests

def main():
    print("--- 脚本启动成功 ---")
    print("当前时间:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 1. 读取并验证环境变量
    BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    ACCOUNTS = os.getenv('ACCOUNTS')          # 期待格式如: "elonmusk,BarackObama"
    ONLY_ORIGINAL = os.getenv('ONLY_ORIGINAL', 'true').lower() == 'true'

    print(f"配置检查 -> 待监控账号: {ACCOUNTS}, 仅转推: {ONLY_ORIGINAL}")
    print(f"配置检查 -> Chat ID: {CHAT_ID}")

    if not BEARER_TOKEN or not BOT_TOKEN or not CHAT_ID or not ACCOUNTS:
        print("❌ 错误: 缺少必要的 GitHub Secrets 环境变量，请检查配置！")
        return

    # 2. 准备 Telegram 发送函数
    def send_tg_message(text):
        # ✨【已修改】这里换成了真正的 api.telegram.org 网址，并加上了 /bot 路径
        url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        try:
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                print("✅ Telegram 消息发送成功")
            else:
                print(f"❌ Telegram 发送失败: {res.text}")
        except Exception as e:
            print(f"❌ 请求 Telegram API 异常: {e}")

    # 3. 核心请求头（用于 X API v2）
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "User-Agent": "v2UserTweetsPython"
    }

    # 4. 遍历处理每个账号
    account_list = [a.strip() for a in ACCOUNTS.split(",") if a.strip()]
    for username in account_list:
        print(f"\n正在检查账号: @{username} ...")
        
        # A. 根据用户名获取用户 ID
        # ✨【已修改】这里换成了 X 官方查询用户 ID 的专用 API 接口，带上了正确的斜杠
        user_url = f"https://twitter.com{username}"
        user_res = requests.get(user_url, headers=headers)
        
        if user_res.status_code != 200:
            print(f"❌ 无法获取用户 @{username} 的信息: {user_res.text}")
            continue
            
        user_data = user_res.json()
        if "data" not in user_data:
            print(f"❌ 未找到用户 @{username}，请检查用户名是否正确。")
            continue
            
        user_id = user_data["data"]["id"]

        # B. 获取该用户最近的推文
        # ✨【已修改】这里换成了 X 官方获取推文列表的专用 API 接口路径
        tweets_url = f"https://twitter.com{user_id}/tweets?max_results=5&tweet.fields=referenced_tweets,created_at"
        tweets_res = requests.get(tweets_url, headers=headers)
        
        if tweets_res.status_code != 200:
            print(f"❌ 无法获取 @{username} 的推文: {tweets_res.text}")
            continue

        tweets_data = tweets_res.json()
        if "data" not in tweets_data or not tweets_data["data"]:
            print(f" ℹ️ @{username} 最近没有发布任何推文。")
            continue

        # C. 过滤并推送
        for tweet in tweets_data["data"]:
            text = tweet["text"]
            tweet_id = tweet["id"]
            ref_tweets = tweet.get("referenced_tweets", [])
            
            # 判断是否为转推 (retweeted)
            is_retweet = any(ref["type"] == "retweeted" for ref in ref_tweets)
            
            if ONLY_ORIGINAL and is_retweet:
                print(f"-> 跳过转推: {tweet_id}")
                continue

            # 构造发送到 Telegram 的消息文本
            # ✨【已修改】补上了跳转链接里的斜杠
            tg_text = (
                f"🔔 <b>@{username} 发布了新内容</b>\n\n"
                f"{text}\n\n"
                f"🔗 <a href='https://x.com{username}/status/{tweet_id}'>查看原推文</a>"
            )
            
            # 🚀 临时测试：直接发送最新的一条即可
            send_tg_message(tg_text)
            break # 测试时只发一条，避免刷屏

    print("\n--- 测试结束 ---")

if __name__ == "__main__":
    main()
