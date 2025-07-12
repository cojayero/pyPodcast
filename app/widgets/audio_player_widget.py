"""
Widget del reproductor de audio
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QSlider, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon, QFont
from pathlib import Path
from typing import Optional

from services.audio_player import AudioPlayer
from utils.logger import get_logger

logger = get_logger(__name__)

class AudioPlayerWidget(QWidget):
    """Widget del reproductor de audio integrado"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_player = AudioPlayer()
        self.current_file = None
        self.current_title = "Sin contenido"
        self.setup_ui()
        self.setup_audio_callbacks()
        self.setup_timer()
    
    def setup_ui(self):
        """Configura la interfaz del reproductor"""
        layout = QVBoxLayout()
        
        # Frame del reproductor
        player_frame = QFrame()
        player_frame.setFrameStyle(QFrame.StyledPanel)
        player_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        player_layout = QVBoxLayout()
        
        # Información de la pista
        info_layout = QVBoxLayout()
        
        self.title_label = QLabel(self.current_title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.title_label)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #666; font-size: 12px;")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.time_label)
        
        player_layout.addLayout(info_layout)
        
        # Barra de progreso
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border: 1px solid #777;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #5c5c5c;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)
        player_layout.addWidget(self.progress_slider)
        
        # Controles de reproducción
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Botón anterior (placeholder)
        self.prev_button = QPushButton("⏮")
        self.prev_button.setEnabled(False)
        self.prev_button.setFixedSize(40, 40)
        self.prev_button.setStyleSheet(self._get_button_style())
        controls_layout.addWidget(self.prev_button)
        
        # Botón play/pause
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(50, 50)
        self.play_button.setStyleSheet(self._get_play_button_style())
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        # Botón siguiente (placeholder)
        self.next_button = QPushButton("⏭")
        self.next_button.setEnabled(False)
        self.next_button.setFixedSize(40, 40)
        self.next_button.setStyleSheet(self._get_button_style())
        controls_layout.addWidget(self.next_button)
        
        controls_layout.addStretch()
        
        # Control de volumen
        volume_layout = QHBoxLayout()
        
        volume_label = QLabel("🔊")
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d4;
                border: 1px solid #777;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #5c5c5c;
                width: 12px;
                margin: -3px 0;
                border-radius: 6px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)
        
        controls_layout.addLayout(volume_layout)
        
        # Botón stop
        self.stop_button = QPushButton("⏹")
        self.stop_button.setFixedSize(40, 40)
        self.stop_button.setStyleSheet(self._get_button_style())
        self.stop_button.clicked.connect(self.stop_playback)
        controls_layout.addWidget(self.stop_button)
        
        player_layout.addLayout(controls_layout)
        
        player_frame.setLayout(player_layout)
        layout.addWidget(player_frame)
        
        self.setLayout(layout)
        
        # Estado inicial
        self.update_ui_state()
    
    def _get_button_style(self) -> str:
        """Estilo para botones normales"""
        return """
            QPushButton {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e6f3ff;
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background-color: #cce7ff;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                color: #ccc;
                border-color: #eee;
            }
        """
    
    def _get_play_button_style(self) -> str:
        """Estilo para botón play/pause"""
        return """
            QPushButton {
                background-color: #0078d4;
                border: 2px solid #0078d4;
                border-radius: 25px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
                border-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
                border-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #ccc;
                border-color: #ccc;
            }
        """
    
    def setup_audio_callbacks(self):
        """Configura callbacks del reproductor de audio"""
        self.audio_player.on_position_changed = self.on_position_changed
        self.audio_player.on_playback_finished = self.on_playback_finished
        self.audio_player.on_playback_started = self.on_playback_started
        self.audio_player.on_playback_paused = self.on_playback_paused
    
    def setup_timer(self):
        """Configura timer para actualizar UI"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_progress)
        self.update_timer.setInterval(100)  # Actualizar cada 100ms
    
    def load_audio_file(self, file_path: str, title: str = None) -> bool:
        """Carga un archivo de audio"""
        try:
            if not Path(file_path).exists():
                logger.error(f"Archivo no encontrado: {file_path}")
                return False
            
            if self.audio_player.load_file(file_path):
                self.current_file = file_path
                self.current_title = title or Path(file_path).stem
                self.title_label.setText(self.current_title)
                self.update_ui_state()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cargando archivo de audio: {e}")
            return False
    
    def toggle_playback(self):
        """Alterna entre play y pause"""
        if not self.current_file:
            return
        
        if self.audio_player.is_playing_file():
            self.pause_playback()
        else:
            self.play_audio()
    
    def play_audio(self):
        """Inicia la reproducción"""
        if self.current_file and self.audio_player.play():
            self.update_timer.start()
            self.update_ui_state()
    
    def pause_playback(self):
        """Pausa la reproducción"""
        if self.audio_player.pause():
            self.update_timer.stop()
            self.update_ui_state()
    
    def stop_playback(self):
        """Detiene la reproducción"""
        if self.audio_player.stop():
            self.update_timer.stop()
            self.progress_slider.setValue(0)
            self.update_ui_state()
    
    def on_volume_changed(self, value: int):
        """Maneja cambios en el volumen"""
        volume = value / 100.0
        self.audio_player.set_volume(volume)
    
    def on_slider_pressed(self):
        """Maneja cuando se presiona el slider de progreso"""
        self.update_timer.stop()
    
    def on_slider_released(self):
        """Maneja cuando se suelta el slider de progreso"""
        if self.audio_player.get_duration() > 0:
            position = (self.progress_slider.value() / 100.0) * self.audio_player.get_duration()
            self.audio_player.seek(position)
        
        if self.audio_player.is_playing_file():
            self.update_timer.start()
    
    def update_progress(self):
        """Actualiza la barra de progreso"""
        if not self.current_file:
            return
        
        position = self.audio_player.get_position()
        duration = self.audio_player.get_duration()
        
        if duration > 0:
            progress = int((position / duration) * 100)
            self.progress_slider.setValue(progress)
        
        # Actualizar tiempo
        pos_str = self.format_time(position)
        dur_str = self.format_time(duration)
        self.time_label.setText(f"{pos_str} / {dur_str}")
    
    def format_time(self, seconds: float) -> str:
        """Formatea tiempo en MM:SS"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_ui_state(self):
        """Actualiza el estado de la interfaz"""
        has_file = bool(self.current_file)
        is_playing = self.audio_player.is_playing_file()
        
        # Botón play/pause
        if is_playing:
            self.play_button.setText("⏸")
        else:
            self.play_button.setText("▶")
        
        self.play_button.setEnabled(has_file)
        self.stop_button.setEnabled(has_file)
        self.progress_slider.setEnabled(has_file)
        
        if not has_file:
            self.title_label.setText("Sin contenido")
            self.time_label.setText("00:00 / 00:00")
            self.progress_slider.setValue(0)
    
    def on_position_changed(self, position: float):
        """Callback cuando cambia la posición"""
        # Se actualiza en update_progress()
        pass
    
    def on_playback_finished(self):
        """Callback cuando termina la reproducción"""
        self.update_timer.stop()
        self.progress_slider.setValue(100)
        self.update_ui_state()
    
    def on_playback_started(self):
        """Callback cuando inicia la reproducción"""
        self.update_ui_state()
    
    def on_playback_paused(self):
        """Callback cuando se pausa la reproducción"""
        self.update_ui_state()
    
    def cleanup(self):
        """Limpia recursos"""
        self.update_timer.stop()
        if self.audio_player:
            self.audio_player.cleanup()
