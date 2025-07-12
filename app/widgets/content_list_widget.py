"""
Widget de lista de items de contenido
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                              QListWidgetItem, QLabel, QPushButton, QFrame,
                              QComboBox, QLineEdit, QTextEdit, QMessageBox,
                              QProgressBar, QMenu)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QPixmap, QIcon, QAction
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from models.database import DatabaseManager
from models.content_item import ContentItem
from utils.logger import get_logger

logger = get_logger(__name__)

class ContentItemWidget(QFrame):
    """Widget para mostrar un item de contenido"""
    
    clicked = Signal(int)
    action_requested = Signal(int, str)  # item_id, action
    
    def __init__(self, content_item: ContentItem):
        super().__init__()
        self.content_item = content_item
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del item"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(self._get_style_for_status())
        
        layout = QVBoxLayout()
        
        # Header con título y estado
        header_layout = QHBoxLayout()
        
        # Título
        title_label = QLabel(self.content_item.display_title)
        title_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Estado
        status_label = QLabel(self.content_item.status_display)
        status_label.setStyleSheet(self._get_status_label_style())
        header_layout.addWidget(status_label)
        
        layout.addLayout(header_layout)
        
        # Descripción (si existe)
        if self.content_item.description:
            desc_label = QLabel(self.content_item.description[:150] + "..." 
                              if len(self.content_item.description) > 150 
                              else self.content_item.description)
            desc_label.setStyleSheet("color: #666; font-size: 11px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Footer con información adicional
        footer_layout = QHBoxLayout()
        
        # Fuente
        if self.content_item.source_name:
            source_label = QLabel(f"📡 {self.content_item.source_name}")
            source_label.setStyleSheet("color: #888; font-size: 10px;")
            footer_layout.addWidget(source_label)
        
        footer_layout.addStretch()
        
        # Indicadores
        indicators_layout = QHBoxLayout()
        
        if self.content_item.has_summary:
            summary_icon = QLabel("📄")
            summary_icon.setToolTip("Tiene resumen")
            indicators_layout.addWidget(summary_icon)
        
        if self.content_item.has_audio:
            audio_icon = QLabel("🎵")
            audio_icon.setToolTip("Tiene audio generado")
            indicators_layout.addWidget(audio_icon)
        
        footer_layout.addLayout(indicators_layout)
        layout.addLayout(footer_layout)
        
        self.setLayout(layout)
    
    def _get_style_for_status(self) -> str:
        """Obtiene el estilo según el estado"""
        base_style = """
            ContentItemWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: #fff;
                margin: 1px;
                padding: 8px;
            }
            ContentItemWidget:hover {
                border-color: #0078d4;
                background-color: #f5f9ff;
            }
        """
        
        status_colors = {
            'nuevo': '#e6f3ff',
            'procesado': '#e6ffe6',
            'escuchado': '#f0f0f0',
            'ignorar': '#ffe6e6'
        }
        
        bg_color = status_colors.get(self.content_item.status, '#fff')
        return base_style.replace('#fff', bg_color)
    
    def _get_status_label_style(self) -> str:
        """Obtiene el estilo para la etiqueta de estado"""
        status_styles = {
            'nuevo': 'background-color: #0078d4; color: white;',
            'procesado': 'background-color: #107c10; color: white;',
            'escuchado': 'background-color: #605e5c; color: white;',
            'ignorar': 'background-color: #d13438; color: white;'
        }
        
        base_style = """
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """
        
        return base_style + status_styles.get(self.content_item.status, 'background-color: #ccc;')
    
    def mousePressEvent(self, event):
        """Maneja el click en el item"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.content_item.id)
        super().mousePressEvent(event)
    
    def contextMenuEvent(self, event):
        """Menú contextual"""
        menu = QMenu(self)
        
        # Acciones según el estado
        if self.content_item.status == 'nuevo':
            process_action = QAction("Procesar", self)
            process_action.triggered.connect(lambda: self.action_requested.emit(self.content_item.id, 'process'))
            menu.addAction(process_action)
        
        if self.content_item.has_audio:
            play_action = QAction("Reproducir", self)
            play_action.triggered.connect(lambda: self.action_requested.emit(self.content_item.id, 'play'))
            menu.addAction(play_action)
        
        # Cambiar estado
        status_menu = menu.addMenu("Cambiar estado")
        
        for status, display in [('nuevo', 'Nuevo'), ('procesado', 'Procesado'), 
                               ('escuchado', 'Escuchado'), ('ignorar', 'Ignorar')]:
            if status != self.content_item.status:
                action = QAction(display, self)
                action.triggered.connect(lambda checked, s=status: self.action_requested.emit(self.content_item.id, f'status_{s}'))
                status_menu.addAction(action)
        
        menu.exec(event.globalPos())

