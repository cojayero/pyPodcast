"""
Gestor de feeds RSS
"""

import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
from utils.config import config_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class RSSManager:
    """Gestor de feeds RSS"""
    
    def __init__(self):
        self.timeout = config_manager.get('network.timeout', 30)
        self.user_agent = config_manager.get('network.user_agent', 'PyPodcast/1.0.0')
    
    def get_youtube_rss_url(self, channel_url: str) -> str:
        """Convierte URL de canal YouTube a URL de RSS"""
        try:
            if 'youtube.com/channel/' in channel_url:
                # URL con channel ID
                channel_id = channel_url.split('/channel/')[-1].split('/')[0]
                return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
            elif 'youtube.com/c/' in channel_url or 'youtube.com/@' in channel_url:
                # URL con nombre personalizado - necesitamos obtener el channel ID
                return self._get_channel_id_from_custom_url(channel_url)
            
            elif 'youtube.com/user/' in channel_url:
                # URL con username
                username = channel_url.split('/user/')[-1].split('/')[0]
                return f"https://www.youtube.com/feeds/videos.xml?user={username}"
            
            else:
                raise ValueError("URL de YouTube no reconocida")
                
        except Exception as e:
            logger.error(f"Error obteniendo URL de RSS de YouTube: {e}")
            raise
    
    def _get_channel_id_from_custom_url(self, channel_url: str) -> str:
        """Obtiene channel ID desde URL personalizada de YouTube"""
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(channel_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Buscar channel ID en el HTML
            content = response.text
            if 'channelId":"' in content:
                start = content.find('channelId":"') + 12
                end = content.find('"', start)
                channel_id = content[start:end]
                return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
            raise ValueError("No se pudo obtener el channel ID")
            
        except Exception as e:
            logger.error(f"Error obteniendo channel ID: {e}")
            raise
    
    def parse_feed(self, feed_url: str) -> Dict[str, Any]:
        """Parsea un feed RSS y retorna información del canal y entradas"""
        try:
            # Configurar feedparser
            feedparser.USER_AGENT = self.user_agent
            
            # Parsear feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed RSS con errores: {feed.bozo_exception}")
            
            # Información del canal
            channel_info = {
                'title': feed.feed.get('title', 'Sin título'),
                'description': feed.feed.get('description', ''),
                'link': feed.feed.get('link', ''),
                'image_url': self._get_feed_image(feed),
                'last_updated': datetime.now()
            }
            
            # Parsear entradas
            entries = []
            for entry in feed.entries:
                entry_data = {
                    'title': entry.get('title', 'Sin título'),
                    'url': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'summary': entry.get('summary', ''),
                    'published_date': self._parse_date(entry.get('published')),
                    'thumbnail_url': self._get_entry_thumbnail(entry)
                }
                entries.append(entry_data)
            
            return {
                'channel': channel_info,
                'entries': entries,
                'total_entries': len(entries)
            }
            
        except Exception as e:
            logger.error(f"Error parseando feed RSS {feed_url}: {e}")
            raise
    
    def _get_feed_image(self, feed) -> str:
        """Extrae URL de imagen del feed"""
        try:
            # Probar diferentes ubicaciones de imagen
            if hasattr(feed.feed, 'image') and 'href' in feed.feed.image:
                return feed.feed.image.href
            
            if hasattr(feed.feed, 'image') and 'url' in feed.feed.image:
                return feed.feed.image.url
            
            if hasattr(feed.feed, 'logo'):
                return feed.feed.logo
            
            # Para YouTube, buscar en namespaces
            for key, value in feed.feed.items():
                if 'image' in key.lower() and isinstance(value, str):
                    return value
            
            return None
            
        except Exception:
            return None
    
    def _get_entry_thumbnail(self, entry) -> str:
        """Extrae URL de thumbnail de una entrada"""
        try:
            # Buscar en diferentes ubicaciones
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                if isinstance(entry.media_thumbnail, list) and entry.media_thumbnail:
                    return entry.media_thumbnail[0].get('url')
                elif hasattr(entry.media_thumbnail, 'url'):
                    return entry.media_thumbnail.url
            
            # Para YouTube RSS
            if hasattr(entry, 'media_group') and entry.media_group:
                if hasattr(entry.media_group, 'media_thumbnail'):
                    thumbnails = entry.media_group.media_thumbnail
                    if thumbnails and isinstance(thumbnails, list):
                        return thumbnails[0].get('url')
            
            # Buscar en links
            for link in getattr(entry, 'links', []):
                if link.get('type', '').startswith('image/'):
                    return link.get('href')
            
            return None
            
        except Exception:
            return None
    
    def _parse_date(self, date_string: str) -> datetime:
        """Parsea fecha de entrada RSS"""
        if not date_string:
            return None
        
        try:
            # feedparser ya parsea las fechas
            import time
            if hasattr(feedparser, '_parse_date'):
                parsed = feedparser._parse_date(date_string)
                if parsed:
                    return datetime.fromtimestamp(time.mktime(parsed))
            
            # Fallback manual
            from dateutil import parser
            return parser.parse(date_string)
            
        except Exception:
            logger.warning(f"No se pudo parsear fecha: {date_string}")
            return None
    
    def validate_feed_url(self, url: str) -> bool:
        """Valida si una URL es un feed RSS válido"""
        try:
            feed = feedparser.parse(url)
            return not feed.bozo or len(feed.entries) > 0
        except Exception:
            return False
    
    def discover_feeds(self, website_url: str) -> List[str]:
        """Descubre feeds RSS en una página web"""
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(website_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            feeds = []
            
            # Buscar enlaces RSS/Atom
            for link in soup.find_all('link', type=['application/rss+xml', 'application/atom+xml']):
                href = link.get('href')
                if href:
                    # Convertir URL relativa a absoluta
                    feed_url = urljoin(website_url, href)
                    feeds.append(feed_url)
            
            # Buscar enlaces comunes
            common_feed_paths = ['/rss', '/feed', '/rss.xml', '/feed.xml', '/atom.xml']
            for path in common_feed_paths:
                feed_url = urljoin(website_url, path)
                if self.validate_feed_url(feed_url):
                    feeds.append(feed_url)
            
            return list(set(feeds))  # Eliminar duplicados
            
        except Exception as e:
            logger.error(f"Error descubriendo feeds en {website_url}: {e}")
            return []
