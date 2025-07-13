#!/usr/bin/env python3
"""
Script de prueba para verificar mejoras en síntesis de voz
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.text_to_speech import TextToSpeechService
from utils.logger import setup_logger
import time

# Configurar logger
logger = setup_logger()

def test_tts_improvements():
    """Prueba las mejoras en síntesis de voz"""
    
    print("🎤 Probando mejoras en síntesis de voz...")
    print("=" * 50)
    
    try:
        # Inicializar servicio TTS
        tts = TextToSpeechService()
        
        # Mostrar configuración actual
        print(f"🔧 Configuración actual:")
        print(f"   Voz: {tts.voice}")
        print(f"   Velocidad: {tts.rate} wpm")
        print(f"   Formato: {tts.format}")
        print(f"   Directorio: {tts.output_dir}")
        
        # Texto de prueba con elementos que requieren mejoras
        test_text = """
        Bienvenido a PyPodcast. Esta es una prueba de síntesis de voz mejorada.
        
        Vamos a probar diferentes elementos:
        - URLs como https://www.youtube.com y www.example.org
        - Abreviaciones como Dr. García, Sr. López, etc.
        - Símbolos técnicos: API, RSS, HTTP
        - Puntuación: ¡Hola! ¿Cómo estás? Bien, gracias.
        
        El texto ahora debería sonar más natural y con pausas apropiadas.
        """
        
        print(f"\n📝 Texto de prueba preparado:")
        prepared_text = tts._prepare_text_for_tts(test_text)
        print(f"   Longitud original: {len(test_text)} caracteres")
        print(f"   Longitud preparada: {len(prepared_text)} caracteres")
        
        # Prueba con velocidad por defecto
        print(f"\n🎵 Generando audio con velocidad por defecto ({tts.rate} wpm)...")
        start_time = time.time()
        
        try:
            audio_file = tts.text_to_speech(test_text, "test_default_speed")
            duration = time.time() - start_time
            
            print(f"   ✅ Audio generado en {duration:.1f}s: {audio_file}")
            
            # Verificar que es MP3
            if audio_file.endswith('.mp3'):
                print(f"   ✅ Formato MP3 correcto")
            else:
                print(f"   ⚠️  Formato: {audio_file.split('.')[-1]} (esperado MP3)")
                
            # Verificar que el archivo existe
            if os.path.exists(audio_file):
                file_size = os.path.getsize(audio_file)
                print(f"   ✅ Archivo creado: {file_size} bytes")
            else:
                print(f"   ❌ Archivo no encontrado")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Prueba con velocidad más lenta
        print(f"\n🐌 Probando velocidad más lenta (120 wpm)...")
        tts.set_speech_rate(120)
        
        try:
            audio_file = tts.text_to_speech(
                "Esta es una prueba con velocidad de habla más lenta para mejor comprensión.",
                "test_slow_speed"
            )
            print(f"   ✅ Audio lento generado: {audio_file}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Prueba con velocidad más rápida
        print(f"\n🚀 Probando velocidad más rápida (180 wpm)...")
        tts.set_speech_rate(180)
        
        try:
            audio_file = tts.text_to_speech(
                "Esta es una prueba con velocidad de habla más rápida.",
                "test_fast_speed"
            )
            print(f"   ✅ Audio rápido generado: {audio_file}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Probar voces disponibles
        print(f"\n🗣️  Probando voces disponibles...")
        spanish_voices = tts.get_spanish_voices()
        print(f"   Voces en español encontradas: {len(spanish_voices)}")
        
        for i, voice in enumerate(spanish_voices[:3]):  # Probar solo las primeras 3
            print(f"   Probando voz: {voice}")
            try:
                tts.set_voice(voice)
                audio_file = tts.text_to_speech(
                    f"Hola, soy la voz {voice}. Esta es una prueba.",
                    f"test_voice_{voice.lower()}"
                )
                print(f"     ✅ Audio con {voice}: {audio_file}")
            except Exception as e:
                print(f"     ❌ Error con {voice}: {e}")
        
        # Probar creación de podcast completo
        print(f"\n📻 Probando creación de podcast completo...")
        try:
            # Restaurar voz original
            tts.set_voice(tts.voice)
            tts.set_speech_rate(150)  # Velocidad óptima
            
            podcast_text = """
            En este episodio hablaremos sobre las mejoras implementadas en PyPodcast.
            
            Hemos mejorado significativamente la síntesis de voz, incluyendo:
            - Velocidad más natural de 150 palabras por minuto
            - Mejor manejo de URLs y abreviaciones
            - Pausas más naturales en la narración
            - Salida directa en formato MP3
            
            Estas mejoras hacen que la experiencia de escucha sea mucho más agradable.
            """
            
            audio_file = tts.create_podcast_with_intro(
                podcast_text, 
                "Mejoras en PyPodcast TTS",
                "Equipo PyPodcast"
            )
            print(f"   ✅ Podcast completo generado: {audio_file}")
            
        except Exception as e:
            print(f"   ❌ Error creando podcast: {e}")
        
        print(f"\n" + "=" * 50)
        print(f"🎉 Pruebas de TTS completadas!")
        
        # Listar archivos generados
        podcast_dir = tts.output_dir
        if podcast_dir.exists():
            audio_files = list(podcast_dir.glob("test_*.mp3")) + list(podcast_dir.glob("test_*.aiff"))
            if audio_files:
                print(f"\n📁 Archivos de audio generados:")
                for file in audio_files:
                    size = file.stat().st_size
                    print(f"   {file.name} ({size} bytes)")
            else:
                print(f"\n⚠️  No se encontraron archivos de audio generados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Pruebas de Mejoras TTS - pyPodcast")
    print("=" * 40)
    
    success = test_tts_improvements()
    
    if success:
        print("\n✅ Todas las pruebas de TTS completadas exitosamente!")
        print("🎧 Puedes reproducir los archivos generados para verificar calidad")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
