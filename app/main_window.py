"""
Ventana principal de la aplicación PyPodcast
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QSplitter, QMenuBar, QStatusBar, QMessageBox,
                              QDialog, QLabel, QTextEdit, QPushButton,
                              QProgressDialog, QApplication)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap, QFont, QAction
import sys
from pathlib import Path
from typing import Optional

from app.widgets.data_source_widget import DataSourceWidget
from app.widgets.content_list_widget import ContentListWidget
from app.widgets.audio_player_widget import AudioPlayerWidget
from models.database import DatabaseManager
from services.rss_manager import RSSManager
from utils.config import config_manager
from utils.logger import get_logger

logger = get_logger(__name__)

class FeedUpdateThread(QThread):
    """Hilo para actualizar feeds RSS en background"""
    
    progress_updated = Signal(int, str)
    update_finished = Signal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.rss_manager = RSSManager()
    
    def run(self):
        """Actualiza todos los feeds RSS"""
        try:
            sources = self.db_manager.get_data_sources()
            total_sources = len(sources)
            
            if total_sources == 0:
                self.update_finished.emit(True, "No hay fuentes para actualizar")
                return
            
            updated_count = 0
            new_items_count = 0
            
            for i, source in enumerate(sources):
                source_id = source['id']
                source_name = source['name']
                source_type = source['type']
                source_url = source['url']
                
                progress = int((i / total_sources) * 100)
                self.progress_updated.emit(progress, f"Actualizando {source_name}...")
                
                try:
                    if source_type in ['youtube', 'rss']:
                        # Obtener URL de RSS si es YouTube
                        if source_type == 'youtube':
                            rss_url = self.rss_manager.get_youtube_rss_url(source_url)
                        else:
                            rss_url = source_url
                        
                        # Parsear feed
                        feed_data = self.rss_manager.parse_feed(rss_url)
                        
                        # Añadir nuevos items
                        for entry in feed_data['entries']:
                            try:
                                item_id = self.db_manager.add_content_item(
                                    source_id=source_id,
                                    title=entry['title'],
                                    url=entry['url'],
                                    description=entry['description'],
                                    published_date=entry['published_date']
                                )
                                if item_id:
                                    new_items_count += 1
                            except Exception:
                                # Item ya existe, continuar
                                pass
                        
                        updated_count += 1
                        
                    elif source_type == 'web':
                        # Para páginas web individuales, verificar si cambió
                        # TODO: Implementar detección de cambios en páginas web
                        pass
                        
                except Exception as e:
                    logger.error(f"Error actualizando fuente {source_name}: {e}")
                    continue
            
            self.progress_updated.emit(100, "Actualización completada")
            
            message = f"Actualización completada.\n"
            message += f"Fuentes actualizadas: {updated_count}/{total_sources}\n"
            message += f"Nuevos elementos: {new_items_count}"
            
            self.update_finished.emit(True, message)
            
        except Exception as e:
            logger.error(f"Error en actualización de feeds: {e}")
            self.update_finished.emit(False, f"Error: {str(e)}")

class AboutDialog(QDialog):
    """Diálogo Acerca de"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de PyPodcast")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        layout = QVBoxLayout()
        
        # Logo y título
        title_label = QLabel("PyPodcast")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #0078d4;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Versión
        version_label = QLabel("Versión 1.0.0")
        version_label.setStyleSheet("font-size: 14px; color: #666;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Descripción
        description = QTextEdit()
        description.setReadOnly(True)
        description.setMaximumHeight(150)
        description.setText("""
Generador automático de podcasts a partir de contenido web y videos de YouTube.

Características:
• Extracción de contenido de múltiples fuentes
• Generación automática de resúmenes
• Síntesis de voz usando macOS
• Reproductor integrado
• Gestión de estados de contenido

Desarrollado con Python 3.9 y PySide6.
        """)
        layout.addWidget(description)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_source_id = None
        self.feed_update_thread = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_timers()
        self.connect_signals()
        
        # Configuración inicial de ventana
        self.apply_window_config()
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal con splitter horizontal
        main_layout = QHBoxLayout()
        
        # Splitter principal (horizontal)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Lista de contenido
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.content_list_widget = ContentListWidget()
        left_layout.addWidget(self.content_list_widget)
        
        # Reproductor de audio en la parte inferior
        self.audio_player_widget = AudioPlayerWidget()
        left_layout.addWidget(self.audio_player_widget)
        
        left_panel.setLayout(left_layout)
        main_splitter.addWidget(left_panel)
        
        # Panel derecho: Fuentes de datos
        self.data_source_widget = DataSourceWidget()
        main_splitter.addWidget(self.data_source_widget)
        
        # Proporciones del splitter (70% contenido, 30% fuentes)
        main_splitter.setSizes([700, 300])
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        
        main_layout.addWidget(main_splitter)
        central_widget.setLayout(main_layout)
    
    def setup_menu(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        
        # Acción actualizar feeds
        update_action = QAction("Actualizar Feeds", self)
        update_action.setShortcut("Ctrl+R")
        update_action.triggered.connect(self.update_all_feeds)
        file_menu.addAction(update_action)
        
        file_menu.addSeparator()
        
        # Acción salir
        exit_action = QAction("Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu("Herramientas")
        
        # Configuración
        config_action = QAction("Configuración", self)
        config_action.triggered.connect(self.show_config)
        tools_menu.addAction(config_action)
        
        # Base de datos
        db_action = QAction("Estadísticas", self)
        db_action.triggered.connect(self.show_statistics)
        tools_menu.addAction(db_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")
        
        # Acerca de
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Configura la barra de estado"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Listo")
        
        # Etiqueta de estado de feeds
        self.feeds_status_label = QLabel("Feeds: Actualizados")
        self.status_bar.addPermanentWidget(self.feeds_status_label)
    
    def setup_timers(self):
        """Configura timers para actualizaciones automáticas"""
        # Timer para actualización automática de feeds
        if config_manager.get('ui.auto_refresh', True):
            self.auto_refresh_timer = QTimer()
            self.auto_refresh_timer.timeout.connect(self.update_all_feeds)
            
            # Intervalo en minutos
            interval_minutes = config_manager.get('ui.refresh_interval_minutes', 60)
            self.auto_refresh_timer.start(interval_minutes * 60 * 1000)
    
    def connect_signals(self):
        """Conecta señales entre widgets"""
        # Cuando se selecciona una fuente de datos
        self.data_source_widget.source_selected.connect(self.on_source_selected)
        
        # Cuando se selecciona un item de contenido
        self.content_list_widget.item_selected.connect(self.on_item_selected)
    
    def apply_window_config(self):
        """Aplica configuración de ventana"""
        # Tamaño y título
        width = config_manager.get('ui.window_width', 1200)
        height = config_manager.get('ui.window_height', 800)
        self.resize(width, height)
        self.setWindowTitle("PyPodcast - Generador de Podcasts")
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.primaryScreen().availableGeometry()
        window = self.frameGeometry()
        center = screen.center()
        window.moveCenter(center)
        self.move(window.topLeft())
    
    def on_source_selected(self, source_id: int):
        """Maneja la selección de una fuente de datos"""
        self.current_source_id = source_id
        self.content_list_widget.set_data_source(source_id)
        self.status_bar.showMessage(f"Mostrando contenido de la fuente seleccionada")
    
    def on_item_selected(self, item_id: int):
        """Maneja la selección de un item de contenido"""
        try:
            # Obtener información del item
            items = self.db_manager.get_content_items()
            selected_item = None
            
            for item in items:
                if item['id'] == item_id:
                    selected_item = item
                    break
            
            if selected_item and selected_item['audio_file']:
                audio_file = selected_item['audio_file']
                if Path(audio_file).exists():
                    # Cargar en el reproductor
                    if self.audio_player_widget.load_audio_file(audio_file, selected_item['title']):
                        self.status_bar.showMessage(f"Audio cargado: {selected_item['title']}")
                    else:
                        self.status_bar.showMessage("Error cargando audio")
                else:
                    self.status_bar.showMessage("Archivo de audio no encontrado")
            else:
                self.status_bar.showMessage("El item seleccionado no tiene audio generado")
                
        except Exception as e:
            logger.error(f"Error seleccionando item: {e}")
            self.status_bar.showMessage("Error seleccionando item")
    
    def update_all_feeds(self):
        """Actualiza todos los feeds RSS"""
        if self.feed_update_thread and self.feed_update_thread.isRunning():
            QMessageBox.information(self, "Info", "Ya se está ejecutando una actualización")
            return
        
        # Mostrar diálogo de progreso
        self.progress_dialog = QProgressDialog("Actualizando feeds...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setWindowTitle("Actualización de Feeds")
        self.progress_dialog.show()
        
        # Iniciar actualización en hilo separado
        self.feed_update_thread = FeedUpdateThread()
        self.feed_update_thread.progress_updated.connect(self.on_update_progress)
        self.feed_update_thread.update_finished.connect(self.on_update_finished)
        self.feed_update_thread.start()
        
        self.feeds_status_label.setText("Feeds: Actualizando...")
    
    def on_update_progress(self, progress: int, message: str):
        """Actualiza progreso de actualización"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(message)
    
    def on_update_finished(self, success: bool, message: str):
        """Finaliza actualización de feeds"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        if success:
            self.feeds_status_label.setText("Feeds: Actualizados")
            self.status_bar.showMessage("Feeds actualizados correctamente")
            
            # Refrescar widgets
            self.data_source_widget.refresh_sources()
            if self.current_source_id:
                self.content_list_widget.load_content_items()
            
            # Mostrar resumen si hay nuevos items
            if "Nuevos elementos:" in message:
                QMessageBox.information(self, "Actualización Completada", message)
        else:
            self.feeds_status_label.setText("Feeds: Error")
            self.status_bar.showMessage("Error actualizando feeds")
            QMessageBox.warning(self, "Error de Actualización", message)
    
    def show_config(self):
        """Muestra diálogo de configuración"""
        # TODO: Implementar diálogo de configuración
        QMessageBox.information(self, "Configuración", "Diálogo de configuración pendiente de implementar")
    
    def show_statistics(self):
        """Muestra estadísticas de la base de datos"""
        try:
            sources = self.db_manager.get_data_sources()
            all_items = self.db_manager.get_content_items()
            
            # Contar por estado
            status_counts = {}
            for item in all_items:
                status = item['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            stats_text = f"""Estadísticas de PyPodcast:

Fuentes de datos: {len(sources)}
Total de elementos: {len(all_items)}

Por estado:
• Nuevos: {status_counts.get('nuevo', 0)}
• Procesados: {status_counts.get('procesado', 0)}
• Escuchados: {status_counts.get('escuchado', 0)}
• Ignorados: {status_counts.get('ignorar', 0)}
"""
            
            QMessageBox.information(self, "Estadísticas", stats_text)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error obteniendo estadísticas: {str(e)}")
    
    def show_about(self):
        """Muestra diálogo Acerca de"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def closeEvent(self, event):
        """Maneja el cierre de la aplicación"""
        try:
            # Detener timers
            if hasattr(self, 'auto_refresh_timer'):
                self.auto_refresh_timer.stop()
            
            # Detener hilo de actualización si está corriendo
            if self.feed_update_thread and self.feed_update_thread.isRunning():
                self.feed_update_thread.terminate()
                self.feed_update_thread.wait(3000)  # Esperar máximo 3 segundos
            
            # Limpiar reproductor de audio
            self.audio_player_widget.cleanup()
            
            # Guardar configuración de ventana
            config_manager.set('ui.window_width', self.width())
            config_manager.set('ui.window_height', self.height())
            config_manager.save_config()
            
            logger.info("Aplicación cerrada correctamente")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error cerrando aplicación: {e}")
            event.accept()
