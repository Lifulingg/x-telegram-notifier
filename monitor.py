import os
import requests

print("脚本开始运行")
print("Python 环境正常")

BEARER = os.getenv("TWITTER_BEARER_TOKEN")
print("Bearer Token 长度:", len(BEARER) if BEARER else 0)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ACCOUNTS = [a.strip() for a in os.getenv("ACCOUNTS", "").split(",") if a.strip()]

print("监控账号:", ACCOUNTS)
print("Chat ID:", CHAT_ID)

print("所有配置读取完成")
