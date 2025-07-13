"""
Diálogo para analizar y comparar contenido original vs resumen
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QTextEdit, QPushButton, QSplitter, QFrame, 
                              QGroupBox, QGridLayout, QProgressBar, QTabWidget,
                              QWidget, QScrollArea, QMessageBox)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor
from typing import Optional, Dict, Any

from models.content_item import ContentItem
from models.database import DatabaseManager
from services.content_analyzer import ContentAnalyzer
from services.text_to_speech import TextToSpeechService
from utils.logger import get_logger

logger = get_logger(__name__)

class ContentAnalysisThread(QThread):
    """Hilo para análisis de contenido en background"""
    
    analysis_finished = Signal(dict)
    
    def __init__(self, content: str, title: str = None):
        super().__init__()
        self.content = content
        self.title = title
        self.analyzer = ContentAnalyzer()
    
    def run(self):
        """Ejecuta el análisis"""
        try:
            analysis = self.analyzer.analyze_content(self.content, self.title)
            self.analysis_finished.emit(analysis)
        except Exception as e:
            logger.error(f"Error en análisis: {e}")
            self.analysis_finished.emit({})

class ContentAnalysisDialog(QDialog):
    """Diálogo para análisis y comparación de contenido"""
    
    content_updated = Signal(int)
    
    def __init__(self, content_item: ContentItem, parent=None):
        super().__init__(parent)
        self.content_item = content_item
        self.db_manager = DatabaseManager()
        self.tts_service = TextToSpeechService()
        
        self.analysis_result = None
        
        self.setup_ui()
        self.start_analysis()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle(f"Análisis de Contenido - {self.content_item.display_title}")
        self.setGeometry(100, 100, 1200, 800)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Header con información del item
        header_frame = self.create_header()
        layout.addWidget(header_frame)
        
        # Tabs principales
        self.tab_widget = QTabWidget()
        
        # Tab 1: Análisis y Comparación
        analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(analysis_tab, "📊 Análisis y Comparación")
        
        # Tab 2: Editor de Resumen
        editor_tab = self.create_editor_tab()
        self.tab_widget.addTab(editor_tab, "✏️ Editor de Resumen")
        
        layout.addWidget(self.tab_widget)
        
        # Botones de acción
        buttons_layout = self.create_buttons()
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def create_header(self) -> QFrame:
        """Crea el header con información del item"""
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
        
        return header_frame
    
    def create_analysis_tab(self) -> QWidget:
        """Crea el tab de análisis"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Progress bar para análisis
        self.analysis_progress = QProgressBar()
        self.analysis_progress.setRange(0, 0)  # Indeterminado
        self.analysis_progress.setVisible(True)
        layout.addWidget(self.analysis_progress)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Contenido original
        left_panel = self.create_original_panel()
        main_splitter.addWidget(left_panel)
        
        # Panel derecho - Resumen y estadísticas
        right_panel = self.create_summary_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([600, 600])
        layout.addWidget(main_splitter)
        
        widget.setLayout(layout)
        return widget
    
    def create_original_panel(self) -> QGroupBox:
        """Crea el panel del contenido original"""
        group_box = QGroupBox("📄 Contenido Original")
        layout = QVBoxLayout()
        
        # Texto original
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ddd;")
        
        # Cargar contenido
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
        layout.addWidget(self.original_text)
        
        # Estadísticas del original
        self.original_stats = QLabel("Analizando...")
        self.original_stats.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(self.original_stats)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_summary_panel(self) -> QGroupBox:
        """Crea el panel del resumen"""
        group_box = QGroupBox("📝 Resumen Inteligente")
        layout = QVBoxLayout()
        
        # Texto del resumen
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("background-color: #f0f8ff; border: 1px solid #0078d4;")
        layout.addWidget(self.summary_text)
        
        # Estadísticas del resumen
        self.summary_stats = QLabel("Generando resumen...")
        self.summary_stats.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        layout.addWidget(self.summary_stats)
        
        # Panel de comparación
        comparison_frame = QFrame()
        comparison_frame.setFrameStyle(QFrame.StyledPanel)
        comparison_frame.setStyleSheet("background-color: #e6f3ff; border-radius: 5px; padding: 8px;")
        comparison_layout = QVBoxLayout(comparison_frame)
        
        comparison_title = QLabel("📊 Comparación")
        comparison_title.setStyleSheet("font-weight: bold; color: #0078d4;")
        comparison_layout.addWidget(comparison_title)
        
        self.comparison_stats = QLabel("Calculando...")
        self.comparison_stats.setStyleSheet("color: #333; font-size: 11px;")
        comparison_layout.addWidget(self.comparison_stats)
        
        layout.addWidget(comparison_frame)
        
        # Frases clave
        key_phrases_frame = QFrame()
        key_phrases_frame.setFrameStyle(QFrame.StyledPanel)
        key_phrases_frame.setStyleSheet("background-color: #fff4e6; border-radius: 5px; padding: 8px;")
        key_phrases_layout = QVBoxLayout(key_phrases_frame)
        
        key_phrases_title = QLabel("🔑 Frases Clave")
        key_phrases_title.setStyleSheet("font-weight: bold; color: #cc7a00;")
        key_phrases_layout.addWidget(key_phrases_title)
        
        self.key_phrases_text = QLabel("Extrayendo...")
        self.key_phrases_text.setStyleSheet("color: #333; font-size: 10px;")
        self.key_phrases_text.setWordWrap(True)
        key_phrases_layout.addWidget(self.key_phrases_text)
        
        layout.addWidget(key_phrases_frame)
        
        group_box.setLayout(layout)
        return group_box
    
    def create_editor_tab(self) -> QWidget:
        """Crea el tab del editor"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instrucciones
        instructions = QLabel(
            "✏️ Aquí puedes editar manualmente el resumen generado o crear uno completamente nuevo. "
            "El texto editado se utilizará para generar el audio del podcast."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #e6f3ff; padding: 8px; border-radius: 4px; margin-bottom: 5px;")
        layout.addWidget(instructions)
        
        # Editor
        self.editable_summary = QTextEdit()
        self.editable_summary.setPlaceholderText("Edita el resumen aquí...")
        self.editable_summary.textChanged.connect(self.on_summary_edited)
        layout.addWidget(self.editable_summary)
        
        # Información del resumen editado
        self.edited_info_label = QLabel()
        self.edited_info_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px;")
        layout.addWidget(self.edited_info_label)
        
        # Botones del editor
        editor_buttons = QHBoxLayout()
        
        self.use_generated_btn = QPushButton("📋 Usar Resumen Generado")
        self.use_generated_btn.clicked.connect(self.use_generated_summary)
        self.use_generated_btn.setEnabled(False)
        editor_buttons.addWidget(self.use_generated_btn)
        
        self.preview_audio_btn = QPushButton("🎵 Preview Audio")
        self.preview_audio_btn.clicked.connect(self.generate_preview_audio)
        self.preview_audio_btn.setEnabled(False)
        editor_buttons.addWidget(self.preview_audio_btn)
        
        editor_buttons.addStretch()
        layout.addLayout(editor_buttons)
        
        widget.setLayout(layout)
        return widget
    
    def create_buttons(self) -> QHBoxLayout:
        """Crea los botones principales"""
        buttons_layout = QHBoxLayout()
        
        # Botón para regenerar análisis
        self.regenerate_btn = QPushButton("🔄 Regenerar Análisis")
        self.regenerate_btn.clicked.connect(self.start_analysis)
        buttons_layout.addWidget(self.regenerate_btn)
        
        buttons_layout.addStretch()
        
        # Botones estándar
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Guardar Resumen")
        self.save_btn.clicked.connect(self.save_summary)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("QPushButton { background-color: #0078d4; color: white; font-weight: bold; }")
        buttons_layout.addWidget(self.save_btn)
        
        return buttons_layout
    
    def start_analysis(self):
        """Inicia el análisis del contenido"""
        # Mostrar progress bar
        self.analysis_progress.setVisible(True)
        self.regenerate_btn.setEnabled(False)
        
        # Obtener contenido para analizar
        content = ""
        if self.content_item.content:
            content = self.content_item.content
        elif self.content_item.summary:
            content = self.content_item.summary
        elif self.content_item.description:
            content = self.content_item.description
        
        if not content:
            self.analysis_progress.setVisible(False)
            self.regenerate_btn.setEnabled(True)
            QMessageBox.warning(self, "Error", "No hay contenido para analizar")
            return
        
        # Iniciar análisis en hilo separado
        self.analysis_thread = ContentAnalysisThread(content, self.content_item.title)
        self.analysis_thread.analysis_finished.connect(self.on_analysis_finished)
        self.analysis_thread.start()
    
    def on_analysis_finished(self, analysis: Dict[str, Any]):
        """Se ejecuta cuando termina el análisis"""
        self.analysis_progress.setVisible(False)
        self.regenerate_btn.setEnabled(True)
        
        if not analysis:
            QMessageBox.warning(self, "Error", "No se pudo completar el análisis")
            return
        
        self.analysis_result = analysis
        self.update_analysis_display()
    
    def update_analysis_display(self):
        """Actualiza la pantalla con los resultados del análisis"""
        if not self.analysis_result:
            return
        
        # Actualizar resumen
        summary = self.analysis_result.get('summary', '')
        self.summary_text.setPlainText(summary)
        self.editable_summary.setPlainText(summary)
        
        # Actualizar estadísticas
        analysis = self.analysis_result.get('analysis', {})
        
        # Estadísticas del original
        orig_stats = f"""📊 Estadísticas del Original:
