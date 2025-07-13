"""
Gestión de configuración de la aplicación
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Gestiona la configuración de la aplicación"""
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            "app": {
                "version": "1.0.0",
                "debug": False,
                "language": "es"
            },
            "database": {
                "path": "data/pypodcast.db",
                "backup_enabled": True,
                "backup_interval_hours": 24
            },
            "audio": {
                "output_dir": "podcasts",
                "format": "wav",  # Cambiado a WAV para compatibilidad con pygame
                "quality": "high",
                "voice": "Jorge",  # Voz en español de macOS
                "rate": 150  # Palabras por minuto (velocidad más natural)
            },
            "network": {
                "timeout": 30,
                "max_retries": 3,
                "user_agent": "PyPodcast/1.0.0"
            },
            "ui": {
                "theme": "light",
                "window_width": 1200,
                "window_height": 800,
                "auto_refresh": True,
                "refresh_interval_minutes": 60
            },
            "content": {
                "max_summary_length": 500,
                "summary_language": "es",
                "auto_process": False,
                "skip_processed": True,
                "use_apple_intelligence": True
            },
            "apple_intelligence": {
                "base_url": "http://127.0.0.1:11535/v1",
                "max_tokens": 500,
                "temperature": 0.7,
                "enabled": True
            }
        }
    
    def load_config(self) -> bool:
        """Carga la configuración desde archivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merger con configuración por defecto
                    self._merge_configs(self.config, loaded_config)
                return True
            else:
                # Crear archivo de configuración por primera vez
                return self.save_config()
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return False
    
    def save_config(self) -> bool:
        """Guarda la configuración actual"""
        try:
            # Crear directorio si no existe
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False
    
    def get(self, key_path: str, default=None):
        """Obtiene un valor de configuración usando notación de punto"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Establece un valor de configuración usando notación de punto"""
        keys = key_path.split('.')
        config = self.config
        
        # Navegar hasta el penúltimo nivel
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Establecer el valor final
        config[keys[-1]] = value
    
    def _merge_configs(self, default: Dict, loaded: Dict):
        """Combina configuración cargada con la por defecto"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_configs(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value

# Instancia global del gestor de configuración
config_manager = ConfigManager()
