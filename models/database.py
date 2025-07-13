"""
Gestión de base de datos SQLite
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.config import config_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Gestor de base de datos SQLite"""
    
    def __init__(self):
        self.db_path = Path(config_manager.get('database.path', 'data/pypodcast.db'))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self):
        """Inicializa las tablas de la base de datos"""
        try:
            with self.get_connection() as conn:
                # Tabla de fuentes de datos
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS data_sources (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,  -- 'youtube', 'rss', 'web'
                        url TEXT NOT NULL UNIQUE,
                        thumbnail_url TEXT,
                        description TEXT,
                        active BOOLEAN DEFAULT 1,
                        last_check TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabla de items de contenido
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS content_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL UNIQUE,
                        description TEXT,
                        content TEXT,
                        summary TEXT,
                        audio_file TEXT,
                        thumbnail_url TEXT,
                        status TEXT DEFAULT 'nuevo',  -- 'nuevo', 'procesado', 'escuchado', 'ignorar'
                        published_date TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (source_id) REFERENCES data_sources (id)
                    )
                ''')
                
                # Tabla de configuración
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS app_config (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabla de logs de procesamiento
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS processing_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id INTEGER NOT NULL,
                        action TEXT NOT NULL,
                        status TEXT NOT NULL,  -- 'success', 'error', 'warning'
                        message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (item_id) REFERENCES content_items (id)
                    )
                ''')
                
                # Índices para mejorar rendimiento
                conn.execute('CREATE INDEX IF NOT EXISTS idx_content_items_source_id ON content_items(source_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_content_items_status ON content_items(status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_content_items_created_at ON content_items(created_at)')
                
                conn.commit()
                logger.info("Base de datos inicializada correctamente")
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    def add_data_source(self, name: str, source_type: str, url: str, 
                       thumbnail_url: str = None, description: str = None) -> int:
        """Añade una nueva fuente de datos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO data_sources (name, type, url, thumbnail_url, description, last_check)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, source_type, url, thumbnail_url, description, datetime.now()))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Fuente de datos ya existe: {url}")
            raise ValueError("La fuente de datos ya existe")
        except Exception as e:
            logger.error(f"Error añadiendo fuente de datos: {e}")
            raise
    
    def get_data_sources(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Obtiene todas las fuentes de datos"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM data_sources"
                if active_only:
                    query += " WHERE active = 1"
                query += " ORDER BY name"
                
                cursor = conn.execute(query)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo fuentes de datos: {e}")
            return []
    
    def add_content_item(self, source_id: int, title: str, url: str,
                        description: str = None, content: str = None,
                        published_date: datetime = None) -> int:
        """Añade un nuevo item de contenido"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute('''
                    INSERT INTO content_items 
                    (source_id, title, url, description, content, published_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (source_id, title, url, description, content, published_date))
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"Item de contenido ya existe: {url}")
            return None
        except Exception as e:
            logger.error(f"Error añadiendo item de contenido: {e}")
            raise
    
    def get_content_items(self, source_id: int = None, status: str = None) -> List[Dict[str, Any]]:
        """Obtiene items de contenido filtrados"""
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT ci.*, ds.name as source_name, ds.type as source_type
                    FROM content_items ci
                    JOIN data_sources ds ON ci.source_id = ds.id
                '''
                params = []
                
                conditions = []
                if source_id:
                    conditions.append("ci.source_id = ?")
                    params.append(source_id)
                
                if status:
                    conditions.append("ci.status = ?")
                    params.append(status)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY ci.published_date DESC, ci.created_at DESC"
                
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error obteniendo items de contenido: {e}")
            return []
    
    def update_content_item_status(self, item_id: int, status: str):
        """Actualiza el estado de un item de contenido"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE content_items 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, item_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error actualizando estado del item: {e}")
            raise
    
    def update_content_item_files(self, item_id: int, summary: str = None, audio_file: str = None):
        """Actualiza archivos generados de un item"""
        try:
            with self.get_connection() as conn:
                updates = []
                params = []
                
                if summary is not None:
                    updates.append("summary = ?")
                    params.append(summary)
                
                if audio_file is not None:
                    updates.append("audio_file = ?")
                    params.append(audio_file)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(item_id)
                    
                    query = f"UPDATE content_items SET {', '.join(updates)} WHERE id = ?"
                    conn.execute(query, params)
                    conn.commit()
        except Exception as e:
            logger.error(f"Error actualizando archivos del item: {e}")
            raise
    
    def log_processing_action(self, item_id: int, action: str, status: str, message: str = None):
        """Registra una acción de procesamiento"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO processing_logs (item_id, action, status, message)
                    VALUES (?, ?, ?, ?)
                ''', (item_id, action, status, message))
                conn.commit()
        except Exception as e:
            logger.error(f"Error registrando acción de procesamiento: {e}")
    
    def get_item_count_by_source(self, source_id: int) -> int:
        """Obtiene el número de items de una fuente"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM content_items WHERE source_id = ?",
                    (source_id,)
                )
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error obteniendo conteo de items: {e}")
            return 0

    def get_source_deletion_info(self, source_id: int) -> Dict[str, Any]:
        """Obtiene información detallada sobre lo que se eliminará al borrar una fuente"""
        try:
            with self.get_connection() as conn:
                # Información de la fuente
                source_cursor = conn.execute(
                    "SELECT name, type, url FROM data_sources WHERE id = ?",
                    (source_id,)
                )
                source_row = source_cursor.fetchone()
                
                if not source_row:
                    return None
                
                # Contar items de contenido
                items_cursor = conn.execute(
                    "SELECT COUNT(*) FROM content_items WHERE source_id = ?",
                    (source_id,)
                )
                total_items = items_cursor.fetchone()[0]
                
                # Contar archivos de audio existentes
                audio_cursor = conn.execute(
                    "SELECT COUNT(*) FROM content_items WHERE source_id = ? AND audio_file IS NOT NULL AND audio_file != ''",
                    (source_id,)
                )
                audio_files = audio_cursor.fetchone()[0]
                
                # Obtener lista de archivos de audio para eliminación física
                audio_files_cursor = conn.execute(
                    "SELECT audio_file FROM content_items WHERE source_id = ? AND audio_file IS NOT NULL AND audio_file != ''",
                    (source_id,)
                )
                audio_file_paths = [row[0] for row in audio_files_cursor.fetchall()]
                
                # Contar logs de procesamiento
                logs_cursor = conn.execute(
                    """SELECT COUNT(*) FROM processing_logs pl 
                       JOIN content_items ci ON pl.item_id = ci.id 
                       WHERE ci.source_id = ?""",
                    (source_id,)
                )
                processing_logs = logs_cursor.fetchone()[0]
                
                return {
                    'source_name': source_row[0],
                    'source_type': source_row[1],
                    'source_url': source_row[2],
                    'total_items': total_items,
                    'audio_files_count': audio_files,
                    'audio_file_paths': audio_file_paths,
                    'processing_logs': processing_logs
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo información de eliminación: {e}")
            return None

    def delete_data_source_and_content(self, source_id: int) -> bool:
        """Elimina una fuente de datos y todo su contenido asociado"""
        try:
            with self.get_connection() as conn:
                # Verificar que la fuente existe
                cursor = conn.execute("SELECT id FROM data_sources WHERE id = ?", (source_id,))
                if not cursor.fetchone():
                    logger.warning(f"Fuente de datos no encontrada: {source_id}")
                    return False
                
                # Eliminar logs de procesamiento primero (por foreign key)
                conn.execute("""
                    DELETE FROM processing_logs 
                    WHERE item_id IN (
                        SELECT id FROM content_items WHERE source_id = ?
                    )
                """, (source_id,))
                
                # Eliminar items de contenido
                conn.execute("DELETE FROM content_items WHERE source_id = ?", (source_id,))
                
                # Eliminar la fuente de datos
                conn.execute("DELETE FROM data_sources WHERE id = ?", (source_id,))
                
                conn.commit()
                logger.info(f"Fuente de datos {source_id} y todo su contenido eliminado exitosamente")
                return True
                
        except Exception as e:
            logger.error(f"Error eliminando fuente de datos {source_id}: {e}")
            return False

    def update_content_item_text(self, item_id: int, content: str = None, summary: str = None):
        """Actualiza el contenido de texto de un item"""
        try:
            with self.get_connection() as conn:
                updates = []
                params = []
                
                if content is not None:
                    updates.append("content = ?")
                    params.append(content)
                
                if summary is not None:
                    updates.append("summary = ?")
                    params.append(summary)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(item_id)
                    
                    query = f"UPDATE content_items SET {', '.join(updates)} WHERE id = ?"
                    conn.execute(query, params)
                    conn.commit()
        except Exception as e:
            logger.error(f"Error actualizando texto del item: {e}")
            raise

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
