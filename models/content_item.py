"""
Modelo de item de contenido
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pathlib import Path

@dataclass
class ContentItem:
    """Modelo para un item de contenido"""
    id: Optional[int]
    source_id: int
    title: str
    url: str
    description: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    audio_file: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str = 'nuevo'  # 'nuevo', 'procesado', 'escuchado', 'ignorar'
    published_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    
    @property
    def display_title(self) -> str:
        """Título para mostrar en la UI"""
        return self.title if self.title else "Sin título"
    
    @property
    def status_display(self) -> str:
        """Estado para mostrar en la UI"""
        status_mapping = {
            'nuevo': 'Nuevo',
            'procesado': 'Procesado',
            'escuchado': 'Escuchado',
            'ignorar': 'Ignorar'
        }
        return status_mapping.get(self.status, self.status)
    
    @property
    def has_audio(self) -> bool:
        """Verifica si tiene archivo de audio"""
        if not self.audio_file:
            return False
        return Path(self.audio_file).exists()
    
    @property
    def has_summary(self) -> bool:
        """Verifica si tiene resumen"""
        return bool(self.summary and self.summary.strip())
    
    def __str__(self) -> str:
        return f"{self.display_title} ({self.status_display})"