class ContentProcessorThread(QThread):
    """Hilo para procesar contenido en background"""
    
    progress_updated = Signal(int, str)  # progress, message
    processing_finished = Signal(int, bool, str)  # item_id, success, message
    
    def __init__(self, content_item: ContentItem):
        super().__init__()
        self.content_item = content_item
    
    def run(self):
        """Procesa el contenido"""
        try:
            from services.web_extractor import WebExtractor
            from services.youtube_transcriber import YouTubeTranscriber
            from services.text_to_speech import TextToSpeechService
            
            db_manager = DatabaseManager()
            
            self.progress_updated.emit(10, "Iniciando procesamiento...")
            
            # Determinar tipo de contenido y extraer
            content_text = ""
            
            if self.content_item.source_type == 'youtube':
                self.progress_updated.emit(20, "Obteniendo transcripción...")
                transcriber = YouTubeTranscriber()
                if transcriber.is_youtube_url(self.content_item.url):
                    transcript_data = transcriber.get_transcript(self.content_item.url)
                    content_text = transcript_data['summary'] or transcript_data['transcript']
                else:
                    raise ValueError("URL de YouTube no válida")
            
            else:  # web o rss
                self.progress_updated.emit(20, "Extrayendo contenido...")
                extractor = WebExtractor()
                content_data = extractor.extract_content(self.content_item.url)
                content_text = extractor.get_content_summary(content_data['content'])
            
            if not content_text:
                raise ValueError("No se pudo extraer contenido")
            
            self.progress_updated.emit(50, "Generando resumen...")
            
            # Actualizar resumen en base de datos
            db_manager.update_content_item_files(self.content_item.id, summary=content_text)
            
            self.progress_updated.emit(70, "Generando audio...")
            
            # Generar audio
            tts_service = TextToSpeechService()
            audio_file = tts_service.create_podcast_with_intro(
                content_text, 
                self.content_item.title,
                self.content_item.source_name
            )
            
            self.progress_updated.emit(90, "Finalizando...")
            
            # Actualizar archivo de audio y estado
            db_manager.update_content_item_files(self.content_item.id, audio_file=audio_file)
            db_manager.update_content_item_status(self.content_item.id, 'procesado')
            
            # Log de procesamiento
            db_manager.log_processing_action(
                self.content_item.id, 
                'process', 
                'success', 
                'Contenido procesado correctamente'
            )
            
            self.progress_updated.emit(100, "Completado")
            self.processing_finished.emit(self.content_item.id, True, "Procesamiento completado")
            
        except Exception as e:
            logger.error(f"Error procesando contenido {self.content_item.id}: {e}")
            
            # Log de error
            try:
                db_manager = DatabaseManager()
                db_manager.log_processing_action(
                    self.content_item.id, 
                    'process', 
                    'error', 
                    str(e)
                )
            except:
                pass
            
            self.processing_finished.emit(self.content_item.id, False, str(e))

