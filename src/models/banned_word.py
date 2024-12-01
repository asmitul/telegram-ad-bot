from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class BannedWord:
    word: str
    created_by: int
    created_at: datetime = datetime.now()
    id: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'word': self.word,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BannedWord':
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data) 