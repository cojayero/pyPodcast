#!/usr/bin/env python3
"""
Script para probar la compatibilidad de pygame con diferentes formatos de audio
"""

import pygame
import subprocess
import tempfile
import os
from pathlib import Path
import time

def test_pygame_formats():
    """Prueba qué formatos puede cargar pygame"""
    print("=== PRUEBA DE COMPATIBILIDAD DE PYGAME ===\n")
    
    # Inicializar pygame
    try:
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        print("✓ Pygame inicializado correctamente")
    except Exception as e:
        print(f"✗ Error inicializando pygame: {e}")
        return
    
    # Crear archivo de audio de prueba con 'say'
    temp_dir = Path(tempfile.mkdtemp())
    test_text = "Hola, esto es una prueba de audio"
    
    # Generar archivo AIFF original
    aiff_file = temp_dir / "test.aiff"
    cmd = ['say', '-v', 'Jorge', '-o', str(aiff_file), test_text]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Error generando archivo AIFF: {result.stderr}")
            return
        print(f"✓ Archivo AIFF generado: {aiff_file}")
    except Exception as e:
        print(f"✗ Error ejecutando 'say': {e}")
        return
    
    # Lista de formatos a probar
    formats_to_test = [
        ("AIFF original", str(aiff_file)),
    ]
    
    # Intentar convertir a otros formatos
    wav_file = temp_dir / "test.wav"
    mp3_file = temp_dir / "test.mp3"
    m4a_file = temp_dir / "test.m4a"
    ogg_file = temp_dir / "test.ogg"
    
    # Convertir a WAV usando afconvert
    try:
        cmd = ['afconvert', '-f', 'WAVE', '-d', 'LEI16@44100', str(aiff_file), str(wav_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            formats_to_test.append(("WAV (convertido)", str(wav_file)))
            print(f"✓ Archivo WAV convertido: {wav_file}")
        else:
            print(f"✗ Error convirtiendo a WAV: {result.stderr}")
    except Exception as e:
        print(f"✗ Error en conversión WAV: {e}")
    
    # Convertir a M4A usando afconvert
    try:
        cmd = ['afconvert', '-f', 'm4af', '-d', 'aac', str(aiff_file), str(m4a_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            formats_to_test.append(("M4A/AAC (convertido)", str(m4a_file)))
            print(f"✓ Archivo M4A convertido: {m4a_file}")
        else:
            print(f"✗ Error convirtiendo a M4A: {result.stderr}")
    except Exception as e:
        print(f"✗ Error en conversión M4A: {e}")
    
    # Intentar convertir con ffmpeg si está disponible
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        
        # Convertir a OGG
        cmd = ['ffmpeg', '-i', str(aiff_file), '-c:a', 'libvorbis', '-y', str(ogg_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            formats_to_test.append(("OGG Vorbis (ffmpeg)", str(ogg_file)))
            print(f"✓ Archivo OGG convertido: {ogg_file}")
        
        # Convertir a MP3 si tiene libmp3lame
        cmd = ['ffmpeg', '-i', str(aiff_file), '-c:a', 'libmp3lame', '-b:a', '128k', '-y', str(mp3_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            formats_to_test.append(("MP3 (ffmpeg)", str(mp3_file)))
            print(f"✓ Archivo MP3 convertido: {mp3_file}")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ℹ ffmpeg no disponible")
    
    print(f"\n=== PROBANDO CARGA EN PYGAME ===")
    print(f"Total de formatos a probar: {len(formats_to_test)}\n")
    
    # Probar cada formato
    successful_formats = []
    failed_formats = []
    
    for format_name, file_path in formats_to_test:
        print(f"Probando {format_name}...")
        
        if not Path(file_path).exists():
            print(f"  ✗ Archivo no existe: {file_path}")
            failed_formats.append((format_name, "Archivo no existe"))
            continue
        
        file_size = Path(file_path).stat().st_size
        print(f"  📁 Tamaño: {file_size} bytes")
        
        try:
            # Intentar cargar el archivo
            pygame.mixer.music.load(file_path)
            print(f"  ✓ Carga exitosa")
            
            # Intentar reproducir brevemente
            pygame.mixer.music.play()
            time.sleep(0.5)  # Reproducir por medio segundo
            
            if pygame.mixer.music.get_busy():
                print(f"  ✓ Reproducción exitosa")
                successful_formats.append(format_name)
                pygame.mixer.music.stop()
            else:
                print(f"  ⚠ Carga exitosa pero no reproduce")
                failed_formats.append((format_name, "No reproduce"))
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            failed_formats.append((format_name, str(e)))
        
        print()
    
    # Mostrar resumen
    print("=== RESUMEN ===")
    print(f"✓ Formatos exitosos ({len(successful_formats)}):")
    for fmt in successful_formats:
        print(f"  - {fmt}")
    
    print(f"\n✗ Formatos fallidos ({len(failed_formats)}):")
    for fmt, error in failed_formats:
        print(f"  - {fmt}: {error}")
    
    # Mostrar información de pygame
    print(f"\n=== INFO PYGAME ===")
    print(f"Versión pygame: {pygame.version.ver}")
    print(f"Versión SDL: {pygame.version.SDL}")
    
    # Limpiar archivos temporales
    try:
        for _, file_path in formats_to_test:
            if Path(file_path).exists():
                Path(file_path).unlink()
        temp_dir.rmdir()
        print(f"\n🧹 Archivos temporales limpiados")
    except Exception as e:
        print(f"\n⚠ Error limpiando archivos temporales: {e}")
    
    pygame.mixer.quit()
    
    # Recomendar solución
    print(f"\n=== RECOMENDACIONES ===")
    if successful_formats:
        print(f"🎉 Pygame soporta: {', '.join(successful_formats)}")
        if 'WAV (convertido)' in successful_formats:
            print("💡 SOLUCIÓN: Convertir archivos de TTS a WAV para máxima compatibilidad")
        elif 'OGG Vorbis (ffmpeg)' in successful_formats:
            print("💡 SOLUCIÓN: Convertir archivos de TTS a OGG para compatibilidad")
    else:
        print("😞 Ningún formato funcionó correctamente")
        print("💡 ALTERNATIVA: Considerar usar otra librería como python-vlc o PyQt5.QtMultimedia")

if __name__ == "__main__":
    test_pygame_formats()
