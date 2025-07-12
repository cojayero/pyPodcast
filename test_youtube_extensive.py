#!/usr/bin/env python3
"""
Prueba extensa de URLs de YouTube para validar la robustez del sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.rss_manager import RSSManager
from utils.logger import setup_logger
import requests

# Configurar logger
logger = setup_logger()

def test_extensive_youtube_urls():
    """Prueba extensa de URLs de YouTube"""
    
    # URLs de diferentes tipos y casos problemáticos
    test_urls = [
        # URLs problemáticas reportadas originalmente
        "https://www.youtube.com/TEDTalks",
        "https://www.youtube.com/c/TEDTalks",
        "https://www.youtube.com/c/MrBeast6000",
        
        # URLs con diferentes formatos
        "https://www.youtube.com/@TEDTalks",
        "https://www.youtube.com/@MrBeast", 
        "https://www.youtube.com/@mkbhd",
        "https://www.youtube.com/@pewdiepie",
        
        # URLs tradicionales
        "https://www.youtube.com/user/TEDtalksDirector",
        "https://www.youtube.com/user/marquesbrownlee",
        "https://www.youtube.com/user/PewDiePie",
        
        # URLs con channel ID
        "https://www.youtube.com/channel/UCAuUUnT6oDeKwE6v1NGQxug",  # TED
        "https://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA",  # MrBeast
        "https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ",  # MKBHD
        
        # URLs con /c/ (discontinuadas)
        "https://www.youtube.com/c/mkbhd",
        "https://www.youtube.com/c/pewdiepie",
        
        # URLs sin formato específico (casos complicados)
        "https://www.youtube.com/google",
        "https://www.youtube.com/youtube",
        "https://www.youtube.com/music",
        
        # URLs con variaciones
        "https://youtube.com/@MrBeast",  # Sin www
        "https://www.youtube.com/@MrBeast/",  # Con slash final
        "https://www.youtube.com/@MrBeast/videos",  # Con subcarpeta
        "https://www.youtube.com/@MrBeast?tab=videos",  # Con parámetros
    ]
    
    rss_manager = RSSManager()
    
    print("🧪 Prueba Extensa de URLs de YouTube")
    print("=" * 60)
    
    successful_urls = []
    failed_urls = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📺 [{i:2d}/{len(test_urls)}] Probando: {url}")
        
        try:
            rss_url = rss_manager.get_youtube_rss_url(url)
            
            # Validar que el RSS sea accesible
            response = requests.get(rss_url, timeout=5)
            if response.status_code == 200 and 'xml' in response.headers.get('content-type', ''):
                print(f"   ✅ RSS válido: {rss_url}")
                successful_urls.append((url, rss_url))
            else:
                print(f"   ⚠️  RSS generado pero no accesible: {rss_url}")
                failed_urls.append(url)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_urls.append(url)
    
    # Resumen detallado
    print("\n" + "=" * 60)
    print("📊 RESUMEN DETALLADO")
    print("=" * 60)
    
    print(f"\n✅ URLs exitosas ({len(successful_urls)}):")
    for url, rss_url in successful_urls:
        print(f"   {url}")
        print(f"   → {rss_url}")
        print()
    
    if failed_urls:
        print(f"\n❌ URLs fallidas ({len(failed_urls)}):")
        for url in failed_urls:
            print(f"   {url}")
    
    success_rate = len(successful_urls) / len(test_urls) * 100
    print(f"\n📈 Estadísticas finales:")
    print(f"   • URLs probadas: {len(test_urls)}")
    print(f"   • URLs exitosas: {len(successful_urls)}")
    print(f"   • URLs fallidas: {len(failed_urls)}")
    print(f"   • Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 ¡Excelente! El sistema maneja muy bien las URLs de YouTube.")
    elif success_rate >= 75:
        print("\n👍 Bueno. El sistema maneja bien la mayoría de URLs de YouTube.")
    else:
        print("\n⚠️  Hay margen de mejora en el manejo de URLs de YouTube.")

if __name__ == "__main__":
    test_extensive_youtube_urls()
