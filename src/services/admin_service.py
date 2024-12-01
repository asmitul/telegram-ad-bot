from typing import List, Optional, Set
from src.models.user import User
from src.repositories.data_repository import DataRepository
from src.utils.logger import log_info, log_error, log_warning
from datetime import datetime
from telegram.ext import Application

class AdminService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
    
    async def add_admin(self, user_id: int, username: Optional[str] = None) -> bool:
        """添加新管理员"""
        try:
            # 检查用户是否已经是管理员
            existing_user = await self.repository.get_user(user_id)
            if existing_user and existing_user.is_admin:
                log_warning(f"用户 {user_id} 已经是管理员")
                return False
            
            # 创建或更新用户
            user = User(
                id=user_id,
                username=username,
                is_admin=True
            )
            
            success = await self.repository.save_user(user)
            if success:
                log_info(f"添加管理员成功: {user_id}")
            return success
        except Exception as e:
            log_error(e, f"添加管理员失败: {user_id}")
            return False
    
    async def remove_admin(self, user_id: int) -> bool:
        """移除管理员"""
        try:
            user = await self.repository.get_user(user_id)
            if not user:
                return False
            
            user.is_admin = False
            success = await self.repository.save_user(user)
            if success:
                log_info(f"移除管理员成功: {user_id}")
            return success
        except Exception as e:
            log_error(e, f"移除管理员失败: {user_id}")
            return False
    
    async def is_admin(self, user_id: int) -> bool:
        """检查用户是否是管理员"""
        try:
            user = await self.repository.get_user(user_id)
            return user is not None and user.is_admin
        except Exception as e:
            log_error(e, f"检查管理员状态失败: {user_id}")
            return False
    
    async def get_all_admins(self) -> List[User]:
        """获取所有管理员"""
        try:
            return await self.repository.get_all_admins()
        except Exception as e:
            log_error(e, "获取管理员列表失败")
            return []
    
    async def notify_admin_startup(self, application: Application) -> None:
        """在机器人启动时通知第一个管理员"""
        try:
            # 获取所有管理员
            admins = await self.get_all_admins()
            
            if not admins:
                log_warning("没有找到管理员来发送启动通知")
                return
            
            # 获取第一个管理员
            first_admin = admins[0]
            
            # 发送启动通知
            await application.bot.send_message(
                chat_id=first_admin.id,
                text="🤖 机器人已启动并准备就绪！\n"
                     f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            log_info(f"已向管理员 {first_admin.id} 发送启动通知")
            
        except Exception as e:
            log_error(e, "发送启动通知失败")