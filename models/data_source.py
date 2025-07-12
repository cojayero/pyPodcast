"""
Modelo de fuente de datos
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DataSource:
    """Modelo para una fuente de datos"""
    id: Optional[int]
    name: str
    type: str  # 'youtube', 'rss', 'web'
    url: str
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
    active: bool = True
    last_check: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def display_name(self) -> str:
        """Nombre para mostrar en la UI"""
        return self.name if self.name else self.url
    
    @property
    def type_display(self) -> str:
        """Tipo para mostrar en la UI"""
        type_mapping = {
            'youtube': 'Canal YouTube',
            'rss': 'Feed RSS',
            'web': 'Página Web'
        }
        return type_mapping.get(self.type, self.type)
    
    def __str__(self) -> str:
        return f"{self.display_name} ({self.type_display})"
