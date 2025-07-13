#!/usr/bin/env python3
"""
Prueba rápida de TTS con velocidad ajustada y conversión a M4A
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.text_to_speech import TextToSpeechService
from utils.logger import setup_logger

def quick_tts_test():
    """Prueba rápida de TTS mejorado"""
    
    print("🎤 Prueba Rápida: TTS con Velocidad Ajustada")
    print("=" * 50)
    
    try:
        # Inicializar TTS
        tts = TextToSpeechService()
        
        print(f"📊 Configuración:")
        print(f"   Voz: {tts.voice}")
        print(f"   Velocidad: {tts.rate} wpm (antes: 200 wpm)")
        
        # Texto de prueba simple
        test_text = """
        Hola, esta es una prueba de PyPodcast con velocidad mejorada.
        Ahora el texto se reproduce a ciento cincuenta palabras por minuto,
        lo que debería sonar mucho más natural y fácil de entender.
        El archivo se generará en formato M4A que es compatible con la mayoría de reproductores.
        """
        
        print(f"\n🎵 Generando audio de prueba...")
        
        # Generar audio
        audio_file = tts.text_to_speech(test_text, "prueba_velocidad_mejorada")
        
        print(f"✅ Audio generado: {audio_file}")
        
        # Verificar archivo
        if os.path.exists(audio_file):
            size = os.path.getsize(audio_file)
            extension = audio_file.split('.')[-1].lower()
            print(f"   Tamaño: {size:,} bytes")
            print(f"   Formato: {extension.upper()}")
            
            if extension in ['m4a', 'mp3']:
                print(f"   ✅ Formato comprimido correcto")
            elif extension == 'aiff':
                print(f"   ⚠️  Formato sin comprimir (conversión falló)")
                
        else:
            print(f"   ❌ Archivo no encontrado")
            return False
            
        # Probar velocidades diferentes
        print(f"\n🐌 Probando velocidad más lenta (120 wpm)...")
        tts.set_speech_rate(120)
        
        slow_file = tts.text_to_speech(
            "Esta es una prueba con velocidad muy lenta para comparar.", 
            "prueba_lenta"
        )
        print(f"   ✅ Audio lento: {slow_file}")
        
        print(f"\n⚡ Probando velocidad más rápida (180 wpm)...")
        tts.set_speech_rate(180)
        
        fast_file = tts.text_to_speech(
            "Esta es una prueba con velocidad más rápida.", 
            "prueba_rapida"
        )
        print(f"   ✅ Audio rápido: {fast_file}")
        
        # Restaurar velocidad original
        tts.set_speech_rate(150)
        
        print(f"\n🎉 Prueba completada exitosamente!")
        print(f"📁 Revisa la carpeta 'podcasts' para escuchar los archivos generados.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

if __name__ == "__main__":
    success = quick_tts_test()
    if not success:
        sys.exit(1)
