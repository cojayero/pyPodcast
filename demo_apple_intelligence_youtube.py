#!/usr/bin/env python3
"""
Demostración de Apple Intelligence para Resúmenes de YouTube

Este script demuestra cómo usar la implementación de Apple Intelligence
para resumir transcripciones de YouTube, siguiendo exactamente el ejemplo
proporcionado en ComousarAppleIntelligence.txt.

Funcionalidades demostradas:
- Lectura de archivos de transcripción
- Generación de resúmenes con prompts personalizados  
- Manejo de la ventana de contexto de 4096 tokens
- Fragmentación automática para textos largos
- Prompts optimizados para diferentes estilos

Author: Demo Team
Date: 2025
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from services.apple_intelligence_summarizer import get_apple_intelligence_service
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_transcription_file(file_path: str) -> str:
    """
    Lee el contenido de un archivo de transcripción de texto.
    
    (Implementación basada en ComousarAppleIntelligence.txt)

    Args:
        file_path (str): La ruta al archivo de transcripción.

    Returns:
        str: El contenido del archivo como una cadena, o None si ocurre un error.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{file_path}'.")
        return None
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return None

def create_sample_transcript():
    """Crea una transcripción de ejemplo para la demostración"""
    return """
    Hola y bienvenidos a nuestro canal de tecnología. En el video de hoy vamos a hablar sobre
    Apple Intelligence, la nueva plataforma de inteligencia artificial que Apple ha integrado
    en sus dispositivos más recientes.
    
    Apple Intelligence representa un cambio fundamental en cómo pensamos sobre la IA personal.
    A diferencia de otros sistemas que dependen de la nube, Apple Intelligence funciona
    completamente en el dispositivo, lo que significa que tus datos nunca salen de tu Mac,
    iPhone o iPad.
    
    Las características principales incluyen herramientas de escritura que pueden resumir,
    corregir y reescribir texto automáticamente. También hay capacidades avanzadas de
    análisis de contenido que pueden extraer información clave de documentos largos.
    
    Una de las ventajas más importantes es la privacidad. Como todo el procesamiento ocurre
    localmente, no tienes que preocuparte por enviar información sensible a servidores
    externos. Esto es especialmente importante para profesionales y empresas que manejan
    datos confidenciales.
    
    En términos de rendimiento, Apple Intelligence es sorprendentemente rápido. Las respuestas
    son prácticamente instantáneas porque no hay latencia de red. Además, una vez que compras
    el dispositivo, no hay costos adicionales por usar estas funciones de IA.
    
    Sin embargo, también hay algunas limitaciones que debemos mencionar. El modelo en el
    dispositivo tiene una ventana de contexto más pequeña comparado con modelos en la nube,
    lo que significa que puede tener dificultades con documentos extremadamente largos.
    
    Para los desarrolladores, Apple ha hecho muy fácil integrar estas capacidades en sus
    aplicaciones. El framework Foundation Models permite añadir funcionalidades de IA
    con solo unas pocas líneas de código.
    
    En resumen, Apple Intelligence marca un hito importante en la democratización de la IA,
    haciendo que herramientas poderosas estén disponibles directamente en nuestros dispositivos
    sin comprometer la privacidad o generar costos adicionales.
    
    Eso es todo por hoy. Si te gustó este video, no olvides darle like y suscribirte para
    más contenido sobre tecnología. Nos vemos en el próximo video.
    """

