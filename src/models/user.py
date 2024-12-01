from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: int
    is_admin: bool = False
    joined_at: datetime = datetime.now()
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    def to_dict(self) -> dict:
        """将对象转换为字典"""
        return {
            'id': self.id,
            'is_admin': self.is_admin,
            'joined_at': self.joined_at.isoformat(),
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """从字典创建对象"""
        if 'joined_at' in data and isinstance(data['joined_at'], str):
            data['joined_at'] = datetime.fromisoformat(data['joined_at'])
        return cls(**data)