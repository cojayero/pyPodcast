"""
Servicio de conversión texto a voz usando macOS
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, List, Dict
import tempfile
from utils.config import config_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class TextToSpeechService:
    """Servicio de conversión texto a voz usando capacidades nativas de macOS"""
    
    def __init__(self):
        self.voice = config_manager.get('audio.voice', 'Jorge')  # Voz en español
        self.rate = config_manager.get('audio.rate', 200)  # Palabras por minuto
        self.output_dir = Path(config_manager.get('audio.output_dir', 'podcasts'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """Obtiene las voces disponibles en el sistema"""
        try:
            result = subprocess.run(['say', '-v', '?'], capture_output=True, text=True)
            voices = []
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Parsear línea: "Nombre idioma_REGION # descripción"
                    parts = line.split('#')
                    if len(parts) >= 2:
                        voice_info = parts[0].strip().split()
                        if len(voice_info) >= 2:
                            name = voice_info[0]
                            language = voice_info[1] if len(voice_info) > 1 else 'unknown'
                            description = parts[1].strip() if len(parts) > 1 else ''
                            
                            voices.append({
                                'name': name,
                                'language': language,
                                'description': description
                            })
            
            return voices
            
        except Exception as e:
            logger.error(f"Error obteniendo voces disponibles: {e}")
            return []
    
    def get_spanish_voices(self) -> List[str]:
        """Obtiene solo las voces en español"""
        try:
            voices = self.get_available_voices()
            spanish_voices = []
            
            for voice in voices:
                lang = voice.get('language', '').lower()
                if 'es' in lang or 'spanish' in voice.get('description', '').lower():
                    spanish_voices.append(voice['name'])
            
            # Voces conocidas en español como fallback
            if not spanish_voices:
                spanish_voices = ['Jorge', 'Monica', 'Paulina']
            
            return spanish_voices
            
        except Exception as e:
            logger.error(f"Error obteniendo voces en español: {e}")
            return ['Jorge']  # Fallback
    
    def text_to_speech(self, text: str, filename: str, title: str = None) -> str:
        """Convierte texto a archivo de audio MP3"""
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío")
        
        try:
            # Limpiar el texto para TTS
            clean_text = self._prepare_text_for_tts(text)
            
            # Generar nombre de archivo
            if not filename.endswith('.aiff'):
                filename = filename.replace('.mp3', '.aiff')
            
            output_path = self.output_dir / filename
            
            # Comando say de macOS
            cmd = [
                'say',
                '-v', self.voice,
                '-r', str(self.rate),
                '-o', str(output_path),
                clean_text
            ]
            
            logger.info(f"Generando audio con voz {self.voice} a {self.rate} wpm")
            
            # Ejecutar comando
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise RuntimeError(f"Error en síntesis de voz: {result.stderr}")
            
            # Convertir AIFF a MP3 si es necesario
            mp3_path = str(output_path).replace('.aiff', '.mp3')
            if self._convert_to_mp3(str(output_path), mp3_path):
                # Eliminar archivo AIFF temporal
                if output_path.exists():
                    output_path.unlink()
                return mp3_path
            else:
                # Si la conversión falla, devolver el AIFF
                return str(output_path)
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout en síntesis de voz")
            raise RuntimeError("La síntesis de voz tardó demasiado tiempo")
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            raise
    
    def _prepare_text_for_tts(self, text: str) -> str:
        """Prepara el texto para síntesis de voz"""
        # Limpiar caracteres problemáticos
        import re
        
        # Reemplazar abreviaciones comunes
        text = re.sub(r'\bDr\.', 'Doctor', text)
        text = re.sub(r'\bSr\.', 'Señor', text)
        text = re.sub(r'\bSra\.', 'Señora', text)
        text = re.sub(r'\betc\.', 'etcétera', text)
        
        # Limpiar caracteres especiales que pueden causar problemas
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)áéíóúñÁÉÍÓÚÑ]', ' ', text)
        
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Añadir pausas naturales
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace(';', '; ')
        text = text.replace(':', ': ')
        
        # Limitar longitud (say tiene límites)
        max_length = 15000  # Límite seguro para say
        if len(text) > max_length:
            # Cortar en la última oración completa
            text = text[:max_length]
            last_period = text.rfind('.')
            if last_period > max_length * 0.8:
                text = text[:last_period + 1]
        
        return text.strip()
    
    def _convert_to_mp3(self, input_path: str, output_path: str) -> bool:
        """Convierte archivo AIFF a MP3 usando ffmpeg si está disponible"""
        try:
            # Verificar si ffmpeg está disponible
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            
            # Convertir a MP3
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'mp3',
                '-ab', '128k',
                '-y',  # Sobrescribir si existe
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            # ffmpeg no disponible, intentar con afconvert (nativo de macOS)
            try:
                cmd = [
                    'afconvert',
                    '-f', 'mp4f',
                    '-d', 'aac',
                    input_path,
                    output_path.replace('.mp3', '.m4a')
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
                
            except Exception as e:
                logger.warning(f"No se pudo convertir a MP3: {e}")
                return False
    
    def create_podcast_with_intro(self, text: str, title: str, author: str = None) -> str:
        """Crea un podcast completo con introducción"""
        try:
            # Preparar texto completo con introducción
            intro = f"Bienvenido a PyPodcast. "
            if title:
                intro += f"El tema de hoy es: {title}. "
            if author:
                intro += f"Autor: {author}. "
            
            intro += "Comenzamos. "
            
            full_text = intro + text
            
            # Añadir conclusión
            outro = " Esto ha sido todo por hoy. Gracias por escuchar PyPodcast."
            full_text += outro
            
            # Generar archivo
            filename = self._sanitize_filename(title) + '.mp3'
            return self.text_to_speech(full_text, filename, title)
            
        except Exception as e:
            logger.error(f"Error creando podcast: {e}")
            raise
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nombre de archivo"""
        import re
        
        # Reemplazar caracteres problemáticos
        filename = re.sub(r'[^\w\s\-_.]', '', filename)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.strip('._-')
        
        # Limitar longitud
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename or "podcast"
    
    def test_voice_synthesis(self) -> bool:
        """Prueba la síntesis de voz"""
        try:
            test_text = "Prueba de síntesis de voz para PyPodcast."
            with tempfile.NamedTemporaryFile(suffix='.aiff', delete=False) as tmp:
                cmd = ['say', '-v', self.voice, '-o', tmp.name, test_text]
                result = subprocess.run(cmd, capture_output=True, timeout=10)
                
                success = result.returncode == 0 and Path(tmp.name).exists()
                
                # Limpiar archivo temporal
                if Path(tmp.name).exists():
                    Path(tmp.name).unlink()
                
                return success
                
        except Exception as e:
            logger.error(f"Error en prueba de síntesis: {e}")
            return False
