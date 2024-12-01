from typing import List, Optional
from src.models.banned_word import BannedWord
from src.repositories.data_repository import DataRepository
from src.utils.logger import log_error, log_info
import uuid

class BannedWordService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
    
    async def add_banned_word(self, word: str, created_by: int) -> bool:
        """添加禁言词"""
        try:
            banned_word = BannedWord(
                id=str(uuid.uuid4()),
                word=word.lower(),
                created_by=created_by
            )
            return await self.repository.save_banned_word(banned_word)
        except Exception as e:
            log_error(e, "添加禁言词失败")
            return False
    
    async def get_all_banned_words(self) -> List[BannedWord]:
        """获取所有禁言词"""
        return await self.repository.get_all_banned_words()
    
    async def delete_banned_word(self, word: str) -> bool:
        """删除禁言词"""
        return await self.repository.delete_banned_word(word)
    
    async def check_message(self, text: str) -> bool:
        """检查消息是否包含禁言词"""
        try:
            banned_words = await self.get_all_banned_words()
            text = text.lower()
            return any(word.word in text for word in banned_words)
        except Exception as e:
            log_error(e, "检查禁言词失败")
            return False 