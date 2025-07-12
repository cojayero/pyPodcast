#!/usr/bin/env python3
"""
PyPodcast - Generador automático de podcasts
Aplicación principal que inicia la interfaz gráfica
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.main_window import MainWindow
from utils.config import ConfigManager
from utils.logger import setup_logger
from models.database import DatabaseManager

def main():
    """Función principal de la aplicación"""
    # Configurar logging
    logger = setup_logger()
    logger.info("Iniciando PyPodcast...")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("PyPodcast")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PyPodcast")
    
    try:
        # Inicializar configuración
        config_manager = ConfigManager()
        config_manager.load_config()
        
        # Inicializar base de datos
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        # Crear y mostrar ventana principal
        window = MainWindow()
        window.show()
        
        logger.info("Aplicación iniciada correctamente")
        
        # Ejecutar aplicación
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
