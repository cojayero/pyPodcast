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
            # Limpiar URL (quitar parámetros, etc.)
            clean_url = channel_url.split('?')[0].rstrip('/')
            
            # Casos directos con channel ID
            if '/channel/' in clean_url:
                channel_id = clean_url.split('/channel/')[-1]
                if len(channel_id) == 24 and channel_id.startswith('UC'):
                    logger.info(f"Channel ID directo: {channel_id}")
                    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
            # URLs con username (formato antiguo)
            elif '/user/' in clean_url:
                username = clean_url.split('/user/')[-1]
                logger.info(f"Username encontrado: {username}")
                return f"https://www.youtube.com/feeds/videos.xml?user={username}"
            
            # URLs con handle (formato nuevo @username)
            elif '/@' in clean_url:
                handle = clean_url.split('/@')[-1]
                logger.info(f"Handle encontrado: @{handle}")
                
                # Intentar primero con el handle como user
                feed_url = f"https://www.youtube.com/feeds/videos.xml?user={handle}"
                if self.validate_feed_url(feed_url):
                    return feed_url
                
                # Si falla, buscar el channel ID
                return self._get_channel_id_from_custom_url(clean_url)
            
            # URLs con /c/ (nombres personalizados)
            elif '/c/' in clean_url:
                custom_name = clean_url.split('/c/')[-1]
                logger.info(f"Nombre personalizado /c/: {custom_name}")
                
                # Intentar convertir /c/ a /@
                modern_url = f"https://www.youtube.com/@{custom_name}"
                logger.info(f"Intentando URL moderna: {modern_url}")
                
                try:
                    return self.get_youtube_rss_url(modern_url)
                except Exception:
                    logger.warning(f"Conversión a URL moderna falló, intentando método tradicional")
                    return self._get_channel_id_from_custom_url(clean_url)
            
            # URLs sin formato específico (ej: youtube.com/TEDTalks)
            elif 'youtube.com/' in clean_url:
                # Extraer el nombre del canal
                channel_name = clean_url.split('youtube.com/')[-1].split('/')[0].split('?')[0]
                logger.info(f"Nombre de canal extraído: {channel_name}")
                
                # Intentar formatos modernos primero
                modern_attempts = [
                    f"https://www.youtube.com/@{channel_name}",
                    f"https://www.youtube.com/c/{channel_name}",
                    f"https://www.youtube.com/user/{channel_name}"
                ]
                
                for attempt_url in modern_attempts:
                    try:
                        logger.info(f"Intentando formato: {attempt_url}")
                        return self.get_youtube_rss_url(attempt_url)
                    except Exception as e:
                        logger.debug(f"Falló {attempt_url}: {e}")
                        continue
                
                # Si todos los formatos modernos fallan, intentar buscar en la página original
                return self._get_channel_id_from_custom_url(clean_url)
            
            else:
                raise ValueError(f"Formato de URL de YouTube no reconocido: {channel_url}")
                
        except Exception as e:
            logger.error(f"Error obteniendo URL de RSS de YouTube: {e}")
            raise
    
    def _get_channel_id_from_custom_url(self, channel_url: str) -> str:
        """Obtiene channel ID desde URL personalizada de YouTube"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Intentar primero con seguimiento de redirecciones
            response = requests.get(channel_url, headers=headers, timeout=self.timeout, allow_redirects=True)
            
            # Si hay una redirección a una URL con channel ID, usarla
            if response.url != channel_url and '/channel/' in response.url:
                channel_id = response.url.split('/channel/')[-1].split('/')[0].split('?')[0]
                if len(channel_id) == 24 and channel_id.startswith('UC'):
                    logger.info(f"Channel ID encontrado por redirección: {channel_id}")
                    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
            # Si hay una redirección a una URL con @handle, usar recursión
            if response.url != channel_url and '/@' in response.url:
                logger.info(f"Redirección a handle encontrada: {response.url}")
                return self.get_youtube_rss_url(response.url)
            
            response.raise_for_status()
            content = response.text
            
            # Múltiples patrones para buscar el channel ID
            patterns = [
                r'"channelId":"([^"]+)"',
                r'"externalId":"([^"]+)"',
                r'"browseId":"([^"]+)"',
                r'channel/([^/"]+)',
                r'"webCommandMetadata":{"url":"/channel/([^"]+)"',
                r'"navigationEndpoint":{"commandMetadata":{"webCommandMetadata":{"url":"/channel/([^"]+)"'
            ]
            
            import re
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    channel_id = match.group(1)
                    # Verificar que sea un ID válido (24 caracteres alfanuméricos)
                    if len(channel_id) == 24 and channel_id.startswith('UC'):
                        logger.info(f"Channel ID encontrado: {channel_id}")
                        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
            # Intentar con método alternativo usando la API de YouTube
            logger.warning("No se encontró channel ID en HTML, intentando método alternativo...")
            return self._get_channel_id_alternative(channel_url)
            
        except Exception as e:
            logger.error(f"Error obteniendo channel ID: {e}")
            raise
    
    def _get_channel_id_alternative(self, channel_url: str) -> str:
        """Método alternativo para obtener channel ID"""
        try:
            # Intentar extraer directamente de la URL si es posible
            if '/channel/' in channel_url:
                channel_id = channel_url.split('/channel/')[-1].split('/')[0].split('?')[0]
                if len(channel_id) == 24 and channel_id.startswith('UC'):
                    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
            # Para URLs con @ (nuevas URLs de YouTube)
            if '/@' in channel_url:
                # Extraer el handle
                handle = channel_url.split('/@')[-1].split('/')[0].split('?')[0]
                logger.info(f"Handle encontrado: {handle}")
                
                # Intentar acceso directo al feed con el handle
                potential_feeds = [
                    f"https://www.youtube.com/feeds/videos.xml?user={handle}",
                    f"https://www.youtube.com/@{handle}/videos.rss"
                ]
                
                for feed_url in potential_feeds:
                    if self.validate_feed_url(feed_url):
                        logger.info(f"Feed RSS encontrado: {feed_url}")
                        return feed_url
            
            # Si todo falla, intentar con un método más agresivo
            return self._extract_channel_id_from_page_source(channel_url)
            
        except Exception as e:
            logger.error(f"Error en método alternativo: {e}")
            raise ValueError("No se pudo obtener el channel ID con ningún método")
    
    def _extract_channel_id_from_page_source(self, channel_url: str) -> str:
        """Extrae channel ID usando múltiples estrategias"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(channel_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            content = response.text
            
            # Buscar en metadatos
            import re
            
            # Buscar en meta tags
            meta_patterns = [
                r'<meta property="og:url" content="https://www\.youtube\.com/channel/([^"]+)"',
                r'<meta name="channelId" content="([^"]+)"',
                r'<link rel="canonical" href="https://www\.youtube\.com/channel/([^"]+)"'
            ]
            
            for pattern in meta_patterns:
                match = re.search(pattern, content)
                if match:
                    channel_id = match.group(1)
                    if len(channel_id) == 24 and channel_id.startswith('UC'):
                        logger.info(f"Channel ID encontrado en metadatos: {channel_id}")
                        return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
            raise ValueError("No se pudo extraer channel ID del código fuente")
            
        except Exception as e:
            logger.error(f"Error extrayendo channel ID del código fuente: {e}")
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
