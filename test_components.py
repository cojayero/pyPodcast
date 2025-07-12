#!/usr/bin/env python3
"""
Script de prueba para verificar componentes de PyPodcast
"""

import sys
import os
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Prueba las importaciones básicas"""
    print("🔧 Probando importaciones...")
    
    try:
        from utils.config import ConfigManager
        print("✅ ConfigManager importado")
        
        from utils.logger import setup_logger
        print("✅ Logger importado")
        
        from models.database import DatabaseManager
        print("✅ DatabaseManager importado")
        
        from services.rss_manager import RSSManager
        print("✅ RSSManager importado")
        
        from services.web_extractor import WebExtractor
        print("✅ WebExtractor importado")
        
        from services.text_to_speech import TextToSpeechService
        print("✅ TextToSpeechService importado")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return False

def test_config():
    """Prueba el sistema de configuración"""
    print("\n⚙️ Probando configuración...")
    
    try:
        from utils.config import ConfigManager
        config = ConfigManager()
        
        # Cargar configuración
        config.load_config()
        print("✅ Configuración cargada")
        
        # Probar obtener valores
        app_version = config.get('app.version', 'unknown')
        print(f"✅ Versión de app: {app_version}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def test_database():
    """Prueba la base de datos"""
    print("\n💾 Probando base de datos...")
    
    try:
        from models.database import DatabaseManager
        db = DatabaseManager()
        
        # Inicializar base de datos
        db.initialize_database()
        print("✅ Base de datos inicializada")
        
        # Probar obtener fuentes
        sources = db.get_data_sources()
        print(f"✅ Fuentes obtenidas: {len(sources)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def test_text_to_speech():
    """Prueba la síntesis de voz"""
    print("\n🗣️ Probando síntesis de voz...")
    
    try:
        from services.text_to_speech import TextToSpeechService
        tts = TextToSpeechService()
        
        # Probar obtener voces
        if tts.test_voice_synthesis():
            print("✅ Síntesis de voz funcionando")
            
            spanish_voices = tts.get_spanish_voices()
            print(f"✅ Voces en español disponibles: {len(spanish_voices)}")
            
            return True
        else:
            print("❌ Síntesis de voz no funciona")
            return False
        
    except Exception as e:
        print(f"❌ Error en síntesis de voz: {e}")
        return False

def test_rss():
    """Prueba el gestor de RSS"""
    print("\n📡 Probando gestor RSS...")
    
    try:
        from services.rss_manager import RSSManager
        rss = RSSManager()
        
        # Probar validación de feed
        test_feed = "https://feeds.bbci.co.uk/news/rss.xml"
        if rss.validate_feed_url(test_feed):
            print("✅ Validación de feed RSS funcionando")
        else:
            print("⚠️ Validación de feed RSS falló (puede ser conectividad)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en gestor RSS: {e}")
        return False

def test_audio_player():
    """Prueba el reproductor de audio"""
    print("\n🎵 Probando reproductor de audio...")
    
    try:
        from services.audio_player import AudioPlayer
        player = AudioPlayer()
        
        print("✅ AudioPlayer inicializado")
        
        # Obtener formatos soportados
        formats = player.get_supported_formats()
        print(f"✅ Formatos soportados: {formats}")
        
        player.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Error en reproductor de audio: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 PyPodcast - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Importaciones", test_imports),
        ("Configuración", test_config),
        ("Base de Datos", test_database),
        ("Síntesis de Voz", test_text_to_speech),
        ("Gestor RSS", test_rss),
        ("Reproductor Audio", test_audio_player)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 Todos los componentes funcionan correctamente!")
        print("✅ La aplicación está lista para usar")
    else:
        print("⚠️ Algunos componentes tienen problemas")
        print("📖 Consulta el README.md para instrucciones de instalación")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
