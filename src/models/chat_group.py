from dataclasses import dataclass
from datetime import datetime
from typing import Union

@dataclass
class ChatGroup:
    id: int
    title: str
    type: Union[str, object]  # 可以是字符串或 ChatType 对象
    is_ad_group: bool = False
    joined_at: datetime = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'type': str(self.type),  # 将 type 转换为字符串
            'is_ad_group': bool(self.is_ad_group),  # 确保是布尔值
            'joined_at': self.joined_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChatGroup':
        # 创建一个数据的副本，避免修改原始数据
        data_copy = data.copy()
        
        # 确保 is_ad_group 是布尔值
        data_copy['is_ad_group'] = bool(data_copy.get('is_ad_group', False))
        
        # 处理 joined_at
        if 'joined_at' in data_copy and isinstance(data_copy['joined_at'], str):
            data_copy['joined_at'] = datetime.fromisoformat(data_copy['joined_at'])
            
        return cls(**data_copy) 