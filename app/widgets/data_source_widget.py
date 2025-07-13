"""
Widget de lista de fuentes de datos
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                              QListWidgetItem, QLabel, QPushButton, QFrame,
                              QDialog, QFormLayout, QLineEdit, QComboBox,
                              QTextEdit, QMessageBox)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QIcon
import requests
from pathlib import Path
from typing import List, Dict, Any

from models.database import DatabaseManager
from models.data_source import DataSource
from services.rss_manager import RSSManager
from utils.logger import get_logger
from utils.file_manager import FileManager
from app.dialogs.delete_confirmation_dialog import DeleteConfirmationDialog

logger = get_logger(__name__)

class DataSourceItem(QFrame):
    """Widget para mostrar una fuente de datos"""
    
    clicked = Signal(int)
    
    def __init__(self, data_source: DataSource, item_count: int = 0):
        super().__init__()
        self.data_source = data_source
        self.item_count = item_count
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del item"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            DataSourceItem {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
                margin: 2px;
                padding: 5px;
            }
            DataSourceItem:hover {
                background-color: #e6f3ff;
                border-color: #0078d4;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Thumbnail (placeholder por ahora)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(64, 64)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #eee;
                border-radius: 4px;
            }
        """)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setText("IMG")
        layout.addWidget(self.thumbnail_label)
        
        # Información
        info_layout = QVBoxLayout()
        
        # Nombre
        name_label = QLabel(self.data_source.display_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(name_label)
        
        # Tipo
        type_label = QLabel(self.data_source.type_display)
        type_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(type_label)
        
        # Número de items
        count_label = QLabel(f"{self.item_count} elementos")
        count_label.setStyleSheet("color: #666; font-size: 11px;")
        info_layout.addWidget(count_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Cargar thumbnail si existe
        if self.data_source.thumbnail_url:
            self.load_thumbnail()
    
    def load_thumbnail(self):
        """Carga el thumbnail de manera asíncrona"""
        # TODO: Implementar carga asíncrona de imágenes
        pass
    
    def mousePressEvent(self, event):
        """Maneja el click en el item"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.data_source.id)
        super().mousePressEvent(event)

class AddDataSourceDialog(QDialog):
    """Diálogo para añadir nueva fuente de datos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir Fuente de Datos")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        
        # Nombre
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nombre de la fuente")
        form_layout.addRow("Nombre:", self.name_edit)
        
        # Tipo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Canal YouTube", "Feed RSS", "Página Web"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        form_layout.addRow("Tipo:", self.type_combo)
        
        # URL
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://...")
        form_layout.addRow("URL:", self.url_edit)
        
        # Descripción
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Descripción opcional")
        form_layout.addRow("Descripción:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.test_button = QPushButton("Probar")
        self.test_button.clicked.connect(self.test_source)
        buttons_layout.addWidget(self.test_button)
        
        buttons_layout.addStretch()
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        
        ok_button = QPushButton("Añadir")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        buttons_layout.addWidget(ok_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def on_type_changed(self, type_text):
        """Actualiza placeholder según el tipo"""
        placeholders = {
            "Canal YouTube": "https://www.youtube.com/channel/UCxxxxx o https://www.youtube.com/@usuario",
            "Feed RSS": "https://ejemplo.com/feed.xml",
            "Página Web": "https://ejemplo.com/articulo"
        }
        self.url_edit.setPlaceholderText(placeholders.get(type_text, "https://..."))
    
    def test_source(self):
        """Prueba la fuente de datos"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Por favor ingrese una URL")
            return
        
        try:
            # Determinar tipo de fuente
            source_type = self.get_source_type()
            
            if source_type == "youtube":
                rss_manager = RSSManager()
                rss_url = rss_manager.get_youtube_rss_url(url)
                feed_data = rss_manager.parse_feed(rss_url)
                QMessageBox.information(self, "Éxito", 
                    f"Canal encontrado: {feed_data['channel']['title']}\n"
                    f"Entradas: {feed_data['total_entries']}")
            
            elif source_type == "rss":
                rss_manager = RSSManager()
                if rss_manager.validate_feed_url(url):
                    feed_data = rss_manager.parse_feed(url)
                    QMessageBox.information(self, "Éxito",
                        f"Feed válido: {feed_data['channel']['title']}\n"
                        f"Entradas: {feed_data['total_entries']}")
                else:
                    QMessageBox.warning(self, "Error", "URL de RSS no válida")
            
            else:  # web
                from services.web_extractor import WebExtractor
                extractor = WebExtractor()
                if extractor.is_valid_url(url):
                    QMessageBox.information(self, "Éxito", "URL válida")
                else:
                    QMessageBox.warning(self, "Error", "URL no válida")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error probando fuente: {str(e)}")
    
    def get_source_type(self) -> str:
        """Obtiene el tipo de fuente seleccionado"""
        type_mapping = {
            "Canal YouTube": "youtube",
            "Feed RSS": "rss",
            "Página Web": "web"
        }
        return type_mapping.get(self.type_combo.currentText(), "web")
    
    def get_data(self) -> Dict[str, str]:
        """Obtiene los datos del formulario"""
        return {
            'name': self.name_edit.text().strip(),
            'type': self.get_source_type(),
            'url': self.url_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip()
        }

class DataSourceWidget(QWidget):
    """Widget principal para gestión de fuentes de datos"""
    
    source_selected = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.data_sources = []
        self.setup_ui()
        self.load_data_sources()
    
    def setup_ui(self):
        """Configura la interfaz del widget"""
        layout = QVBoxLayout()
        
        # Título y botón añadir
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Fuentes de Datos")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        add_button = QPushButton("Añadir")
        add_button.clicked.connect(self.add_data_source)
        header_layout.addWidget(add_button)
        
        layout.addLayout(header_layout)
        
        # Lista de fuentes
        self.sources_list = QListWidget()
        self.sources_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget::item {
                border: none;
                padding: 2px;
            }
        """)
        layout.addWidget(self.sources_list)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Actualizar")
        refresh_button.clicked.connect(self.refresh_sources)
        actions_layout.addWidget(refresh_button)
        
        actions_layout.addStretch()
        
        remove_button = QPushButton("Eliminar")
        remove_button.clicked.connect(self.remove_selected_source)
        actions_layout.addWidget(remove_button)
        
        layout.addLayout(actions_layout)
        self.setLayout(layout)
    
    def load_data_sources(self):
        """Carga las fuentes de datos desde la base de datos"""
        try:
            sources_data = self.db_manager.get_data_sources()
            self.data_sources = []
            self.sources_list.clear()
            
            for source_data in sources_data:
                # Crear objeto DataSource
                data_source = DataSource(
                    id=source_data['id'],
                    name=source_data['name'],
                    type=source_data['type'],
                    url=source_data['url'],
                    thumbnail_url=source_data['thumbnail_url'],
                    description=source_data['description'],
                    active=bool(source_data['active'])
                )
                
                # Obtener número de items
                item_count = self.db_manager.get_item_count_by_source(data_source.id)
                
                # Crear widget del item
                item_widget = DataSourceItem(data_source, item_count)
                item_widget.clicked.connect(self.on_source_clicked)
                
                # Añadir a la lista
                list_item = QListWidgetItem()
                list_item.setSizeHint(item_widget.sizeHint())
                self.sources_list.addItem(list_item)
                self.sources_list.setItemWidget(list_item, item_widget)
                
                self.data_sources.append(data_source)
                
        except Exception as e:
            logger.error(f"Error cargando fuentes de datos: {e}")
    
    def add_data_source(self):
        """Añade una nueva fuente de datos"""
        dialog = AddDataSourceDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                
                if not all([data['name'], data['url']]):
                    QMessageBox.warning(self, "Error", "Por favor complete todos los campos requeridos")
                    return
                
                # Añadir a la base de datos
                source_id = self.db_manager.add_data_source(
                    name=data['name'],
                    source_type=data['type'],
                    url=data['url'],
                    description=data['description']
                )
                
                logger.info(f"Fuente de datos añadida: {data['name']}")
                self.load_data_sources()
                
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error añadiendo fuente: {str(e)}")
    
    def remove_selected_source(self):
        """Elimina la fuente seleccionada y todo su contenido asociado"""
        current_row = self.sources_list.currentRow()
        if current_row >= 0 and current_row < len(self.data_sources):
            source = self.data_sources[current_row]
            
            try:
                # Obtener información detallada sobre lo que se eliminará
                deletion_info = self.db_manager.get_source_deletion_info(source.id)
                
                if not deletion_info:
                    QMessageBox.warning(self, "Error", "No se pudo obtener información de la fuente")
                    return
                
                # Mostrar diálogo de confirmación avanzada
                dialog = DeleteConfirmationDialog(deletion_info, self)
                
                if dialog.exec() == QDialog.Accepted:
                    # Proceder con la eliminación
                    success = self._perform_deletion(source.id, deletion_info)
                    
                    if success:
                        # Mostrar reporte de eliminación
                        self._show_deletion_report(deletion_info)
                        # Recargar la lista
                        self.load_data_sources()
                    else:
                        QMessageBox.critical(self, "Error", 
                            "Error durante la eliminación. Consulte los logs para más detalles.")
                
            except Exception as e:
                logger.error(f"Error en eliminación de fuente: {e}")
                QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
    
    def _perform_deletion(self, source_id: int, deletion_info: Dict[str, Any]) -> bool:
        """Realiza la eliminación completa de la fuente y sus archivos"""
        try:
            # 1. Eliminar archivos de audio físicos
            audio_deletion_results = None
            if deletion_info['audio_file_paths']:
                audio_deletion_results = FileManager.delete_audio_files(
                    deletion_info['audio_file_paths']
                )
                logger.info(f"Eliminación de archivos de audio: {audio_deletion_results}")
            
            # 2. Eliminar registros de base de datos
            db_success = self.db_manager.delete_data_source_and_content(source_id)
            
            if not db_success:
                logger.error("Error eliminando registros de base de datos")
                return False
            
            # 3. Limpiar directorios vacíos
            audio_dir = FileManager.get_audio_directory()
            deleted_dirs = FileManager.clean_empty_directories(audio_dir)
            if deleted_dirs > 0:
                logger.info(f"Se eliminaron {deleted_dirs} directorios vacíos")
            
            logger.info(f"Eliminación completa exitosa para fuente {source_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error durante eliminación completa: {e}")
            return False
    
    def _show_deletion_report(self, deletion_info: Dict[str, Any]):
        """Muestra un reporte de lo que se eliminó"""
        total_items = deletion_info['total_items']
        audio_files = deletion_info['audio_files_count']
        logs = deletion_info['processing_logs']
        
        report = f"""Eliminación completada exitosamente:

📝 Fuente: {deletion_info['source_name']}
📄 Items de contenido eliminados: {total_items}
🎵 Archivos de audio eliminados: {audio_files}
📊 Registros de procesamiento eliminados: {logs}

La fuente y todo su contenido asociado han sido eliminados permanentemente."""
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Eliminación Completada")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("✅ Eliminación completada exitosamente")
        msg_box.setDetailedText(report)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def refresh_sources(self):
        """Actualiza las fuentes de datos"""
        self.load_data_sources()
    
    def on_source_clicked(self, source_id: int):
        """Maneja el click en una fuente"""
        self.source_selected.emit(source_id)
