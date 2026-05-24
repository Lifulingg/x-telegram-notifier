print("=== 脚本成功启动 ===")
print("当前时间:", __import__('datetime').datetime.now())

import os
print("ACCOUNTS =", os.getenv("ACCOUNTS"))
print("Chat ID =", os.getenv("TELEGRAM_CHAT_ID"))

print("=== 测试结束 ===")
