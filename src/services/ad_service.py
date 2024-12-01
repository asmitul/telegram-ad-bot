from typing import List, Optional
from src.models.ad import Advertisement
from src.repositories.data_repository import DataRepository
from src.utils.logger import log_info, log_error
import random

class AdService:
    def __init__(self, repository: DataRepository):
        self.repository = repository
    
    async def create_ad(self, 
                       media_id: str,
                       media_type: str,
                       welcome_text: str,
                       ad_text: str,
                       buttons: List[dict]) -> Optional[Advertisement]:
        """创建新广告"""
        try:
            ad = Advertisement(
                media_id=media_id,
                media_type=media_type,
                welcome_text=welcome_text,
                ad_text=ad_text,
                buttons=buttons
            )
            
            success = await self.repository.save_ad(ad)
            if success:
                log_info(f"创建广告成功: {ad.id}")
                return ad
            return None
        except Exception as e:
            log_error(e, "创建广告失败")
            return None
    
    async def get_all_ads(self) -> List[Advertisement]:
        """获取所有广告"""
        try:
            return await self.repository.get_all_ads()
        except Exception as e:
            log_error(f"获取广告列表失败: {e}")
            return []
    
    async def delete_ad(self, ad_id: str) -> bool:
        """删除广告"""
        try:
            success = await self.repository.delete_ad(ad_id)
            if success:
                log_info(f"删除广告成功: {ad_id}")
            return success
        except Exception as e:
            log_error(e, "删除广告失败")
            return False
    
    async def get_random_ad(self) -> Optional[Advertisement]:
        """获取随机广告"""
        try:
            ads = await self.repository.get_all_ads()
            if not ads:
                return None
            return random.choice(ads)
        except Exception as e:
            log_error(e, "获取随机广告失败")
            return None