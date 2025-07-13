#!/usr/bin/env python3
"""
Prueba completa del reproductor embebido de la aplicación
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import QTimer
from app.widgets.audio_player_widget import AudioPlayerWidget
from services.text_to_speech import TextToSpeechService

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba del Reproductor Embebido")
        self.setGeometry(100, 100, 600, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Etiqueta
        self.status_label = QLabel("Iniciando prueba del reproductor embebido...")
        layout.addWidget(self.status_label)
        
        # Botón para generar y probar audio
        self.test_button = QPushButton("Generar y Probar Audio")
        self.test_button.clicked.connect(self.test_audio)
        layout.addWidget(self.test_button)
        
        # Widget del reproductor
        self.audio_player_widget = AudioPlayerWidget()
        layout.addWidget(self.audio_player_widget)
        
        # TTS service
        self.tts = TextToSpeechService()
        
        # Timer para actualizar estado
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(500)  # Cada 500ms
    
    def test_audio(self):
        """Genera audio y lo carga en el reproductor"""
        try:
            self.status_label.setText("🎤 Generando audio con TTS...")
            self.test_button.setEnabled(False)
            
            # Generar audio
            test_text = """
            Hola, bienvenido a la prueba del reproductor embebido de PyPodcast.
            Este es un texto de prueba para verificar que el audio se genera correctamente
            en formato WAV y se puede reproducir desde la interfaz de usuario.
            La síntesis de voz está funcionando a una velocidad natural de 150 palabras por minuto.
            """
            
            audio_file = self.tts.text_to_speech(
                test_text, 
                "test_embebido", 
                "Prueba del Reproductor Embebido"
            )
            
            self.status_label.setText(f"✅ Audio generado: {Path(audio_file).name}")
            
            # Cargar en el reproductor
            success = self.audio_player_widget.load_audio(audio_file)
            if success:
                self.status_label.setText("✅ Audio cargado en el reproductor - ¡Prueba los controles!")
            else:
                self.status_label.setText("❌ Error cargando audio en el reproductor")
                
        except Exception as e:
            self.status_label.setText(f"❌ Error: {e}")
            
        finally:
            self.test_button.setEnabled(True)
    
    def update_status(self):
        """Actualiza el estado del reproductor"""
        if hasattr(self.audio_player_widget, 'audio_player') and self.audio_player_widget.audio_player:
            player = self.audio_player_widget.audio_player
            if player.is_playing_file():
                position = player.get_position()
                duration = player.get_duration()
                self.status_label.setText(f"▶️ Reproduciendo: {position:.1f}s / {duration:.1f}s")

def main():
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    print("=== INSTRUCCIONES ===")
    print("1. Haz clic en 'Generar y Probar Audio'")
    print("2. Espera a que se genere el archivo WAV")
    print("3. Usa los controles del reproductor para probar:")
    print("   - ▶️ Play/Pause")
    print("   - ⏹️ Stop")
    print("   - 🔊 Volume")
    print("4. Verifica que el audio se escucha correctamente")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
