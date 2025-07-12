"""
Transcriptor de videos de YouTube
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs
from utils.config import config_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class YouTubeTranscriber:
    """Transcriptor de videos de YouTube"""
    
    def __init__(self):
        self.preferred_languages = ['es', 'es-ES', 'en', 'en-US']
        self.formatter = TextFormatter()
    
    def extract_video_id(self, url: str) -> str:
        """Extrae el ID del video de una URL de YouTube"""
        try:
            parsed_url = urlparse(url)
            
            if parsed_url.hostname in ['youtube.com', 'www.youtube.com']:
                if parsed_url.path == '/watch':
                    return parse_qs(parsed_url.query)['v'][0]
                elif parsed_url.path.startswith('/embed/'):
                    return parsed_url.path.split('/embed/')[1]
                elif parsed_url.path.startswith('/v/'):
                    return parsed_url.path.split('/v/')[1]
            
            elif parsed_url.hostname in ['youtu.be', 'www.youtu.be']:
                return parsed_url.path[1:]
            
            raise ValueError("URL de YouTube no válida")
            
        except Exception as e:
            logger.error(f"Error extrayendo ID de video de {url}: {e}")
            raise
    
    def get_transcript(self, video_url: str) -> Dict[str, Any]:
        """Obtiene la transcripción de un video de YouTube"""
        try:
            video_id = self.extract_video_id(video_url)
            
            # Obtener transcripciones disponibles
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Buscar transcripción en idiomas preferidos
            transcript = None
            language_used = None
            
            for lang in self.preferred_languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    language_used = lang
                    break
                except Exception:
                    continue
            
            # Si no hay transcripción en idiomas preferidos, usar la primera disponible
            if not transcript:
                try:
                    available_transcripts = list(transcript_list)
                    if available_transcripts:
                        transcript = available_transcripts[0]
                        language_used = transcript.language_code
                except Exception:
                    pass
            
            if not transcript:
                raise ValueError("No hay transcripciones disponibles para este video")
            
            # Obtener la transcripción
            transcript_data = transcript.fetch()
            
            # Formatear como texto
            text_transcript = self.formatter.format_transcript(transcript_data)
            
            # Limpiar y procesar el texto
            cleaned_text = self._clean_transcript(text_transcript)
            
            # Generar resumen
            summary = self._generate_summary(cleaned_text)
            
            return {
                'video_id': video_id,
                'video_url': video_url,
                'language': language_used,
                'transcript': cleaned_text,
                'summary': summary,
                'duration_seconds': self._calculate_duration(transcript_data),
                'is_auto_generated': transcript.is_generated
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo transcripción de {video_url}: {e}")
            raise
    
    def _clean_transcript(self, text: str) -> str:
        """Limpia y normaliza el texto de la transcripción"""
        if not text:
            return ""
        
        # Eliminar marcas de tiempo y caracteres especiales
        text = re.sub(r'\[.*?\]', '', text)  # Eliminar [timestamps] si los hay
        text = re.sub(r'\(.*?\)', '', text)  # Eliminar (comentarios) del transcriptor
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Capitalizar inicio de oraciones
        sentences = text.split('. ')
        sentences = [s.strip().capitalize() if s.strip() else s for s in sentences]
        text = '. '.join(sentences)
        
        return text.strip()
    
    def _generate_summary(self, text: str) -> str:
        """Genera un resumen básico de la transcripción"""
        if not text:
            return ""
        
        max_length = config_manager.get('content.max_summary_length', 500)
        
        # Dividir en oraciones
        sentences = [s.strip() + '.' for s in text.split('.') if s.strip()]
        
        # Seleccionar oraciones más relevantes (simplificado)
        summary_sentences = []
        total_length = 0
        
        # Priorizar oraciones al inicio y final
        important_sentences = []
        
        # Añadir primeras oraciones
        for i, sentence in enumerate(sentences[:5]):
            if len(sentence) > 20:  # Oraciones sustanciales
                important_sentences.append(sentence)
        
        # Añadir últimas oraciones
        for i, sentence in enumerate(sentences[-3:]):
            if len(sentence) > 20:
                important_sentences.append(sentence)
        
        # Construir resumen
        for sentence in important_sentences:
            if total_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                total_length += len(sentence)
            else:
                break
        
        summary = ' '.join(summary_sentences)
        
        # Si el resumen es muy corto, añadir más contenido del centro
        if len(summary) < max_length * 0.5 and len(sentences) > 10:
            middle_start = len(sentences) // 3
            middle_end = 2 * len(sentences) // 3
            
            for sentence in sentences[middle_start:middle_end]:
                if len(sentence) > 20 and total_length + len(sentence) <= max_length:
                    summary_sentences.append(sentence)
                    total_length += len(sentence)
        
        return ' '.join(summary_sentences)
    
    def _calculate_duration(self, transcript_data: List[Dict]) -> int:
        """Calcula la duración del video en segundos"""
        try:
            if not transcript_data:
                return 0
            
            # El último elemento tiene el tiempo final
            last_entry = transcript_data[-1]
            return int(last_entry.get('start', 0) + last_entry.get('duration', 0))
            
        except Exception:
            return 0
    
    def is_youtube_url(self, url: str) -> bool:
        """Verifica si una URL es de YouTube"""
        try:
            parsed = urlparse(url)
            return parsed.hostname in [
                'youtube.com', 'www.youtube.com',
                'youtu.be', 'www.youtu.be',
                'm.youtube.com'
            ]
        except Exception:
            return False
    
    def get_available_languages(self, video_url: str) -> List[str]:
        """Obtiene los idiomas disponibles para la transcripción"""
        try:
            video_id = self.extract_video_id(video_url)
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            languages = []
            for transcript in transcript_list:
                languages.append({
                    'language_code': transcript.language_code,
                    'language': transcript.language,
                    'is_generated': transcript.is_generated
                })
            
            return languages
            
        except Exception as e:
            logger.error(f"Error obteniendo idiomas disponibles: {e}")
            return []
