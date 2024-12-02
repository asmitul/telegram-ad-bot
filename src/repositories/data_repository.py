# src/repositories/data_repository.py
from typing import List, Optional, Set
from telegram.ext import Application
from src.models.ad import Advertisement
from src.models.user import User
from src.models.chat_group import ChatGroup  # 更新导入路径
from src.models.banned_word import BannedWord
import uuid
from datetime import datetime

from src.utils.logger import log_error, log_info, log_warning

class DataRepository:
    def __init__(self, application: Application):
        self.app = application
        self._init_data_structure()
    
    def _init_data_structure(self) -> None:
        """初始化数据结构"""
        if 'groups' not in self.app.bot_data:
            self.app.bot_data['groups'] = {}
        if 'settings' not in self.app.bot_data:
            self.app.bot_data['settings'] = {}
        if 'users' not in self.app.bot_data:
            self.app.bot_data['users'] = {}
        if 'ads' not in self.app.bot_data:
            self.app.bot_data['ads'] = {}
        if 'banned_words' not in self.app.bot_data:
            self.app.bot_data['banned_words'] = []
    
    # 广告相关方法
    async def save_ad(self, ad: Advertisement) -> bool:
        """保存广告"""
        if not ad.id:
            ad.id = str(uuid.uuid4())
        
        ads = self.app.bot_data.get('advertisements', [])
        ads_dict = [a for a in ads if a.get('id') != ad.id]
        ads_dict.append(ad.to_dict())
        self.app.bot_data['advertisements'] = ads_dict
        
        return True
    
    async def get_ad(self, ad_id: str) -> Optional[Advertisement]:
        """获取单个广告"""
        ads = self.app.bot_data.get('advertisements', [])
        for ad in ads:
            if ad.get('id') == ad_id:
                return Advertisement.from_dict(ad)
        return None
    
    async def get_all_ads(self) -> List[Advertisement]:
        """获取所有广告"""
        ads = self.app.bot_data.get('advertisements', [])
        return [Advertisement.from_dict(ad) for ad in ads]
    
    async def delete_ad(self, ad_id: str) -> bool:
        """删除广告"""
        try:
            ads = self.app.bot_data.get('advertisements', [])
            # 过滤掉要删除的广告
            filtered_ads = [ad for ad in ads if ad.get('id') != ad_id]
            # 如果长度相同，说明没有找到要删除的广告
            if len(filtered_ads) == len(ads):
                log_warning(f"未找到广告: {ad_id}")
                return False
            # 保存更新后的广告列表
            self.app.bot_data['advertisements'] = filtered_ads
            log_info(f"成功删除广告: {ad_id}")
            return True
        except Exception as e:
            log_error(e, f"删除广告失败: {ad_id}")
            return False
    
    # 用户相关方法
    async def save_user(self, user: User) -> bool:
        """保存用户信息"""
        users = self.app.bot_data.get('users', {})
        users[user.id] = user.to_dict()
        self.app.bot_data['users'] = users
        return True
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """获取用户信息"""
        users = self.app.bot_data.get('users', {})
        if user_id in users:
            return User.from_dict(users[user_id])
        return None
    
    async def get_all_admins(self) -> List[User]:
        """获取所有管理员"""
        users = self.app.bot_data.get('users', {})
        return [User.from_dict(user) for user in users.values() if user.get('is_admin')]
    
    # 群组相关方法
    async def save_group(self, group: ChatGroup) -> bool:
        """保存群组信息"""
        try:
            groups = self.app.bot_data.get('groups', {})
            group_dict = group.to_dict()
            
            # 添加更详细的调试日志
            log_info(f"准备保存群组，原始对象: id={group.id}, is_ad_group={group.is_ad_group}")
            log_info(f"转换为字典后的数据: {group_dict}")
            
            # 删除可能存在的数字键和字符串键
            if group.id in groups:
                del groups[group.id]
            if str(group.id) in groups:
                del groups[str(group.id)]
                
            # 保存数据
            groups[str(group.id)] = group_dict
            self.app.bot_data['groups'] = groups
            
            # 验证保存后的数据
            saved_data = groups[str(group.id)]
            log_info(f"保存到 bot_data 后的数据: {saved_data}")
            
            # 立即验证数据是否正确保存
            verification_data = self.app.bot_data.get('groups', {}).get(str(group.id))
            log_info(f"从 bot_data 重新读取的数据: {verification_data}")
            
            return True
        except Exception as e:
            log_error(e, f"保存群组失败: {group.id}")
            return False
    
    async def get_group(self, group_id: int) -> Optional[ChatGroup]:
        """获取群组信息"""
        try:
            groups = self.app.bot_data.get('groups', {})
            group_data = groups.get(str(group_id))
            
            if group_data:
                group = ChatGroup.from_dict(group_data)
                log_info(f"转换后的群组对象: id={group.id}, is_ad_group={group.is_ad_group}")
                return group
            return None
        except Exception as e:
            log_error(e, f"获取群组失败: {group_id}")
            return None
    
    async def get_ad_groups(self) -> List[ChatGroup]:
        """获取所有广告群"""
        groups = self.app.bot_data.get('groups', {})
        return [ChatGroup.from_dict(group) 
                for group in groups.values() 
                if group.get('is_ad_group')]
    
    async def set_target_group(self, group_id: int) -> bool:
        """设置目标群组"""
        try:
            settings = self.app.bot_data.get('settings', {})
            settings['target_group_id'] = group_id
            self.app.bot_data['settings'] = settings
            log_info(f"设置目标群组成功: {group_id}")
            return True
        except Exception as e:
            log_error(e, f"设置目标群组失败: {group_id}")
            return False
    
    async def set_target_channel(self, channel_id: int) -> bool:
        """设置目标频道"""
        try:
            settings = self.app.bot_data.get('settings', {})
            settings['target_channel_id'] = channel_id
            self.app.bot_data['settings'] = settings
            log_info(f"设置目标频道成功: {channel_id}")
            return True
        except Exception as e:
            log_error(e, f"设置目标频道失败: {channel_id}")
            return False
    
    async def save_banned_word(self, banned_word: BannedWord) -> bool:
        """保存禁言词"""
        try:
            banned_words = self.app.bot_data.get('banned_words', [])
            banned_words.append(banned_word.to_dict())
            self.app.bot_data['banned_words'] = banned_words
            return True
        except Exception as e:
            log_error(e, "保存禁言词失败")
            return False
    
    async def get_all_banned_words(self) -> List[BannedWord]:
        """获取所有禁言词"""
        try:
            banned_words = self.app.bot_data.get('banned_words', [])
            return [BannedWord.from_dict(word) for word in banned_words]
        except Exception as e:
            log_error(e, "获取禁言词列表失败")
            return []
    
    async def delete_banned_word(self, word: str) -> bool:
        """删除禁言词"""
        try:
            banned_words = self.app.bot_data.get('banned_words', [])
            original_length = len(banned_words)
            banned_words = [w for w in banned_words if w['word'] != word]
            if len(banned_words) == original_length:
                return False
            self.app.bot_data['banned_words'] = banned_words
            return True
        except Exception as e:
            log_error(e, "删除禁言词失败")
            return False
    
    async def get_target_group_id(self) -> Optional[int]:
        """获取目标群组ID"""
        try:
            settings = self.app.bot_data.get('settings', {})
            return settings.get('target_group_id')
        except Exception as e:
            log_error(e, "获取目标群组ID失败")
            return None
    
    async def get_target_channel_id(self) -> Optional[int]:
        """获取目标频道ID"""
        try:
            settings = self.app.bot_data.get('settings', {})
            return settings.get('target_channel_id')
        except Exception as e:
            log_error(e, "获取目标频道ID失败")
            return None