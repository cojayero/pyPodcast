#!/usr/bin/env python3
"""
Script para probar la reproducción actual de la aplicación
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.text_to_speech import TextToSpeechService
from services.audio_player import AudioPlayer
import time

def test_current_app_audio():
    """Prueba el flujo actual de TTS -> AudioPlayer"""
    print("=== PRUEBA DEL FLUJO ACTUAL TTS -> AUDIO PLAYER ===\n")
    
    # Inicializar servicios
    tts = TextToSpeechService()
    player = AudioPlayer()
    
    # Generar audio con TTS
    test_text = "Hola, esto es una prueba del reproductor de audio embebido."
    
    print("🎤 Generando audio con TTS...")
    try:
        audio_file = tts.text_to_speech(test_text, "test_reproduction", "Prueba de reproducción")
        print(f"✓ Audio generado: {audio_file}")
        
        # Verificar que el archivo existe y su extensión
        from pathlib import Path
        audio_path = Path(audio_file)
        if audio_path.exists():
            print(f"✓ Archivo existe: {audio_path}")
            print(f"📁 Tamaño: {audio_path.stat().st_size} bytes")
            print(f"🎵 Extensión: {audio_path.suffix}")
        else:
            print(f"✗ Archivo no existe: {audio_path}")
            return
        
    except Exception as e:
        print(f"✗ Error generando audio: {e}")
        return
    
    # Intentar cargar en el reproductor
    print(f"\n🎵 Intentando cargar en AudioPlayer...")
    try:
        success = player.load_file(audio_file)
        if success:
            print("✓ Archivo cargado exitosamente")
            
            # Intentar reproducir
            print("▶️  Intentando reproducir...")
            play_success = player.play()
            if play_success:
                print("✓ Reproducción iniciada")
                
                # Esperar un poco y verificar estado
                time.sleep(1)
                if player.is_playing_file():
                    print("✓ Audio se está reproduciendo correctamente")
                    
                    # Dejar reproducir por 3 segundos
                    time.sleep(3)
                    player.stop()
                    print("⏹️  Reproducción detenida")
                else:
                    print("✗ Audio no se está reproduciendo (pygame get_busy = False)")
            else:
                print("✗ Error iniciando reproducción")
        else:
            print("✗ Error cargando archivo en AudioPlayer")
            
    except Exception as e:
        print(f"✗ Error en AudioPlayer: {e}")
    
    # Limpiar
    player.cleanup()
    
    print(f"\n=== DIAGNÓSTICO ===")
    print(f"El problema está en que TTS genera archivos {Path(audio_file).suffix}")
    print(f"pero pygame solo reproduce WAV correctamente.")
    print(f"\n💡 SOLUCIÓN NECESARIA:")
    print(f"Modificar TextToSpeechService para generar WAV en lugar de M4A/AIFF")

if __name__ == "__main__":
    test_current_app_audio()
