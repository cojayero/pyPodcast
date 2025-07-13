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
        self.rate = config_manager.get('audio.rate', 150)  # Palabras por minuto (más lento)
        self.output_dir = Path(config_manager.get('audio.output_dir', 'podcasts'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.format = config_manager.get('audio.format', 'mp3')  # Formato de salida
    
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
        """Convierte texto a archivo de audio WAV (compatible con pygame)"""
        if not text or not text.strip():
            raise ValueError("El texto no puede estar vacío")
        
        try:
            # Limpiar el texto para TTS
            clean_text = self._prepare_text_for_tts(text)
            
            # Generar nombres de archivo (temporal AIFF y final WAV)
            base_filename = filename.replace('.mp3', '').replace('.aiff', '').replace('.m4a', '').replace('.wav', '')
            temp_aiff_path = self.output_dir / f"{base_filename}_temp.aiff"
            final_wav_path = self.output_dir / f"{base_filename}.wav"  # Usar WAV para compatibilidad con pygame
            
            # Comando say de macOS para generar AIFF temporal
            cmd = [
                'say',
                '-v', self.voice,
                '-r', str(self.rate),
                '-o', str(temp_aiff_path),
                clean_text
            ]
            
            logger.info(f"Generando audio con voz {self.voice} a {self.rate} wpm")
            logger.info(f"Archivo de salida: {final_wav_path}")
            
            # Ejecutar comando
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise RuntimeError(f"Error en síntesis de voz: {result.stderr}")
            
            # Verificar que se creó el archivo temporal
            if not temp_aiff_path.exists():
                raise RuntimeError("No se pudo generar el archivo de audio temporal")
            
            # Convertir a WAV para compatibilidad con pygame
            if self._convert_to_wav(str(temp_aiff_path), str(final_wav_path)):
                # Eliminar archivo AIFF temporal
                if temp_aiff_path.exists():
                    temp_aiff_path.unlink()
                logger.info(f"Audio WAV generado exitosamente: {final_wav_path}")
                return str(final_wav_path)
            else:
                # Si la conversión falla, usar el AIFF como fallback
                fallback_path = self.output_dir / f"{base_filename}.aiff"
                temp_aiff_path.rename(fallback_path)
                logger.warning(f"Conversión a WAV falló, usando AIFF: {fallback_path}")
                return str(fallback_path)
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout en síntesis de voz")
            raise RuntimeError("La síntesis de voz tardó demasiado tiempo")
        except Exception as e:
            logger.error(f"Error en síntesis de voz: {e}")
            raise
    
    def _prepare_text_for_tts(self, text: str) -> str:
        """Prepara el texto para síntesis de voz más natural"""
        import re
        
        # Reemplazar abreviaciones comunes para mejor pronunciación
        replacements = {
            r'\bDr\.': 'Doctor',
            r'\bSr\.': 'Señor',
            r'\bSra\.': 'Señora',
            r'\bSrta\.': 'Señorita',
            r'\betc\.': 'etcétera',
            r'\bvs\.': 'versus',
            r'\bp\.ej\.': 'por ejemplo',
            r'\bi\.e\.': 'es decir',
            r'\be\.g\.': 'por ejemplo',
            r'\bURL': 'U R L',
            r'\bHTTP': 'H T T P',
            r'\bAPI': 'A P I',
            r'\bYouTube': 'YouTube',
            r'\bRSS': 'R S S',
            # Números ordinales
            r'\b1º': 'primero',
            r'\b2º': 'segundo',
            r'\b3º': 'tercero',
            r'\b1ª': 'primera',
            r'\b2ª': 'segunda',
            r'\b3ª': 'tercera',
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Limpiar caracteres especiales que pueden causar problemas
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)áéíóúñÁÉÍÓÚÑüÜ]', ' ', text)
        
        # Normalizar espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Añadir pausas más naturales
        text = text.replace('.', '. [[slnc 500]]')  # Pausa de 500ms después de punto
        text = text.replace(',', ', [[slnc 200]]')  # Pausa de 200ms después de coma
        text = text.replace(';', '; [[slnc 300]]')  # Pausa de 300ms después de punto y coma
        text = text.replace(':', ': [[slnc 250]]')  # Pausa de 250ms después de dos puntos
        text = text.replace('!', '! [[slnc 400]]')  # Pausa después de exclamación
        text = text.replace('?', '? [[slnc 400]]')  # Pausa después de interrogación
        
        # Mejorar pronunciación de URLs y elementos técnicos
        text = re.sub(r'https?://', 'h t t p ', text)
        text = re.sub(r'www\.', 'doble doble doble punto ', text)
        text = re.sub(r'\.com', ' punto com', text)
        text = re.sub(r'\.org', ' punto org', text)
        text = re.sub(r'\.net', ' punto net', text)
        
        # Limitar longitud (say tiene límites)
        max_length = 15000  # Límite seguro para say
        if len(text) > max_length:
            # Cortar en la última oración completa
            text = text[:max_length]
            last_period = text.rfind('.')
            if last_period > max_length * 0.8:
                text = text[:last_period + 1]
            text += " [[slnc 1000]] El texto ha sido truncado."
        
        return text.strip()
    
    def _convert_to_wav(self, input_path: str, output_path: str) -> bool:
        """Convierte archivo AIFF a WAV usando afconvert (nativo en macOS)"""
        try:
            # Método 1: Usar afconvert para generar WAV PCM (máxima compatibilidad)
            cmd = [
                'afconvert',
                '-f', 'WAVE',           # Formato WAVE
                '-d', 'LEI16@44100',    # PCM 16-bit Little Endian, 44.1kHz
                input_path,
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Conversión exitosa a WAV: {output_path}")
                return True
            else:
                logger.warning(f"afconvert WAV falló: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"afconvert WAV falló: {e}")
        
        # Método 2: Usar ffmpeg si está disponible
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'pcm_s16le',  # PCM 16-bit
                '-ar', '44100',          # Sample rate 44.1 kHz
                '-ac', '2',              # Stereo
                '-y',                    # Sobrescribir si existe
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Conversión exitosa a WAV con ffmpeg")
                return True
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.debug("ffmpeg no disponible")
        
        return False

    def _convert_to_mp3(self, input_path: str, output_path: str) -> bool:
        """Convierte archivo AIFF a M4A/AAC usando herramientas nativas de macOS"""
        try:
            # Método 1: Usar afconvert para AAC (la opción más compatible)
            try:
                # Crear archivo M4A con codec AAC
                m4a_path = output_path.replace('.mp3', '.m4a')
                cmd = [
                    'afconvert',
                    '-f', 'm4af',       # Formato Apple M4A
                    '-d', 'aac',        # Codec AAC
                    '-q', '127',        # Calidad máxima
                    input_path,
                    m4a_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Conversión exitosa a M4A/AAC: {m4a_path}")
                    return True
                else:
                    logger.warning(f"afconvert M4A falló: {result.stderr}")
                    
            except Exception as e:
                logger.warning(f"afconvert M4A falló: {e}")
            
            # Método 2: Usar afconvert para ALAC (sin pérdida)
            try:
                alac_path = output_path.replace('.mp3', '_lossless.m4a')
                cmd = [
                    'afconvert',
                    '-f', 'm4af',       # Formato Apple M4A
                    '-d', 'alac',       # Codec ALAC (sin pérdida)
                    input_path,
                    alac_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"Conversión exitosa a ALAC: {alac_path}")
                    # Renombrar para que sea el archivo principal
                    final_path = output_path.replace('.mp3', '.m4a')
                    Path(alac_path).rename(final_path)
                    return True
                else:
                    logger.warning(f"afconvert ALAC falló: {result.stderr}")
                    
            except Exception as e:
                logger.warning(f"afconvert ALAC falló: {e}")
            
            # Método 3: Intentar con lame si está disponible
            try:
                subprocess.run(['lame', '--version'], capture_output=True, check=True)
                
                cmd = [
                    'lame',
                    '-b', '128',        # Bitrate 128 kbps
                    '-q', '2',          # Calidad alta
                    '--quiet',          # Modo silencioso
                    input_path,
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("Conversión a MP3 exitosa con lame")
                    return True
                    
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.debug("lame no disponible")
            
            # Método 4: Usar ffmpeg con codec AAC si está disponible
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                
                # Intentar con codec AAC incorporado
                m4a_path = output_path.replace('.mp3', '.m4a')
                cmd = [
                    'ffmpeg',
                    '-i', input_path,
                    '-c:a', 'aac',      # Usar codec AAC nativo
                    '-b:a', '128k',     # Bitrate 128 kbps
                    '-ar', '44100',     # Sample rate 44.1 kHz
                    '-y',               # Sobrescribir si existe
                    m4a_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("Conversión exitosa con ffmpeg AAC")
                    return True
                    
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.debug("ffmpeg no disponible o sin codec apropiado")
            
            return False
            
        except Exception as e:
            logger.error(f"Error en conversión de audio: {e}")
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
    
    def set_speech_rate(self, rate: int):
        """Establece la velocidad de habla en palabras por minuto"""
        if 100 <= rate <= 300:
            self.rate = rate
            logger.info(f"Velocidad de habla establecida a {rate} wpm")
        else:
            logger.warning(f"Velocidad inválida {rate}, debe estar entre 100-300 wpm")
    
    def set_voice(self, voice_name: str):
        """Establece la voz a usar"""
        available_voices = [v['name'] for v in self.get_available_voices()]
        if voice_name in available_voices:
            self.voice = voice_name
            logger.info(f"Voz establecida a {voice_name}")
        else:
            logger.warning(f"Voz {voice_name} no disponible. Usando {self.voice}")
