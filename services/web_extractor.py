"""
Extractor de contenido web
"""

import requests
from bs4 import BeautifulSoup, Comment
import re
from typing import Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from utils.config import config_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class WebExtractor:
    """Extractor de contenido de páginas web"""
    
    def __init__(self):
        self.timeout = config_manager.get('network.timeout', 30)
        self.user_agent = config_manager.get('network.user_agent', 'PyPodcast/1.0.0')
        self.max_content_length = 1000000  # 1MB máximo
    
    def extract_content(self, url: str) -> Dict[str, Any]:
        """Extrae contenido principal de una página web"""
        try:
            # Obtener contenido HTML
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Verificar tamaño del contenido
            if len(response.content) > self.max_content_length:
                logger.warning(f"Contenido muy grande para {url}, truncando...")
                content = response.content[:self.max_content_length]
            else:
                content = response.content
            
            # Parsear HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extraer información
            result = {
                'url': url,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'content': self._extract_main_content(soup),
                'author': self._extract_author(soup),
                'published_date': self._extract_published_date(soup),
                'image_url': self._extract_main_image(soup, url),
                'language': self._extract_language(soup),
                'keywords': self._extract_keywords(soup)
            }
            
            # Limpiar y validar contenido
            result['content'] = self._clean_content(result['content'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error extrayendo contenido de {url}: {e}")
            raise
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrae el título de la página"""
        # Probar diferentes ubicaciones
        selectors = [
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'h1',
            'title',
            '.entry-title',
            '.post-title',
            'article h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()
                
                if title and len(title) > 5:
                    return title
        
        return "Sin título"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extrae la descripción de la página"""
        selectors = [
            'meta[property="og:description"]',
            'meta[name="twitter:description"]',
            'meta[name="description"]',
            '.entry-summary',
            '.post-excerpt'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    desc = element.get('content', '').strip()
                else:
                    desc = element.get_text().strip()
                
                if desc and len(desc) > 10:
                    return desc
        
        return ""
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extrae el contenido principal del artículo"""
        # Eliminar elementos no deseados
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Eliminar comentarios HTML
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Probar selectores comunes para contenido principal
        content_selectors = [
            'article',
            '.entry-content',
            '.post-content',
            '.content',
            '.main-content',
            '#content',
            '.article-body',
            'main',
            '.story-body'
        ]
        
        content_text = ""
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Extraer texto de párrafos
                paragraphs = element.find_all(['p', 'div', 'section'])
                texts = []
                
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50:  # Solo párrafos con contenido sustancial
                        texts.append(text)
                
                if texts:
                    content_text = '\n\n'.join(texts)
                    break
        
        # Fallback: extraer todo el texto de la página
        if not content_text or len(content_text) < 100:
            # Eliminar más elementos no deseados
            for element in soup.find_all(['button', 'form', 'input', 'select']):
                element.decompose()
            
            body = soup.find('body')
            if body:
                paragraphs = body.find_all('p')
                texts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50]
                content_text = '\n\n'.join(texts)
        
        return content_text
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extrae el autor del artículo"""
        selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline',
            '.post-author'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    author = element.get('content', '').strip()
                else:
                    author = element.get_text().strip()
                
                if author:
                    return author
        
        return ""
    
    def _extract_published_date(self, soup: BeautifulSoup) -> str:
        """Extrae la fecha de publicación"""
        selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publishdate"]',
            'time[datetime]',
            '.published',
            '.post-date'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    date = element.get('content', '').strip()
                elif element.name == 'time':
                    date = element.get('datetime', '').strip()
                else:
                    date = element.get_text().strip()
                
                if date:
                    return date
        
        return ""
    
    def _extract_main_image(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extrae la imagen principal del artículo"""
        selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            'article img',
            '.featured-image img',
            '.post-image img'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    img_url = element.get('content', '').strip()
                else:
                    img_url = element.get('src', '').strip()
                
                if img_url:
                    # Convertir URL relativa a absoluta
                    return urljoin(base_url, img_url)
        
        return ""
    
    def _extract_language(self, soup: BeautifulSoup) -> str:
        """Extrae el idioma del contenido"""
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag.get('lang')
        
        meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if meta_lang:
            return meta_lang.get('content', '')
        
        return "es"  # Por defecto español
    
    def _extract_keywords(self, soup: BeautifulSoup) -> str:
        """Extrae palabras clave del contenido"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            return meta_keywords.get('content', '')
        
        return ""
    
    def _clean_content(self, content: str) -> str:
        """Limpia y normaliza el contenido extraído"""
        if not content:
            return ""
        
        # Eliminar espacios múltiples y líneas vacías
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Eliminar caracteres especiales problemáticos
        content = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'áéíóúñÁÉÍÓÚÑ]', '', content)
        
        # Limitar longitud
        max_length = config_manager.get('content.max_summary_length', 5000) * 10
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content.strip()
    
    def is_valid_url(self, url: str) -> bool:
        """Valida si una URL es válida"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def get_content_summary(self, content: str) -> str:
        """Genera un resumen básico del contenido"""
        if not content:
            return ""
        
        # Dividir en párrafos
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # Tomar los primeros párrafos más sustanciales
        summary_parts = []
        total_length = 0
        max_length = config_manager.get('content.max_summary_length', 500)
        
        for paragraph in paragraphs:
            if len(paragraph) > 50 and total_length < max_length:
                summary_parts.append(paragraph)
                total_length += len(paragraph)
            
            if total_length >= max_length:
                break
        
        summary = '\n\n'.join(summary_parts)
        
        # Truncar si es necesario
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit('.', 1)[0] + "."
        
        return summary
