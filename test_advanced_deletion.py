#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de eliminación avanzada de fuentes de datos
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt

from models.database import DatabaseManager
from utils.file_manager import FileManager
from app.dialogs.delete_confirmation_dialog import DeleteConfirmationDialog
from utils.logger import get_logger

logger = get_logger(__name__)

class TestDeletionWindow(QMainWindow):
    """Ventana de prueba para la funcionalidad de eliminación"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de prueba"""
        self.setWindowTitle("Prueba de Eliminación Avanzada")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Prueba de Eliminación Avanzada de Fuentes")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Botones de prueba
        self.test_info_button = QPushButton("1. Probar Obtención de Información de Eliminación")
        self.test_info_button.clicked.connect(self.test_deletion_info)
        layout.addWidget(self.test_info_button)
        
        self.test_dialog_button = QPushButton("2. Probar Diálogo de Confirmación")
        self.test_dialog_button.clicked.connect(self.test_confirmation_dialog)
        layout.addWidget(self.test_dialog_button)
        
        self.test_file_ops_button = QPushButton("3. Probar Operaciones de Archivos")
        self.test_file_ops_button.clicked.connect(self.test_file_operations)
        layout.addWidget(self.test_file_ops_button)
        
        self.create_test_data_button = QPushButton("4. Crear Datos de Prueba")
        self.create_test_data_button.clicked.connect(self.create_test_data)
        layout.addWidget(self.create_test_data_button)
        
        # Área de resultados
        self.results_label = QLabel("Haga clic en los botones para probar la funcionalidad")
        self.results_label.setStyleSheet("padding: 20px; border: 1px solid #ccc; margin: 20px;")
        self.results_label.setWordWrap(True)
        self.results_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.results_label)
        
        central_widget.setLayout(layout)
    
    def test_deletion_info(self):
        """Prueba la obtención de información de eliminación"""
        try:
            # Obtener las fuentes de datos existentes
            sources = self.db_manager.get_data_sources(active_only=False)
            
            if not sources:
                self.results_label.setText("❌ No hay fuentes de datos para probar. Cree algunas primero.")
                return
            
            # Probar con la primera fuente
            source = sources[0]
            deletion_info = self.db_manager.get_source_deletion_info(source['id'])
            
            if deletion_info:
                info_text = f"""✅ Información de eliminación obtenida:

📝 Fuente: {deletion_info['source_name']}
🔗 Tipo: {deletion_info['source_type']}
📄 Items de contenido: {deletion_info['total_items']}
🎵 Archivos de audio: {deletion_info['audio_files_count']}
📊 Logs de procesamiento: {deletion_info['processing_logs']}
🗂️ Rutas de archivos: {len(deletion_info['audio_file_paths'])} archivos"""
                
                self.results_label.setText(info_text)
                logger.info("Prueba de información de eliminación exitosa")
            else:
                self.results_label.setText("❌ Error obteniendo información de eliminación")
                
        except Exception as e:
            self.results_label.setText(f"❌ Error en prueba: {str(e)}")
            logger.error(f"Error en test_deletion_info: {e}")
    
    def test_confirmation_dialog(self):
        """Prueba el diálogo de confirmación"""
        try:
            # Obtener una fuente para probar
            sources = self.db_manager.get_data_sources(active_only=False)
            
            if not sources:
                self.results_label.setText("❌ No hay fuentes de datos para probar. Cree algunas primero.")
                return
            
            source = sources[0]
            deletion_info = self.db_manager.get_source_deletion_info(source['id'])
            
            if deletion_info:
                # Mostrar el diálogo
                dialog = DeleteConfirmationDialog(deletion_info, self)
                result = dialog.exec()
                
                if result == dialog.Accepted:
                    self.results_label.setText("✅ Usuario confirmó la eliminación en el diálogo")
                else:
                    self.results_label.setText("ℹ️ Usuario canceló la eliminación en el diálogo")
                    
                logger.info("Prueba de diálogo de confirmación completada")
            else:
                self.results_label.setText("❌ Error obteniendo información para el diálogo")
                
        except Exception as e:
            self.results_label.setText(f"❌ Error en prueba del diálogo: {str(e)}")
            logger.error(f"Error en test_confirmation_dialog: {e}")
    
    def test_file_operations(self):
        """Prueba las operaciones de archivos"""
        try:
            # Crear algunos archivos de prueba
            test_dir = Path("test_audio_files")
            test_dir.mkdir(exist_ok=True)
            
            test_files = []
            for i in range(3):
                test_file = test_dir / f"test_audio_{i}.wav"
                test_file.write_text(f"Contenido de prueba {i}")
                test_files.append(str(test_file))
            
            # Probar eliminación
            results = FileManager.delete_audio_files(test_files)
            
            # Limpiar directorios vacíos
            deleted_dirs = FileManager.clean_empty_directories(test_dir)
            
            result_text = f"""✅ Operaciones de archivos completadas:

📁 Archivos eliminados: {len(results['deleted_files'])}
❌ Archivos con error: {len(results['failed_files'])}
❓ Archivos no encontrados: {len(results['not_found_files'])}
💾 Espacio liberado: {FileManager.format_file_size(results['total_size_freed'])}
🗂️ Directorios limpiados: {deleted_dirs}"""
            
            self.results_label.setText(result_text)
            logger.info("Prueba de operaciones de archivos exitosa")
            
        except Exception as e:
            self.results_label.setText(f"❌ Error en prueba de archivos: {str(e)}")
            logger.error(f"Error en test_file_operations: {e}")
    
    def create_test_data(self):
        """Crea datos de prueba para testing"""
        try:
            # Añadir una fuente de prueba
            source_id = self.db_manager.add_data_source(
                name="Fuente de Prueba para Eliminación",
                source_type="web",
                url="https://ejemplo.com/test",
                description="Fuente creada para probar la eliminación"
            )
            
            # Añadir algunos items de contenido
            for i in range(3):
                item_id = self.db_manager.add_content_item(
                    source_id=source_id,
                    title=f"Contenido de Prueba {i+1}",
                    url=f"https://ejemplo.com/item{i+1}",
                    description=f"Descripción del contenido {i+1}",
                    content=f"Texto del contenido {i+1} para probar la eliminación"
                )
                
                # Simular archivo de audio
                if item_id:
                    audio_file = f"test_audio_{i+1}.wav"
                    self.db_manager.update_content_item_files(item_id, audio_file=audio_file)
                    
                    # Registrar algunas acciones
                    self.db_manager.log_processing_action(
                        item_id, "text_extraction", "success", "Texto extraído"
                    )
                    self.db_manager.log_processing_action(
                        item_id, "tts_generation", "success", "Audio generado"
                    )
            
            self.results_label.setText(f"""✅ Datos de prueba creados:

📝 Fuente ID: {source_id}
📄 3 items de contenido
🎵 3 archivos de audio simulados
📊 6 registros de procesamiento

Ahora puede probar las otras funcionalidades.""")
            
            logger.info(f"Datos de prueba creados exitosamente (source_id: {source_id})")
            
        except Exception as e:
            self.results_label.setText(f"❌ Error creando datos de prueba: {str(e)}")
            logger.error(f"Error en create_test_data: {e}")

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Configurar logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar base de datos
    try:
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        logger.info("Base de datos inicializada")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {e}")
        return 1
    
    # Mostrar ventana de prueba
    window = TestDeletionWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
