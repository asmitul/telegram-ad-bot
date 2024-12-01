from typing import Optional, List
from src.models.chat_group import ChatGroup
from src.repositories.data_repository import DataRepository
from src.utils.logger import log_info, log_error, log_warning
from telegram import Message
from datetime import datetime

class MessageService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
    
    async def register_group(self, group_id: int, title: str, group_type: str) -> bool:
        """注册群组"""
        try:
            # 先获取现有的群组信息
            existing_group = await self.repository.get_group(group_id)
            
            if existing_group:
                # 如果群组存在，只更新基本信息
                existing_group.title = title
                existing_group.type = group_type
                group = existing_group
            else:
                # 如果是新群组，创建新的记录
                group = ChatGroup(
                    id=group_id,
                    title=title,
                    type=group_type,
                    is_ad_group=False
                )
            
            success = await self.repository.save_group(group)
            if success:
                log_info(f"注册群组成功: {group_id} ({title})")
            return success
        except Exception as e:
            log_error(e, f"注册群组失败: {group_id}")
            return False
    
    async def get_ad_groups(self) -> List[ChatGroup]:
        """获取所有广告群"""
        try:
            groups = await self.repository.get_ad_groups()
            log_info(f"获取到的广告群数量: {len(groups)}")
            for group in groups:
                log_info(f"广告群信息: ID={group.id}, Title={group.title}, is_ad_group={group.is_ad_group}")
            return groups
        except Exception as e:
            log_error(e, "获取广告群列表失败")
            return []
    
    async def is_ad_group(self, group_id: int) -> bool:
        """检查是否是广告群"""
        try:
            group = await self.repository.get_group(group_id)
            is_ad = group is not None and group.is_ad_group
            log_info(f"群组 {group_id} 是否为广告群: {is_ad}")
            return is_ad
        except Exception as e:
            log_error(e, f"检查广告群状态失败: {group_id}")
            return False
    
    async def set_ad_group(self, group_id: int, is_ad_group: bool = True) -> bool:
        """设置群组的广告群状态"""
        try:
            group = await self.repository.get_group(group_id)
            if not group:
                return False
            
            group.is_ad_group = is_ad_group
            success = await self.repository.save_group(group)
            if success:
                log_info(f"{'设置' if is_ad_group else '取消'}广告群成功: {group_id}")
            return success
        except Exception as e:
            log_error(e, f"设置广告群状态失败: {group_id}")
            return False
    
    async def check_channel_subscription(self, user_id: int, bot) -> bool:
        """检查用户是否关注了目标频道"""
        try:
            # 从设置中获取目标频道ID
            settings = self.repository.app.bot_data.get('settings', {})
            target_channel_id = settings.get('target_channel_id')
            
            if not target_channel_id:
                log_warning("未设置目标频道ID")
                return True
            
            log_info(f"检查用户 {user_id} 是否关注频道 {target_channel_id}")
            
            try:
                # 获取用户在频道中的状态
                member = await bot.get_chat_member(
                    chat_id=target_channel_id,
                    user_id=user_id
                )
                is_member = member.status in ['member', 'administrator', 'creator']
                log_info(f"用户 {user_id} 的频道成员状态: {member.status}")
                return is_member
                
            except Exception as e:
                log_error(e, f"获取用户 {user_id} 的频道成员状态失败")
                return False
                
        except Exception as e:
            log_error(e, "检查频道订阅状态失败")
            return True