# src/bot.py
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    PicklePersistence,
)

from src.api.register_handlers import register_handlers
from src.repositories.data_repository import DataRepository
from src.utils.logger import log_error, log_info
from src.services.scheduler_service import send_random_ad
from src.services.admin_service import AdminService

def main(telegram_token: str):
    persistence = PicklePersistence(filepath="data/bot_database.pkl")
    
    application = (
        ApplicationBuilder()
        .token(telegram_token)
        .concurrent_updates(True)
        .persistence(persistence)
        .build()
    )

    data_manager = DataRepository(application)
    data_manager._init_data_structure()

    register_handlers(application)
    
    job_queue = application.job_queue
    job_queue.run_repeating(send_random_ad, interval=600)

    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            close_loop=False
        )
        log_info("Bot 已启动")
    except KeyboardInterrupt:
        if application.persistence:
            application.persistence.flush()
        application.stop()
    finally:
        log_info("Bot 已停止")