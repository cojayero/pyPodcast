#!/usr/bin/env python3
"""
Script de prueba para URLs de YouTube
"""

import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from services.rss_manager import RSSManager
from utils.logger import setup_logger

def test_youtube_urls():
    """Prueba diferentes formatos de URLs de YouTube"""
    
    logger = setup_logger()
    rss_manager = RSSManager()
    
    # URLs de prueba (ejemplos comunes)
    test_urls = [
        # Formato channel ID directo
        "https://www.youtube.com/channel/UC-lHJZR3Gqxm24_Vd_AJ5Yw",  # PewDiePie
        
        # Formato handle nuevo (@)
        "https://www.youtube.com/@youtube",  # Canal oficial de YouTube
        "https://www.youtube.com/@TEDTalks",  # TED Talks
        
        # Formato username
        "https://www.youtube.com/user/TEDtalksDirector",  # TED (formato antiguo)
        
        # Formato personalizado /c/
        "https://www.youtube.com/c/YouTube",  # YouTube oficial
        
        # URL simple
        "https://www.youtube.com/TEDTalks",
    ]
    
    print("🔍 Probando URLs de YouTube...")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Probando: {url}")
        try:
            rss_url = rss_manager.get_youtube_rss_url(url)
            print(f"   ✅ RSS URL: {rss_url}")
            
            # Validar que el feed funciona
            if rss_manager.validate_feed_url(rss_url):
                print(f"   ✅ Feed válido y accesible")
                
                # Intentar parsear el feed
                try:
                    feed_data = rss_manager.parse_feed(rss_url)
                    print(f"   ✅ Canal: {feed_data['channel']['title']}")
                    print(f"   ✅ Videos: {feed_data['total_entries']}")
                except Exception as e:
                    print(f"   ⚠️ Error parseando feed: {e}")
            else:
                print(f"   ❌ Feed no válido o inaccesible")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Prueba completada")

def test_specific_url():
    """Prueba una URL específica con debug detallado"""
    
    # Cambiar esta URL por la que tengas problemas
    test_url = "https://www.youtube.com/@TEDTalks"
    
    print(f"🔍 Prueba detallada para: {test_url}")
    print("=" * 50)
    
    logger = setup_logger()
    rss_manager = RSSManager()
    
    try:
        print("1. Obteniendo URL de RSS...")
        rss_url = rss_manager.get_youtube_rss_url(test_url)
        print(f"   RSS URL generada: {rss_url}")
        
        print("\n2. Validando feed...")
        is_valid = rss_manager.validate_feed_url(rss_url)
        print(f"   ¿Es válido?: {is_valid}")
        
        if is_valid:
            print("\n3. Parseando feed...")
            feed_data = rss_manager.parse_feed(rss_url)
            
            print(f"   Título del canal: {feed_data['channel']['title']}")
            print(f"   Descripción: {feed_data['channel']['description'][:100]}...")
            print(f"   Total de entradas: {feed_data['total_entries']}")
            
            if feed_data['entries']:
                print(f"\n   Último video: {feed_data['entries'][0]['title']}")
                print(f"   URL: {feed_data['entries'][0]['url']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--specific":
        test_specific_url()
    else:
        test_youtube_urls()
