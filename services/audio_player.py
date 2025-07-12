"""
Reproductor de audio para podcasts
"""

import pygame
import os
from pathlib import Path
from typing import Optional, Callable
import threading
import time
from utils.config import config_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class AudioPlayer:
    """Reproductor de audio usando pygame"""
    
    def __init__(self):
        self.is_initialized = False
        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.position = 0
        self.duration = 0
        self.volume = 0.7
        
        # Callbacks para eventos
        self.on_position_changed: Optional[Callable[[float], None]] = None
        self.on_playback_finished: Optional[Callable[[], None]] = None
        self.on_playback_started: Optional[Callable[[], None]] = None
        self.on_playback_paused: Optional[Callable[[], None]] = None
        
        self._position_thread = None
        self._stop_position_thread = False
        
        self._initialize_pygame()
    
    def _initialize_pygame(self):
        """Inicializa pygame mixer"""
        try:
            if not self.is_initialized:
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                self.is_initialized = True
                logger.info("AudioPlayer inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando AudioPlayer: {e}")
            raise
    
    def load_file(self, file_path: str) -> bool:
        """Carga un archivo de audio"""
        try:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
            # Detener reproducción actual si existe
            self.stop()
            
            # Cargar nuevo archivo
            pygame.mixer.music.load(file_path)
            self.current_file = file_path
            
            # Intentar obtener duración (aproximada)
            self.duration = self._get_file_duration(file_path)
            
            logger.info(f"Archivo cargado: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando archivo {file_path}: {e}")
            return False
    
    def play(self) -> bool:
        """Inicia la reproducción"""
        try:
            if not self.current_file:
                logger.warning("No hay archivo cargado")
                return False
            
            if self.is_paused:
                # Reanudar reproducción pausada
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                # Iniciar nueva reproducción
                pygame.mixer.music.play(start=self.position)
            
            self.is_playing = True
            self._start_position_tracking()
            
            if self.on_playback_started:
                self.on_playback_started()
            
            logger.info("Reproducción iniciada")
            return True
            
        except Exception as e:
            logger.error(f"Error iniciando reproducción: {e}")
            return False
    
    def pause(self) -> bool:
        """Pausa la reproducción"""
        try:
            if self.is_playing and not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.is_playing = False
                
                if self.on_playback_paused:
                    self.on_playback_paused()
                
                logger.info("Reproducción pausada")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error pausando reproducción: {e}")
            return False
    
    def stop(self) -> bool:
        """Detiene la reproducción"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.position = 0
            self._stop_position_tracking()
            
            logger.info("Reproducción detenida")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo reproducción: {e}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Establece el volumen (0.0 a 1.0)"""
        try:
            volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(volume)
            self.volume = volume
            return True
            
        except Exception as e:
            logger.error(f"Error estableciendo volumen: {e}")
            return False
    
    def get_volume(self) -> float:
        """Obtiene el volumen actual"""
        return self.volume
    
    def seek(self, position: float) -> bool:
        """Busca a una posición específica (en segundos)"""
        try:
            if not self.current_file or position < 0:
                return False
            
            # pygame no soporta seek directo, necesitamos reiniciar
            was_playing = self.is_playing
            self.stop()
            
            self.position = min(position, self.duration)
            
            if was_playing:
                # Nota: pygame no soporta seek, esta es una limitación
                # Para un seek real necesitaríamos usar otra librería como python-vlc
                logger.warning("Seek limitado en pygame - reiniciando desde el principio")
                self.play()
            
            return True
            
        except Exception as e:
            logger.error(f"Error en seek: {e}")
            return False
    
    def get_position(self) -> float:
        """Obtiene la posición actual en segundos"""
        return self.position
    
    def get_duration(self) -> float:
        """Obtiene la duración total en segundos"""
        return self.duration
    
    def is_playing_file(self) -> bool:
        """Verifica si está reproduciendo"""
        return self.is_playing and pygame.mixer.music.get_busy()
    
    def _get_file_duration(self, file_path: str) -> float:
        """Obtiene la duración del archivo (aproximada)"""
        try:
            # Para archivos generados por macOS 'say', estimamos basado en el tamaño
            file_size = Path(file_path).stat().st_size
            
            # Estimación rough: ~12KB por segundo para archivos de voz
            estimated_duration = file_size / 12000
            
            # Limitar estimación razonable
            return max(10, min(estimated_duration, 3600))  # Entre 10 segundos y 1 hora
            
        except Exception:
            return 120  # Fallback de 2 minutos
    
    def _start_position_tracking(self):
        """Inicia el hilo de seguimiento de posición"""
        if self._position_thread and self._position_thread.is_alive():
            return
        
        self._stop_position_thread = False
        self._position_thread = threading.Thread(target=self._position_tracker)
        self._position_thread.daemon = True
        self._position_thread.start()
    
    def _stop_position_tracking(self):
        """Detiene el hilo de seguimiento de posición"""
        self._stop_position_thread = True
        if self._position_thread:
            self._position_thread.join(timeout=1)
    
    def _position_tracker(self):
        """Hilo que actualiza la posición de reproducción"""
        start_time = time.time()
        
        while not self._stop_position_thread and self.is_playing:
            if pygame.mixer.music.get_busy():
                # Actualizar posición basada en tiempo transcurrido
                elapsed = time.time() - start_time
                self.position = min(elapsed, self.duration)
                
                # Notificar cambio de posición
                if self.on_position_changed:
                    self.on_position_changed(self.position)
                
            else:
                # La reproducción terminó
                self.is_playing = False
                self.is_paused = False
                
                if self.on_playback_finished:
                    self.on_playback_finished()
                
                break
            
            time.sleep(0.1)  # Actualizar cada 100ms
    
    def get_supported_formats(self) -> list:
        """Obtiene los formatos de audio soportados"""
        return ['.mp3', '.wav', '.ogg', '.aiff', '.m4a']
    
    def cleanup(self):
        """Limpia recursos del reproductor"""
        try:
            self.stop()
            self._stop_position_tracking()
            if self.is_initialized:
                pygame.mixer.quit()
                self.is_initialized = False
            logger.info("AudioPlayer limpiado correctamente")
        except Exception as e:
            logger.error(f"Error limpiando AudioPlayer: {e}")
    
    def __del__(self):
        """Destructor"""
        self.cleanup()