def demo_youtube_summarization():
    """Demostración principal de resumen de transcripción de YouTube"""
    print("🎥 DEMOSTRACIÓN: Resumen de Transcripción de YouTube con Apple Intelligence")
    print("=" * 70)
    print("Basado en la implementación de ComousarAppleIntelligence.txt\n")
    
    # Obtener servicio Apple Intelligence
    service = get_apple_intelligence_service()
    
    # Mostrar estado del servicio
    print("📊 Estado del Servicio:")
    status = service.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    if not service.is_available:
        print("\n⚠️  NOTA: Apple Intelligence no está disponible.")
        print("Esta demostración mostrará la funcionalidad usando datos simulados.\n")
        print("Para usar Apple Intelligence realmente:")
        print("1. Asegúrate de tener macOS Sequoia 15.1+")
        print("2. Habilita Apple Intelligence en Configuración del Sistema")
        print("3. Descarga y ejecuta AppleOnDeviceOpenAI")
        print("4. Verifica que esté ejecutándose en localhost:11535\n")
    
    # Crear transcripción de ejemplo
    print("📝 Creando transcripción de ejemplo...")
    transcript = create_sample_transcript()
    
    print(f"   Longitud: {len(transcript)} caracteres")
    print(f"   Tokens estimados: {service.estimate_tokens(transcript)}")
    print(f"   ¿Cabe en ventana de contexto?: {service.can_fit_in_context(transcript, 'Resume este video.')}")
    
    # Mostrar fragmento de la transcripción
    print(f"\n📄 Fragmento de la transcripción:")
    print("-" * 50)
    print(transcript[:300] + "..." if len(transcript) > 300 else transcript)
    print("-" * 50)
    
    # Diferentes estilos de resumen
    summarization_styles = [
        {
            "name": "Resumen Ejecutivo",
            "prompt": """Por favor, proporciona un resumen ejecutivo de la siguiente transcripción de video de YouTube.
            
FORMATO REQUERIDO:
- Máximo 150 palabras
- Tono profesional y objetivo
- Incluye los puntos principales y conclusiones
- Estructura clara con introducción, desarrollo y conclusión

Transcripción del video:""",
            "max_words": 150,
            "style": "professional"
        },
        {
            "name": "Resumen para Estudiantes",
            "prompt": """Resume esta transcripción de video para un estudiante universitario.
            
INSTRUCCIONES:
- Usa lenguaje claro y accesible
- Máximo 100 palabras
- Enfócate en los conceptos clave y aplicaciones prácticas
- Incluye las ventajas y limitaciones mencionadas

Contenido del video:""",
            "max_words": 100,
            "style": "educational"
        },
        {
            "name": "Lista de Puntos Clave",
            "prompt": """Extrae los puntos clave de esta transcripción en formato de lista.

FORMATO:
• Punto principal 1
• Punto principal 2  
• Punto principal 3
(máximo 5 puntos, cada uno de 15-20 palabras)

Transcripción:""",
            "max_words": 80,
            "style": "bullet_points"
        }
    ]
    
    # Generar resúmenes con diferentes estilos
    for i, style_config in enumerate(summarization_styles, 1):
        print(f"\n{i}. 🎯 Generando {style_config['name']}...")
        print("-" * 40)
        
        if service.is_available:
            # Usar Apple Intelligence real
            result = service.summarize(
                text=transcript,
                custom_prompt=style_config['prompt'],
                max_words=style_config['max_words'],
                style="neutral"
            )
            
            if result['success']:
                print(f"✅ Resumen generado exitosamente:")
                print(f"   Método: {result['method']}")
                print(f"   Fragmentos procesados: {result['chunks_processed']}")
                print(f"   Tiempo de procesamiento: {result['processing_time_seconds']}s")
                print(f"   Palabras en resumen: {result['words_in_summary']}")
                print(f"   Ratio de compresión: {result['compression_ratio']}:1")
                print()
                print(f"📋 {style_config['name']}:")
                print(result['summary'])
            else:
                print(f"❌ Error generando resumen: {result.get('error', 'Desconocido')}")
        else:
            # Simulación para cuando Apple Intelligence no está disponible
            print(f"🔄 Simulando {style_config['name']} (Apple Intelligence no disponible)")
            print("   [Este sería el resumen generado por Apple Intelligence]")
            print("   Método: simulated")
            print("   Estado: service_unavailable")
    
    print(f"\n" + "=" * 70)
    print("✨ DEMOSTRACIÓN COMPLETADA")
    print("=" * 70)
    
    if service.is_available:
        print("🎉 Apple Intelligence funcionó correctamente!")
        print("   Todos los resúmenes fueron generados usando el modelo local.")
    else:
        print("ℹ️  Esta fue una demostración simulada.")
        print("   Para ver Apple Intelligence en acción, completa la configuración.")
    
    print("\n📚 Funcionalidades demostradas:")
    print("   ✓ Lectura de transcripciones")
    print("   ✓ Prompts personalizados optimizados")
    print("   ✓ Múltiples estilos de resumen")
    print("   ✓ Manejo automático de texto largo")
    print("   ✓ Estimación de tokens y gestión de contexto")
    print("   ✓ Métricas de rendimiento y compresión")

def demo_file_based_summarization():
    """Demostración usando archivo de transcripción real"""
    print(f"\n" + "=" * 70)
    print("📁 DEMOSTRACIÓN ADICIONAL: Resumen desde Archivo")
    print("=" * 70)
    
    # Crear archivo de ejemplo
    sample_file = "youtube_transcript_demo.txt"
    transcript_content = create_sample_transcript()
    
    try:
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(transcript_content)
        print(f"✅ Archivo de ejemplo creado: {sample_file}")
    except Exception as e:
        print(f"❌ Error creando archivo: {e}")
        return
    
    # Leer el archivo usando la función del documento
    print(f"📖 Leyendo transcripción de: {sample_file}")
    transcript = read_transcription_file(sample_file)
    
    if transcript:
        print("✅ Transcripción cargada exitosamente.")
        
        # Prompt personalizado según el ejemplo del documento
        custom_summary_prompt = """Por favor, proporciona un resumen conciso de la siguiente transcripción 
de video de YouTube, destacando los temas principales y las conclusiones. Mantenlo por debajo de 200 palabras."""
        
        service = get_apple_intelligence_service()
        
        if service.is_available:
            print("🤖 Generando resumen con Apple Intelligence...")
            result = service.summarize(
                text=transcript,
                custom_prompt=custom_summary_prompt,
                max_words=200
            )
            
            if result['success']:
                print("\n--- 📋 Resumen Generado ---")
                print(result['summary'])
                print(f"\n📊 Estadísticas:")
                print(f"   Palabras originales: ~{len(transcript.split())}")
                print(f"   Palabras en resumen: {result['words_in_summary']}")
                print(f"   Compresión: {result['compression_ratio']}:1")
            else:
                print(f"\n❌ Fallo al generar el resumen: {result.get('error')}")
        else:
            print("⚠️ Apple Intelligence no disponible - usando fallback")
    else:
        print("❌ No se pudo proceder con el resumen debido a un error al leer el archivo.")
    
    # Limpiar archivo temporal
    try:
        os.remove(sample_file)
        print(f"\n🧹 Archivo temporal eliminado: {sample_file}")
    except:
        pass

def main():
    """Función principal de la demostración"""
    print("🍎 APPLE INTELLIGENCE - DEMOSTRACIÓN DE RESÚMENES DE YOUTUBE")
    print("Implementación basada en ComousarAppleIntelligence.txt")
    print("=" * 70)
    
    # Ejecutar demostraciones
    demo_youtube_summarization()
    demo_file_based_summarization()
    
    print(f"\n" + "🎬" * 20)
    print("¡Demostración completada!")
    print("Ahora puedes usar Apple Intelligence para resumir tus propias transcripciones de YouTube.")

if __name__ == "__main__":
    main()
