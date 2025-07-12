#!/usr/bin/env python3
"""
Script de prueba mejorado para URLs de YouTube problemáticas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.rss_manager import RSSManager
from utils.logger import setup_logger
import requests
import re

# Configurar logger
logger = setup_logger()

def test_manual_rss_discovery(channel_url):
    """Prueba manual de descubrimiento de RSS"""
    print(f"\n🔍 Analizando manualmente: {channel_url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        
        response = requests.get(channel_url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Buscar patterns de channel ID
            patterns = [
                r'"channelId":"([^"]+)"',
                r'"externalId":"([^"]+)"',
                r'"browseId":"([^"]+)"',
                r'channel/([^/"]+)',
                r'"webCommandMetadata":{"url":"/channel/([^"]+)"',
                r'"navigationEndpoint":{"commandMetadata":{"webCommandMetadata":{"url":"/channel/([^"]+)"',
                r'<meta property="og:url" content="https://www\.youtube\.com/channel/([^"]+)"',
                r'<link rel="canonical" href="https://www\.youtube\.com/channel/([^"]+)"'
            ]
            
            found_ids = []
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, content)
                if matches:
                    print(f"   Pattern {i+1}: {matches[:3]}...")  # Mostrar primeros 3
                    for match in matches:
                        if len(match) == 24 and match.startswith('UC'):
                            found_ids.append(match)
            
            if found_ids:
                unique_ids = list(set(found_ids))
                print(f"   ✅ Channel IDs encontrados: {unique_ids}")
                
                # Probar cada ID
                for channel_id in unique_ids:
                    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                    try:
                        rss_response = requests.get(rss_url, timeout=5)
                        if rss_response.status_code == 200:
                            print(f"   ✅ RSS válido: {rss_url}")
                            return rss_url
                        else:
                            print(f"   ❌ RSS inválido ({rss_response.status_code}): {rss_url}")
                    except Exception as e:
                        print(f"   ❌ Error probando RSS: {e}")
            else:
                print("   ❌ No se encontraron channel IDs válidos")
                
                # Buscar handles alternativos
                handle_patterns = [
                    r'"handle":"@([^"]+)"',
                    r'"handle":{"runs":\[{"text":"@([^"]+)"}',
                    r'@([a-zA-Z0-9_.-]+)'
                ]
                
                for pattern in handle_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"   🔍 Handles encontrados: {matches[:5]}")
                        for handle in matches[:3]:  # Probar primeros 3
                            for feed_format in [
                                f"https://www.youtube.com/feeds/videos.xml?user={handle}",
                                f"https://www.youtube.com/@{handle}/videos.rss"
                            ]:
                                try:
                                    rss_response = requests.get(feed_format, timeout=5)
                                    if rss_response.status_code == 200:
                                        print(f"   ✅ RSS válido: {feed_format}")
                                        return feed_format
                                except:
                                    pass
        
        print("   ❌ No se pudo obtener RSS válido")
        return None
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_youtube_urls():
    """Prueba URLs problemáticas de YouTube"""
    
    # URLs problemáticas reportadas
    test_urls = [
        "https://www.youtube.com/TEDTalks",  # URL problemática reportada
        "https://www.youtube.com/@TEDTalks",
        "https://www.youtube.com/c/TEDTalks", 
        "https://www.youtube.com/user/TEDtalksDirector",
        "https://www.youtube.com/channel/UCAuUUnT6oDeKwE6v1NGQxug",  # TED oficial
        "https://www.youtube.com/@MrBeast",
        "https://www.youtube.com/c/MrBeast6000",
        "https://www.youtube.com/@mkbhd",
        "https://www.youtube.com/user/marquesbrownlee"
    ]
    
    rss_manager = RSSManager()
    
    print("🧪 Probando URLs de YouTube...")
    print("=" * 60)
    
    successful_urls = []
    failed_urls = []
    
    for url in test_urls:
        print(f"\n📺 Probando: {url}")
        
        try:
            # Probar con el RSS Manager actual
            rss_url = rss_manager.get_youtube_rss_url(url)
            print(f"   ✅ RSS Manager: {rss_url}")
            successful_urls.append((url, rss_url))
            
        except Exception as e:
            print(f"   ❌ RSS Manager falló: {e}")
            failed_urls.append(url)
            
            # Probar método manual
            manual_rss = test_manual_rss_discovery(url)
            if manual_rss:
                print(f"   ✅ Método manual encontró: {manual_rss}")
                successful_urls.append((url, manual_rss))
            else:
                print(f"   ❌ Método manual también falló")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    print(f"\n✅ URLs exitosas ({len(successful_urls)}):")
    for url, rss_url in successful_urls:
        print(f"   {url} → {rss_url}")
    
    print(f"\n❌ URLs fallidas ({len(failed_urls)}):")
    for url in failed_urls:
        print(f"   {url}")
    
    success_rate = len(successful_urls) / len(test_urls) * 100
    print(f"\n📈 Tasa de éxito: {success_rate:.1f}%")

if __name__ == "__main__":
    test_youtube_urls()