class ContentListWidget(QWidget):
    """Widget principal para la lista de contenido"""
    
    item_selected = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.current_source_id = None
        self.content_items = []
        self.processing_threads = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del widget"""
        layout = QVBoxLayout()
        
        # Header con filtros
        header_layout = QVBoxLayout()
        
        # Título
        self.title_label = QLabel("Contenido")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.title_label)
        
        # Filtros
        filters_layout = QHBoxLayout()
        
        # Filtro por estado
        status_label = QLabel("Estado:")
        filters_layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Nuevo", "Procesado", "Escuchado", "Ignorar"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.status_filter)
        
        filters_layout.addStretch()
        
        # Búsqueda
        search_label = QLabel("Buscar:")
        filters_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Título, descripción...")
        self.search_edit.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.search_edit)
        
        header_layout.addLayout(filters_layout)
        layout.addLayout(header_layout)
        
        # Lista de contenido
        self.content_list = QListWidget()
        self.content_list.setStyleSheet("""
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
        layout.addWidget(self.content_list)
        
        # Barra de progreso para procesamiento
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        self.process_all_button = QPushButton("Procesar Todos")
        self.process_all_button.clicked.connect(self.process_all_new)
        actions_layout.addWidget(self.process_all_button)
        
        actions_layout.addStretch()
        
        refresh_button = QPushButton("Actualizar")
        refresh_button.clicked.connect(self.refresh_content)
        actions_layout.addWidget(refresh_button)
        
        layout.addLayout(actions_layout)
        self.setLayout(layout)
    
    def set_data_source(self, source_id: int):
        """Establece la fuente de datos actual"""
        self.current_source_id = source_id
        self.load_content_items()
    
    def load_content_items(self):
        """Carga los items de contenido"""
        if not self.current_source_id:
            return
        
        try:
            items_data = self.db_manager.get_content_items(source_id=self.current_source_id)
            self.content_items = []
            
            for item_data in items_data:
                content_item = ContentItem(
                    id=item_data['id'],
                    source_id=item_data['source_id'],
                    title=item_data['title'],
                    url=item_data['url'],
                    description=item_data['description'],
                    content=item_data['content'],
                    summary=item_data['summary'],
                    audio_file=item_data['audio_file'],
                    thumbnail_url=item_data['thumbnail_url'],
                    status=item_data['status'],
                    source_name=item_data['source_name'],
                    source_type=item_data['source_type']
                )
                self.content_items.append(content_item)
            
            self.apply_filters()
            
            # Actualizar título
            source_name = items_data[0]['source_name'] if items_data else "Fuente"
            self.title_label.setText(f"Contenido - {source_name}")
            
        except Exception as e:
            logger.error(f"Error cargando items de contenido: {e}")
    
    def apply_filters(self):
        """Aplica filtros a la lista"""
        self.content_list.clear()
        
        status_filter = self.status_filter.currentText().lower()
        search_text = self.search_edit.text().lower()
        
        filtered_items = []
        
        for item in self.content_items:
            # Filtro por estado
            if status_filter != "todos" and item.status != status_filter:
                continue
            
            # Filtro por búsqueda
            if search_text:
                searchable_text = f"{item.title} {item.description or ''}".lower()
                if search_text not in searchable_text:
                    continue
            
            filtered_items.append(item)
        
        # Añadir items filtrados a la lista
        for item in filtered_items:
            item_widget = ContentItemWidget(item)
            item_widget.clicked.connect(self.on_item_clicked)
            item_widget.action_requested.connect(self.handle_item_action)
            
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.content_list.addItem(list_item)
            self.content_list.setItemWidget(list_item, item_widget)
    
    def on_item_clicked(self, item_id: int):
        """Maneja el click en un item"""
        self.item_selected.emit(item_id)
    
    def handle_item_action(self, item_id: int, action: str):
        """Maneja acciones en los items"""
        try:
            if action == 'process':
                self.process_item(item_id)
            elif action == 'play':
                self.play_item(item_id)
            elif action.startswith('status_'):
                new_status = action.replace('status_', '')
                self.change_item_status(item_id, new_status)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error ejecutando acción: {str(e)}")
    
    def process_item(self, item_id: int):
        """Procesa un item individual"""
        # Buscar el item
        item = None
        for content_item in self.content_items:
            if content_item.id == item_id:
                item = content_item
                break
        
        if not item:
            return
        
        # Iniciar procesamiento en hilo separado
        thread = ContentProcessorThread(item)
        thread.progress_updated.connect(self.on_processing_progress)
        thread.processing_finished.connect(self.on_processing_finished)
        
        self.processing_threads[item_id] = thread
        self.progress_bar.setVisible(True)
        thread.start()
    
    def process_all_new(self):
        """Procesa todos los items nuevos"""
        new_items = [item for item in self.content_items if item.status == 'nuevo']
        
        if not new_items:
            QMessageBox.information(self, "Info", "No hay items nuevos para procesar")
            return
        
        reply = QMessageBox.question(self, "Confirmar",
            f"¿Procesar {len(new_items)} items nuevos?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for item in new_items:
                self.process_item(item.id)
    
    def play_item(self, item_id: int):
        """Reproduce un item"""
        # TODO: Implementar reproducción
        QMessageBox.information(self, "Info", "Funcionalidad de reproducción pendiente")
    
    def change_item_status(self, item_id: int, new_status: str):
        """Cambia el estado de un item"""
        try:
            self.db_manager.update_content_item_status(item_id, new_status)
            self.load_content_items()
        except Exception as e:
            logger.error(f"Error cambiando estado: {e}")
    
    def on_processing_progress(self, progress: int, message: str):
        """Actualiza progreso de procesamiento"""
        self.progress_bar.setValue(progress)
        self.progress_bar.setFormat(f"{message} ({progress}%)")
    
    def on_processing_finished(self, item_id: int, success: bool, message: str):
        """Finaliza procesamiento"""
        if item_id in self.processing_threads:
            del self.processing_threads[item_id]
        
        if not self.processing_threads:
            self.progress_bar.setVisible(False)
        
        if success:
            self.load_content_items()
        else:
            QMessageBox.warning(self, "Error de Procesamiento", message)
    
    def refresh_content(self):
        """Actualiza la lista de contenido"""
        self.load_content_items()
