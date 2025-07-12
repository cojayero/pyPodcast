"""
Sistema de logging para la aplicación
"""

import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "pypodcast", level: int = logging.INFO) -> logging.Logger:
    """Configura y retorna un logger para la aplicación"""
    
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Formato de los mensajes
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo (con rotación diaria)
    log_file = log_dir / f"pypodcast_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Solo warnings y errores en consola
    console_handler.setFormatter(formatter)
    
    # Añadir handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = "pypodcast") -> logging.Logger:
    """Obtiene el logger configurado"""
    return logging.getLogger(name)
