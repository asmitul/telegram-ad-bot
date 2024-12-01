from telegram import Update
from telegram.ext import ContextTypes
from src.services.admin_service import AdminService
from src.repositories.data_repository import DataRepository
from src.utils.logger import log_error
from functools import wraps
from typing import Callable, Any

def admin_required(func: Callable) -> Callable:
    """管理员权限装饰器"""
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any):
        if not update.effective_user:
            return
            
        repository = DataRepository(context.application)
        admin_service = AdminService(repository)
        
        if not await admin_service.is_admin(update.effective_user.id):
            await update.message.reply_text("⚠️ 此命令仅管理员可用")
            return
            
        return await func(self, update, context, *args, **kwargs)
    return wrapper

class BaseHandler:
    """基础处理器类，提供通用功能"""
    
    def __init__(self, application):
        self.app = application
        self.repository = DataRepository(application)
    
    async def send_error_message(self, update: Update, message: str) -> None:
        """发送错误消息"""
        try:
            await update.message.reply_text(f"❌ {message}")
        except Exception as e:
            log_error(e, "发送错误消息失败")
    
    async def send_success_message(self, update: Update, message: str) -> None:
        """发送成功消息"""
        try:
            await update.message.reply_text(f"✅ {message}")
        except Exception as e:
            log_error(e, "发送成功消息失败")