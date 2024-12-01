from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler as TelegramMessageHandler,
    filters
)
from src.api.handlers.admin_handlers import AdminHandler
from src.api.handlers.ad_handlers import AdHandler
from src.api.handlers.message_handlers import MessageHandler as CustomMessageHandler

def register_handlers(application: Application) -> None:
    """注册所有处理器"""
    # 创建处理器实例
    admin_handler = AdminHandler(application)
    ad_handler = AdHandler(application)
    message_handler = CustomMessageHandler(application)

    # 注册错误处理器
    application.add_error_handler(message_handler.handle_bot_error)
    
    # 注册管理员命令
    application.add_handler(CommandHandler("admin", admin_handler.handle_admin_command))
    application.add_handler(CommandHandler("set_target", admin_handler.handle_set_target_command))
    application.add_handler(CommandHandler("remove_admin", admin_handler.handle_remove_admin))
    application.add_handler(CommandHandler("set_target_channel", admin_handler.handle_set_target_channel))
    
    # 注册广告命令
    application.add_handler(CommandHandler("add_ad", ad_handler.handle_add_ad))
    application.add_handler(CommandHandler("list_ads", ad_handler.handle_list_ads))
    application.add_handler(CommandHandler("delete_ad", ad_handler.handle_delete_ad))
    
    # 注册消息处理器
    application.add_handler(TelegramMessageHandler(
        filters.PHOTO | filters.VIDEO | filters.REPLY,
        ad_handler.handle_ad_media
    ))

    application.add_handler(TelegramMessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler.handle_new_message
    ))

    # 注册新成员处理器
    application.add_handler(TelegramMessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        message_handler.handle_new_member
    ))

    # 注册帮助命令
    application.add_handler(CommandHandler("help", admin_handler.handle_help_command))