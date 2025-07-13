"""
Diálogo de confirmación para eliminación de fuentes de datos
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTextEdit, QCheckBox, QGroupBox,
                              QScrollArea, QWidget, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from typing import Dict, Any

class DeleteConfirmationDialog(QDialog):
    """Diálogo de confirmación avanzada para eliminación de fuentes"""
    
    def __init__(self, deletion_info: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.deletion_info = deletion_info
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle("Confirmar Eliminación")
        self.setFixedSize(500, 600)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("⚠️ Confirmación de Eliminación")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #d32f2f; margin: 10px;")
        layout.addWidget(title_label)
        
        # Información de la fuente
        source_group = QGroupBox("Fuente de Datos")
        source_layout = QVBoxLayout()
        
        source_name = QLabel(f"📝 Nombre: {self.deletion_info['source_name']}")
        source_type = QLabel(f"🔗 Tipo: {self._get_type_display(self.deletion_info['source_type'])}")
        source_url = QLabel(f"🌐 URL: {self.deletion_info['source_url'][:60]}...")
        
        for label in [source_name, source_type, source_url]:
            label.setStyleSheet("margin: 5px; padding: 3px;")
        
        source_layout.addWidget(source_name)
        source_layout.addWidget(source_type)
        source_layout.addWidget(source_url)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # Estadísticas de eliminación
        stats_group = QGroupBox("Contenido que se Eliminará")
        stats_layout = QVBoxLayout()
        
        # Crear área de scroll para las estadísticas
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Items de contenido
        items_label = QLabel(f"📄 Items de contenido: {self.deletion_info['total_items']}")
        items_label.setStyleSheet("font-weight: bold; margin: 5px;")
        scroll_layout.addWidget(items_label)
        
        # Archivos de audio
        audio_count = self.deletion_info['audio_files_count']
        audio_label = QLabel(f"🎵 Archivos de audio: {audio_count}")
        audio_label.setStyleSheet("font-weight: bold; margin: 5px;")
        scroll_layout.addWidget(audio_label)
        
        if audio_count > 0:
            # Calcular tamaño total aproximado
            total_size = self._calculate_total_size()
            size_label = QLabel(f"💾 Espacio a liberar: ~{total_size}")
            size_label.setStyleSheet("color: #666; margin-left: 20px;")
            scroll_layout.addWidget(size_label)
        
        # Logs de procesamiento
        logs_label = QLabel(f"📊 Registros de procesamiento: {self.deletion_info['processing_logs']}")
        logs_label.setStyleSheet("font-weight: bold; margin: 5px;")
        scroll_layout.addWidget(logs_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        scroll_layout.addWidget(separator)
        
        # Lista de archivos de audio (si hay muchos, mostrar solo algunos)
        if self.deletion_info['audio_file_paths']:
            files_label = QLabel("Archivos de audio a eliminar:")
            files_label.setStyleSheet("font-weight: bold; margin: 10px 5px 5px 5px;")
            scroll_layout.addWidget(files_label)
            
            files_to_show = self.deletion_info['audio_file_paths'][:10]  # Mostrar máximo 10
            for file_path in files_to_show:
                file_label = QLabel(f"• {file_path}")
                file_label.setStyleSheet("color: #666; margin-left: 20px; font-family: monospace;")
                file_label.setWordWrap(True)
                scroll_layout.addWidget(file_label)
            
            if len(self.deletion_info['audio_file_paths']) > 10:
                more_label = QLabel(f"... y {len(self.deletion_info['audio_file_paths']) - 10} archivos más")
                more_label.setStyleSheet("color: #999; margin-left: 20px; font-style: italic;")
                scroll_layout.addWidget(more_label)
        
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(250)
        
        stats_layout.addWidget(scroll_area)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Checkbox de confirmación
        self.confirm_checkbox = QCheckBox("Entiendo que esta acción no se puede deshacer")
        self.confirm_checkbox.setStyleSheet("font-weight: bold; margin: 10px;")
        self.confirm_checkbox.stateChanged.connect(self._on_checkbox_changed)
        layout.addWidget(self.confirm_checkbox)
        
        # Advertencia
        warning_label = QLabel("⚠️ Esta acción eliminará permanentemente todos los datos asociados a esta fuente.")
        warning_label.setStyleSheet("color: #d32f2f; font-weight: bold; margin: 10px; padding: 10px; border: 1px solid #d32f2f; border-radius: 4px; background-color: #ffebee;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("padding: 8px 20px;")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        buttons_layout.addStretch()
        
        self.delete_button = QPushButton("Eliminar Todo")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.delete_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def _get_type_display(self, source_type: str) -> str:
        """Convierte el tipo de fuente a texto legible"""
        type_mapping = {
            'youtube': 'Canal de YouTube',
            'rss': 'Feed RSS',
            'web': 'Página Web'
        }
        return type_mapping.get(source_type, source_type)
    
    def _calculate_total_size(self) -> str:
        """Calcula el tamaño total aproximado de los archivos"""
        # Esto es una estimación ya que no tenemos acceso directo a los tamaños
        # En una implementación más completa, se podría calcular el tamaño real
        audio_count = self.deletion_info['audio_files_count']
        
        if audio_count == 0:
            return "0 MB"
        elif audio_count <= 5:
            return f"{audio_count * 2}-{audio_count * 5} MB"
        elif audio_count <= 20:
            return f"{audio_count * 2}-{audio_count * 8} MB"
        else:
            return f"{audio_count * 2}-{audio_count * 10} MB"
    
    def _on_checkbox_changed(self, state):
        """Maneja el cambio del checkbox de confirmación"""
        # state es un int: 0 = unchecked, 2 = checked
        enabled = (state == 2)
        self.delete_button.setEnabled(enabled)
