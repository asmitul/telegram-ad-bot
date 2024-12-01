from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Advertisement:
    media_id: str
    media_type: str  # 'photo' or 'video'
    welcome_text: str
    ad_text: str
    buttons: List[dict]  # 改为按钮列表
    id: Optional[str] = None
    created_at: datetime = datetime.now()
    
    def to_dict(self) -> dict:
        """将对象转换为字典"""
        return {
            'id': self.id,
            'media_id': self.media_id,
            'media_type': self.media_type,
            'welcome_text': self.welcome_text,
            'ad_text': self.ad_text,
            'buttons': self.buttons,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Advertisement':
        """从字典创建对象"""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)