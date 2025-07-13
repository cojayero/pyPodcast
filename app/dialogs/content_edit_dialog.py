"""
Diálogo para editar el contenido de texto de un item
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTextEdit, QPushButton, QMessageBox, QSplitter,
                              QFrame, QScrollArea, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional

from models.content_item import ContentItem
from models.database import DatabaseManager
from services.text_to_speech import TextToSpeechService
from utils.logger import get_logger

logger = get_logger(__name__)

class ContentEditDialog(QDialog):
    """Diálogo para editar el contenido de texto de un item"""
    
    content_updated = Signal(int)  # item_id
    
    def __init__(self, content_item: ContentItem, parent=None):
        super().__init__(parent)
        self.content_item = content_item
        self.db_manager = DatabaseManager()
        self.tts_service = TextToSpeechService()
        
        self.original_content = content_item.content or ""
        self.original_summary = content_item.summary or ""
        
        self.setup_ui()
        self.load_content()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle(f"Editar Contenido - {self.content_item.display_title}")
        self.setGeometry(100, 100, 1000, 700)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Header con información del item
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 5px; padding: 10px;")
        header_layout = QVBoxLayout(header_frame)
        
        # Título del item
        title_label = QLabel(self.content_item.display_title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label)
        
        # Información adicional
        info_text = f"🔗 URL: {self.content_item.url}\n"
        if self.content_item.source_name:
            info_text += f"📡 Fuente: {self.content_item.source_name}\n"
        info_text += f"📊 Estado: {self.content_item.status_display}"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        info_label.setWordWrap(True)
        header_layout.addWidget(info_label)
        
        layout.addWidget(header_frame)
        
        # Splitter principal para dividir contenido original y editado
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Contenido original
        left_panel = self.create_original_content_panel()
        main_splitter.addWidget(left_panel)
        
        # Panel derecho - Contenido editable
        right_panel = self.create_editable_content_panel()
        main_splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        main_splitter.setSizes([400, 600])
        layout.addWidget(main_splitter)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        # Botón para generar audio de prueba
        self.preview_audio_btn = QPushButton("🎵 Generar Audio de Prueba")
        self.preview_audio_btn.clicked.connect(self.generate_preview_audio)
        buttons_layout.addWidget(self.preview_audio_btn)
        
        buttons_layout.addStretch()
        
        # Botones estándar
        self.reset_btn = QPushButton("Restaurar Original")
        self.reset_btn.clicked.connect(self.reset_content)
        buttons_layout.addWidget(self.reset_btn)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Guardar Cambios")
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setDefault(True)
        self.save_btn.setStyleSheet("QPushButton { background-color: #0078d4; color: white; font-weight: bold; }")
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def create_original_content_panel(self) -> QGroupBox:
        """Crea el panel con el contenido original"""
        group_box = QGroupBox("Contenido Original (Solo Lectura)")
        layout = QVBoxLayout()
        
        # Texto original
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ddd;")
        
        layout.addWidget(self.original_text)
        
        # Información del contenido original
        self.original_info_label = QLabel()
        self.original_info_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        layout.addWidget(self.original_info_label)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_editable_content_panel(self) -> QGroupBox:
        """Crea el panel con el contenido editable"""
        group_box = QGroupBox("Contenido para Audio (Editable)")
        layout = QVBoxLayout()
        
        # Instrucciones
        instructions = QLabel(
            "💡 Edita el texto que se utilizará para generar el audio del podcast. "
            "Puedes modificar, resumir o reorganizar el contenido según tus necesidades."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #e6f3ff; padding: 8px; border-radius: 4px; margin-bottom: 5px;")
        layout.addWidget(instructions)
        
        # Editor de texto
        self.editable_text = QTextEdit()
        self.editable_text.setPlaceholderText("Escribe o edita el contenido que se convertirá a audio...")
        self.editable_text.textChanged.connect(self.on_text_changed)
        
        layout.addWidget(self.editable_text)
        
        # Información del contenido editado
        self.edited_info_label = QLabel()
        self.edited_info_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        layout.addWidget(self.edited_info_label)
        
        group_box.setLayout(layout)
        return group_box
    
    def load_content(self):
        """Carga el contenido en los editores"""
        # Cargar contenido original
        display_content = ""
        
        if self.content_item.content:
            display_content = self.content_item.content
        elif self.content_item.summary:
            display_content = self.content_item.summary
        elif self.content_item.description:
            display_content = self.content_item.description
        else:
            display_content = "No hay contenido disponible"
        
        self.original_text.setPlainText(display_content)
        self.update_original_info()
        
        # Cargar contenido editable (usar summary si existe, sino el contenido completo)
        editable_content = self.content_item.summary or display_content
        self.editable_text.setPlainText(editable_content)
        self.update_edited_info()
    
    def update_original_info(self):
        """Actualiza la información del contenido original"""
        text = self.original_text.toPlainText()
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        
        info = f"📝 {char_count:,} caracteres • {word_count:,} palabras"
        self.original_info_label.setText(info)
    
    def update_edited_info(self):
        """Actualiza la información del contenido editado"""
        text = self.editable_text.toPlainText()
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        
        # Estimar duración del audio (aproximadamente 150 palabras por minuto)
        estimated_minutes = word_count / 150 if word_count > 0 else 0
        
        info = f"📝 {char_count:,} caracteres • {word_count:,} palabras • ⏱️ ~{estimated_minutes:.1f} minutos de audio"
        self.edited_info_label.setText(info)
    
    def on_text_changed(self):
        """Se ejecuta cuando cambia el texto editable"""
        self.update_edited_info()
        
        # Habilitar/deshabilitar botones según cambios
        current_text = self.editable_text.toPlainText()
        original_editable = self.content_item.summary or self.original_content
        
        has_changes = current_text != original_editable
        self.save_btn.setEnabled(has_changes)
        self.reset_btn.setEnabled(has_changes)
        
        # Habilitar preview solo si hay contenido
        self.preview_audio_btn.setEnabled(bool(current_text.strip()))
    
    def reset_content(self):
        """Restaura el contenido original"""
        reply = QMessageBox.question(
            self, "Confirmar Restauración",
            "¿Estás seguro de que quieres restaurar el contenido original? "
            "Se perderán todos los cambios realizados.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            original_editable = self.content_item.summary or self.original_content
            self.editable_text.setPlainText(original_editable)
    
    def generate_preview_audio(self):
        """Genera un audio de prueba con el contenido editado"""
        try:
            content = self.editable_text.toPlainText().strip()
            if not content:
                QMessageBox.warning(self, "Error", "No hay contenido para generar audio")
                return
            
            # Tomar solo los primeros 500 caracteres para la preview
            preview_content = content[:500]
            if len(content) > 500:
                preview_content += "... [Preview truncado]"
            
            self.preview_audio_btn.setEnabled(False)
            self.preview_audio_btn.setText("🎵 Generando...")
            
            # Generar audio de prueba
            audio_file = self.tts_service.text_to_speech(
                preview_content,
                f"preview_{self.content_item.id}",
                f"Preview - {self.content_item.display_title}"
            )
            
            QMessageBox.information(
                self, "Audio Generado",
                f"Audio de prueba generado exitosamente:\n{audio_file}\n\n"
                f"Puedes reproducirlo para escuchar cómo sonará el contenido."
            )
            
        except Exception as e:
            logger.error(f"Error generando audio de prueba: {e}")
            QMessageBox.critical(
                self, "Error",
                f"Error generando audio de prueba:\n{str(e)}"
            )
        finally:
            self.preview_audio_btn.setEnabled(True)
            self.preview_audio_btn.setText("🎵 Generar Audio de Prueba")
    
    def save_changes(self):
        """Guarda los cambios en la base de datos"""
        try:
            new_content = self.editable_text.toPlainText().strip()
            
            if not new_content:
                QMessageBox.warning(self, "Error", "El contenido no puede estar vacío")
                return
            
            # Actualizar el summary en la base de datos
            self.db_manager.update_content_item_files(self.content_item.id, summary=new_content)
            
            # Si el item ya tenía audio, preguntar si regenerarlo
            if self.content_item.has_audio:
                reply = QMessageBox.question(
                    self, "Regenerar Audio",
                    "El contenido ha sido actualizado. ¿Quieres regenerar "
                    "el archivo de audio con el nuevo contenido?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        # Regenerar audio
                        audio_file = self.tts_service.create_podcast_with_intro(
                            new_content,
                            self.content_item.title,
                            self.content_item.source_name
                        )
                        
                        # Actualizar archivo de audio
                        self.db_manager.update_content_item_files(self.content_item.id, audio_file=audio_file)
                        
                        QMessageBox.information(self, "Éxito", "Contenido y audio actualizados exitosamente")
                    except Exception as e:
                        logger.error(f"Error regenerando audio: {e}")
                        QMessageBox.warning(
                            self, "Advertencia",
                            f"El contenido se guardó correctamente, pero hubo un error "
                            f"regenerando el audio:\n{str(e)}"
                        )
            else:
                QMessageBox.information(self, "Éxito", "Contenido actualizado exitosamente")
            
            # Emitir señal de actualización
            self.content_updated.emit(self.content_item.id)
            
            # Cerrar diálogo
            self.accept()
            
        except Exception as e:
            logger.error(f"Error guardando cambios: {e}")
            QMessageBox.critical(
                self, "Error",
                f"Error guardando los cambios:\n{str(e)}"
            )
    
    def closeEvent(self, event):
        """Maneja el cierre del diálogo"""
        current_text = self.editable_text.toPlainText()
        original_editable = self.content_item.summary or self.original_content
        
        if current_text != original_editable:
            reply = QMessageBox.question(
                self, "Cambios sin Guardar",
                "Hay cambios sin guardar. ¿Quieres guardar antes de cerrar?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_changes()
                return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        event.accept()
