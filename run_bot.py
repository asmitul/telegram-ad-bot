from dotenv import load_dotenv
import os
from src.bot import main

if __name__ == "__main__":
    load_dotenv()  # 加载 .env 文件
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("请设置环境变量 TELEGRAM_BOT_TOKEN")
    
    main(token)