• {analysis.get('word_count', 0):,} palabras
• {analysis.get('sentence_count', 0)} oraciones
• {analysis.get('paragraph_count', 0)} párrafos
• ~{analysis.get('reading_time_minutes', 0):.1f} minutos de lectura
• Idioma detectado: {analysis.get('language', 'Desconocido').upper()}"""
        self.original_stats.setText(orig_stats)
        
        # Estadísticas del resumen
        summary_word_count = len(summary.split()) if summary else 0
        summary_reading_time = summary_word_count / 200
        
        summ_stats = f"""📝 Estadísticas del Resumen:
• {summary_word_count:,} palabras
• ~{summary_reading_time:.1f} minutos de lectura
• ~{summary_word_count / 150:.1f} minutos de audio"""
        self.summary_stats.setText(summ_stats)
        
        # Comparación
        if analysis.get('word_count', 0) > 0:
            compression = (summary_word_count / analysis.get('word_count', 1)) * 100
            words_saved = analysis.get('word_count', 0) - summary_word_count
            time_saved = analysis.get('reading_time_minutes', 0) - summary_reading_time
            
            comp_stats = f"""⚖️ Comparación:
• Compresión: {compression:.1f}% del original
• Palabras reducidas: {words_saved:,}
• Tiempo ahorrado: {time_saved:.1f} minutos"""
            self.comparison_stats.setText(comp_stats)
        
        # Frases clave
        key_phrases = analysis.get('key_phrases', [])
        if key_phrases:
            phrases_text = '\n• '.join([''] + key_phrases[:5])
            self.key_phrases_text.setText(phrases_text)
        else:
            self.key_phrases_text.setText("No se encontraron frases clave")
        
        # Habilitar botones
        self.use_generated_btn.setEnabled(True)
        self.preview_audio_btn.setEnabled(bool(summary))
        self.update_edited_info()
    
    def use_generated_summary(self):
        """Usa el resumen generado en el editor"""
        if self.analysis_result:
            summary = self.analysis_result.get('summary', '')
            self.editable_summary.setPlainText(summary)
    
    def on_summary_edited(self):
        """Se ejecuta cuando se edita el resumen"""
        self.update_edited_info()
        
        # Habilitar botón de guardar si hay cambios
        current_text = self.editable_summary.toPlainText()
        original_summary = self.content_item.summary or ""
        
        has_changes = current_text != original_summary
        self.save_btn.setEnabled(has_changes and bool(current_text.strip()))
        self.preview_audio_btn.setEnabled(bool(current_text.strip()))
    
    def update_edited_info(self):
        """Actualiza la información del resumen editado"""
        text = self.editable_summary.toPlainText()
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        estimated_minutes = word_count / 150 if word_count > 0 else 0
        
        info = f"📝 {char_count:,} caracteres • {word_count:,} palabras • ⏱️ ~{estimated_minutes:.1f} minutos de audio"
        self.edited_info_label.setText(info)
    
    def generate_preview_audio(self):
        """Genera preview del audio editado"""
        try:
            content = self.editable_summary.toPlainText().strip()
            if not content:
                QMessageBox.warning(self, "Error", "No hay contenido para generar audio")
                return
            
            # Tomar solo los primeros 500 caracteres para preview
            preview_content = content[:500]
            if len(content) > 500:
                preview_content += "... [Preview truncado]"
            
            self.preview_audio_btn.setEnabled(False)
            self.preview_audio_btn.setText("🎵 Generando...")
            
            # Generar audio de prueba
            audio_file = self.tts_service.text_to_speech(
                preview_content,
                f"analysis_preview_{self.content_item.id}",
                f"Preview Análisis - {self.content_item.display_title}"
            )
            
            QMessageBox.information(
                self, "Preview Generado",
                f"Preview de audio generado:\n{audio_file}\n\n"
                f"Reproduce el archivo para escuchar cómo sonará el resumen."
            )
            
        except Exception as e:
            logger.error(f"Error generando preview: {e}")
            QMessageBox.critical(self, "Error", f"Error generando preview:\n{str(e)}")
        finally:
            self.preview_audio_btn.setEnabled(True)
            self.preview_audio_btn.setText("🎵 Preview Audio")
    
    def save_summary(self):
        """Guarda el resumen editado"""
        try:
            new_summary = self.editable_summary.toPlainText().strip()
            
            if not new_summary:
                QMessageBox.warning(self, "Error", "El resumen no puede estar vacío")
                return
            
            # Actualizar en base de datos
            self.db_manager.update_content_item_files(self.content_item.id, summary=new_summary)
            
            # Preguntar si regenerar audio
            if self.content_item.has_audio:
                reply = QMessageBox.question(
                    self, "Regenerar Audio",
                    "¿Quieres regenerar el archivo de audio con el nuevo resumen?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        audio_file = self.tts_service.create_podcast_with_intro(
                            new_summary,
                            self.content_item.title,
                            self.content_item.source_name
                        )
                        
                        self.db_manager.update_content_item_files(self.content_item.id, audio_file=audio_file)
                        QMessageBox.information(self, "Éxito", "Resumen y audio actualizados")
                    except Exception as e:
                        QMessageBox.warning(self, "Advertencia", f"Resumen guardado, pero error en audio:\n{str(e)}")
            else:
                QMessageBox.information(self, "Éxito", "Resumen guardado exitosamente")
            
            self.content_updated.emit(self.content_item.id)
            self.accept()
            
        except Exception as e:
            logger.error(f"Error guardando resumen: {e}")
            QMessageBox.critical(self, "Error", f"Error guardando resumen:\n{str(e)}")
