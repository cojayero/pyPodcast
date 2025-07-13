"""
Utilidades para gestión de archivos y eliminación segura
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class FileManager:
    """Gestiona operaciones de archivos, especialmente eliminación segura"""
    
    @staticmethod
    def delete_audio_files(file_paths: List[str]) -> Dict[str, Any]:
        """
        Elimina archivos de audio de manera segura
        
        Args:
            file_paths: Lista de rutas de archivos de audio a eliminar
            
        Returns:
            Diccionario con estadísticas de la eliminación
        """
        results = {
            'deleted_files': [],
            'failed_files': [],
            'not_found_files': [],
            'total_size_freed': 0
        }
        
        for file_path in file_paths:
            if not file_path:
                continue
                
            try:
                path = Path(file_path)
                
                if not path.exists():
                    results['not_found_files'].append(str(path))
                    logger.warning(f"Archivo no encontrado para eliminar: {path}")
                    continue
                
                # Obtener tamaño antes de eliminar
                file_size = path.stat().st_size
                
                # Eliminar archivo
                path.unlink()
                
                results['deleted_files'].append(str(path))
                results['total_size_freed'] += file_size
                logger.info(f"Archivo eliminado: {path} ({file_size} bytes)")
                
            except Exception as e:
                results['failed_files'].append(str(path))
                logger.error(f"Error eliminando archivo {file_path}: {e}")
        
        return results
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formatea el tamaño de archivo en unidades legibles"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB']
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {units[i]}"
    
    @staticmethod
    def clean_empty_directories(directory: Path) -> int:
        """
        Limpia directorios vacíos de manera recursiva
        
        Args:
            directory: Directorio raíz para limpiar
            
        Returns:
            Número de directorios eliminados
        """
        if not directory.exists() or not directory.is_dir():
            return 0
        
        deleted_dirs = 0
        
        try:
            # Recorrer subdirectorios primero (bottom-up)
            for subdir in directory.rglob('*'):
                if subdir.is_dir() and not any(subdir.iterdir()):
                    try:
                        subdir.rmdir()
                        deleted_dirs += 1
                        logger.info(f"Directorio vacío eliminado: {subdir}")
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar directorio vacío {subdir}: {e}")
            
            # Verificar si el directorio raíz está vacío
            if not any(directory.iterdir()):
                try:
                    directory.rmdir()
                    deleted_dirs += 1
                    logger.info(f"Directorio raíz vacío eliminado: {directory}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar directorio raíz {directory}: {e}")
                    
        except Exception as e:
            logger.error(f"Error limpiando directorios vacíos en {directory}: {e}")
        
        return deleted_dirs
    
    @staticmethod
    def get_audio_directory() -> Path:
        """Obtiene el directorio de archivos de audio"""
        from utils.config import config_manager
        audio_dir = config_manager.get('audio.output_dir', 'podcasts')
        return Path(audio_dir)
    
    @staticmethod
    def safe_delete_with_backup(file_path: str, backup_dir: str = None) -> bool:
        """
        Elimina un archivo de manera segura, opcionalmente creando un backup
        
        Args:
            file_path: Ruta del archivo a eliminar
            backup_dir: Directorio donde hacer backup (opcional)
            
        Returns:
            True si se eliminó exitosamente
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.warning(f"Archivo no existe para eliminar: {path}")
                return True  # Consideramos éxito si ya no existe
            
            # Crear backup si se especifica
            if backup_dir:
                backup_path = Path(backup_dir)
                backup_path.mkdir(parents=True, exist_ok=True)
                
                backup_file = backup_path / path.name
                counter = 1
                while backup_file.exists():
                    stem = path.stem
                    suffix = path.suffix
                    backup_file = backup_path / f"{stem}_backup_{counter}{suffix}"
                    counter += 1
                
                shutil.copy2(path, backup_file)
                logger.info(f"Backup creado: {backup_file}")
            
            # Eliminar archivo original
            path.unlink()
            logger.info(f"Archivo eliminado: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error en eliminación segura de {file_path}: {e}")
            return False
