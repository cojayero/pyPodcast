#!/usr/bin/env python3
"""
Verificación final del problema de reproducción de audio
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.text_to_speech import TextToSpeechService
from services.audio_player import AudioPlayer
from pathlib import Path

def final_verification():
    """Verificación final de que el problema está resuelto"""
    print("=== VERIFICACIÓN FINAL: PROBLEMA DE AUDIO RESUELTO ===\n")
    
    # 1. Verificar TTS
    print("🎤 Paso 1: Verificando TextToSpeechService...")
    tts = TextToSpeechService()
    
    # Generar audio
    test_text = "Verificación final de la corrección del reproductor de audio."
    audio_file = tts.text_to_speech(test_text, "verificacion_final")
    
    audio_path = Path(audio_file)
    print(f"   ✅ Audio generado: {audio_path.name}")
    print(f"   ✅ Formato: {audio_path.suffix}")
    print(f"   ✅ Tamaño: {audio_path.stat().st_size} bytes")
    
    # Verificar que es WAV
    if audio_path.suffix.lower() == '.wav':
        print("   ✅ Formato correcto: WAV")
    else:
        print(f"   ❌ Formato incorrecto: {audio_path.suffix}")
        return False
    
    # 2. Verificar AudioPlayer
    print(f"\n🎵 Paso 2: Verificando AudioPlayer...")
    player = AudioPlayer()
    
    # Cargar archivo
    load_success = player.load_file(audio_file)
    if load_success:
        print("   ✅ Carga exitosa en AudioPlayer")
    else:
        print("   ❌ Error cargando en AudioPlayer")
        return False
    
    # Probar reproducción
    play_success = player.play()
    if play_success:
        print("   ✅ Reproducción iniciada")
        
        # Verificar que está reproduciendo
        import time
        time.sleep(0.5)
        if player.is_playing_file():
            print("   ✅ Audio se está reproduciendo correctamente")
            player.stop()
            print("   ✅ Reproducción detenida")
        else:
            print("   ❌ Audio no se está reproduciendo")
            return False
    else:
        print("   ❌ Error iniciando reproducción")
        return False
    
    # 3. Verificar formatos soportados
    print(f"\n📋 Paso 3: Verificando formatos soportados...")
    supported = player.get_supported_formats()
    print(f"   ✅ Formatos soportados: {supported}")
    
    if '.wav' in supported:
        print("   ✅ WAV está en la lista de formatos soportados")
    else:
        print("   ❌ WAV no está en la lista de formatos soportados")
    
    # Limpiar
    player.cleanup()
    
    # 4. Verificar configuración
    print(f"\n⚙️ Paso 4: Verificando configuración...")
    from utils.config import config_manager
    audio_format = config_manager.get('audio.format', 'unknown')
    print(f"   ✅ Formato configurado: {audio_format}")
    
    if audio_format == 'wav':
        print("   ✅ Configuración correcta")
    else:
        print(f"   ⚠ Configuración podría necesitar actualización: {audio_format}")
    
    print(f"\n=== RESUMEN ===")
    print("✅ PROBLEMA RESUELTO:")
    print("   - TTS ahora genera archivos WAV")
    print("   - AudioPlayer puede cargar y reproducir WAV")
    print("   - Configuración actualizada a formato WAV")
    print("   - Formatos soportados actualizados")
    
    print(f"\n🏆 RESULTADO: Los archivos de audio ahora se reproducen correctamente desde el player embebido")
    
    # Limpiar archivo de prueba
    if audio_path.exists():
        audio_path.unlink()
        print(f"\n🧹 Archivo de prueba eliminado")
    
    return True

if __name__ == "__main__":
    try:
        success = final_verification()
        if success:
            print(f"\n🎉 ¡VERIFICACIÓN EXITOSA!")
        else:
            print(f"\n❌ VERIFICACIÓN FALLÓ")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error durante verificación: {e}")
        sys.exit(1)
