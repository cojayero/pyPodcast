#!/usr/bin/env python3
"""
Apple Intelligence Summarizer Service

Este módulo proporciona funcionalidad para generar resúmenes de texto utilizando
Apple Intelligence a través de la API local compatible con OpenAI.

Implementa las mejores prácticas documentadas en ComousarAppleIntelligence.txt,
incluyendo manejo de la ventana de contexto de 4096 tokens, fragmentación
inteligente para textos largos y prompts optimizados.

Funcionalidades:
- Resumen directo para textos cortos que caben en la ventana de contexto
- Fragmentación automática y resumen jerárquico para textos largos
- Prompts personalizables y optimizados
- Manejo robusto de errores específicos de Apple Intelligence
- Estimación de tokens y gestión de recursos

Author: Apple Intelligence Integration Team
Date: 2025
"""

import os
import logging
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import time

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available. Apple Intelligence summarizer disabled.")

# Configuración de logging
logger = logging.getLogger(__name__)

@dataclass
class AppleIntelligenceConfig:
    """Configuración para el servicio Apple Intelligence"""
    base_url: str = "http://127.0.0.1:11535/v1"
    api_key: str = "not-needed"  # No se necesita para el servidor local
    model_name: str = "apple-on-device"
    max_context_tokens: int = 4096  # Ventana de contexto total
    max_output_tokens: int = 500    # Tokens máximos para la salida
    temperature: float = 0.7        # Control de creatividad
    chunk_overlap: int = 200        # Solapamiento entre fragmentos
    chars_per_token: float = 3.5    # Estimación de caracteres por token (inglés)
    max_retries: int = 3            # Reintentos en caso de error
    retry_delay: float = 1.0        # Delay entre reintentos (segundos)

class AppleIntelligenceSummarizer:
    """
    Servicio para generar resúmenes usando Apple Intelligence.
    
    Utiliza el modelo Foundation de Apple a través de la API local
    compatible con OpenAI para generar resúmenes de alta calidad
    manteniendo la privacidad y evitando costos de API.
    """
    
    def __init__(self, config: Optional[AppleIntelligenceConfig] = None):
        """
        Inicializa el servicio Apple Intelligence.
        
        Args:
            config: Configuración personalizada. Si es None, usa configuración por defecto.
        """
        self.config = config or AppleIntelligenceConfig()
        self.client = None
        self.is_available = False
        
        if OPENAI_AVAILABLE:
            self._initialize_client()
        else:
            logger.warning("OpenAI library not available. Apple Intelligence disabled.")
    
    def _initialize_client(self) -> None:
        """Inicializa el cliente OpenAI para conectar con Apple Intelligence."""
        try:
            self.client = OpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key
            )
            
            # Verificar conectividad con el servidor local
            if self._test_connection():
                self.is_available = True
                logger.info("Apple Intelligence service initialized successfully")
            else:
                logger.warning("Apple Intelligence server not available")
                
        except Exception as e:
            logger.error(f"Error initializing Apple Intelligence client: {e}")
            self.is_available = False
    
    def _test_connection(self) -> bool:
        """
        Prueba la conexión con el servidor Apple Intelligence.
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario.
        """
        try:
            # Intenta una llamada simple para verificar conectividad
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                temperature=0.1
            )
            return True
        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estima el número de tokens en un texto.
        
        Args:
            text: El texto a analizar
            
        Returns:
            int: Estimación del número de tokens
        """
        return int(len(text) / self.config.chars_per_token)
    
    def can_fit_in_context(self, text: str, prompt: str) -> bool:
        """
        Verifica si un texto y prompt caben en la ventana de contexto.
        
        Args:
            text: El texto a resumir
            prompt: El prompt a usar
            
        Returns:
            bool: True si cabe en la ventana de contexto
        """
        total_input_tokens = self.estimate_tokens(text + prompt)
        available_tokens = self.config.max_context_tokens - self.config.max_output_tokens
        return total_input_tokens <= available_tokens
    
    def create_optimized_prompt(self, 
                              custom_prompt: Optional[str] = None,
                              max_words: int = 200,
                              style: str = "neutral",
                              format_type: str = "paragraph") -> str:
        """
        Crea un prompt optimizado siguiendo las mejores prácticas.
        
        Args:
            custom_prompt: Prompt personalizado del usuario
            max_words: Número máximo de palabras para el resumen
            style: Estilo del resumen (neutral, academic, casual)
            format_type: Formato de salida (paragraph, bullets, structured)
            
        Returns:
            str: Prompt optimizado
        """
        if custom_prompt:
            return custom_prompt
        
        # Prompt base optimizado siguiendo las mejores prácticas
        base_prompt = f"""Resume el siguiente texto de manera concisa y {style}.

INSTRUCCIONES:
- Máximo {max_words} palabras
- Mantén un tono {style} e informativo
- Incluye los puntos clave y conclusiones principales
- {"Usa formato de viñetas para los puntos principales" if format_type == "bullets" else "Escribe en párrafos claros y concisos"}
- No incluyas opiniones personales, solo hechos del texto original

Texto a resumir:
"""
        return base_prompt
    
    def split_text_into_chunks(self, text: str, prompt: str) -> List[str]:
        """
        Divide un texto largo en fragmentos manejables.
        
        Args:
            text: El texto a dividir
            prompt: El prompt que se usará (para calcular espacio disponible)
            
        Returns:
            List[str]: Lista de fragmentos de texto
        """
        prompt_tokens = self.estimate_tokens(prompt)
        available_tokens = (self.config.max_context_tokens - 
                          self.config.max_output_tokens - 
                          prompt_tokens - 100)  # 100 tokens de margen
        
        chunk_size_chars = int(available_tokens * self.config.chars_per_token)
        overlap_chars = int(self.config.chunk_overlap * self.config.chars_per_token)
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size_chars
            
            if end >= len(text):
                # Último fragmento
                chunks.append(text[start:])
                break
            
            # Intentar cortar en un límite de oración o párrafo
            chunk_text = text[start:end]
            
            # Buscar un buen punto de corte (final de oración)
            sentence_ends = [m.end() for m in re.finditer(r'[.!?]\s+', chunk_text)]
            if sentence_ends:
                # Usar el último final de oración dentro del fragmento
                actual_end = start + sentence_ends[-1]
                chunks.append(text[start:actual_end])
                start = actual_end - overlap_chars
            else:
                # Si no hay finales de oración, cortar en el límite
                chunks.append(chunk_text)
                start = end - overlap_chars
            
            # Asegurar que no retrocedemos
            if start < 0:
                start = 0
        
        return chunks
    
    def summarize_chunk(self, 
                       chunk: str, 
                       prompt: str, 
                       is_partial: bool = False) -> Optional[str]:
        """
        Genera un resumen para un fragmento individual.
        
        Args:
            chunk: El fragmento de texto a resumir
            prompt: El prompt a usar
            is_partial: Si True, indica que es parte de un texto más largo
            
        Returns:
            Optional[str]: El resumen generado o None si hay error
        """
        if not self.is_available:
            logger.error("Apple Intelligence service not available")
            return None
        
        # Ajustar el prompt para fragmentos parciales
        if is_partial:
            adjusted_prompt = prompt + "\n\nNOTA: Este es un fragmento de un texto más largo. Enfócate en resumir solo este fragmento:"
        else:
            adjusted_prompt = prompt
        
        messages = [
            {"role": "user", "content": f"{adjusted_prompt}\n\n{chunk}"}
        ]
        
        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    max_tokens=self.config.max_output_tokens,
                    temperature=self.config.temperature,
                    stream=False
                )
                
                summary = response.choices[0].message.content
                return summary.strip()
                
            except Exception as e:
                error_str = str(e)
                
                if "exceededContextWindowSize" in error_str:
                    logger.error("Context window exceeded even for chunk. Text may be too complex.")
                    return None
                
                if attempt < self.config.max_retries - 1:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(self.config.retry_delay)
                else:
                    logger.error(f"All attempts failed for chunk summarization: {e}")
                    return None
        
        return None
    
    def hierarchical_summarize(self, summaries: List[str], final_prompt: str) -> Optional[str]:
        """
        Combina múltiples resúmenes parciales en un resumen final.
        
        Args:
            summaries: Lista de resúmenes parciales
            final_prompt: Prompt para el resumen final
            
        Returns:
            Optional[str]: Resumen final combinado
        """
        combined_text = "\n\n".join(summaries)
        
        # Verificar si el texto combinado cabe en la ventana de contexto
        if self.can_fit_in_context(combined_text, final_prompt):
            return self.summarize_chunk(combined_text, final_prompt, is_partial=False)
        else:
            # Si aún es muy largo, dividir de nuevo recursivamente
            logger.info("Combined summaries still too long, applying recursive summarization")
            chunks = self.split_text_into_chunks(combined_text, final_prompt)
            recursive_summaries = []
            
            for chunk in chunks:
                chunk_summary = self.summarize_chunk(chunk, final_prompt, is_partial=True)
                if chunk_summary:
                    recursive_summaries.append(chunk_summary)
            
            if recursive_summaries:
                # Intento final de combinación
                final_combined = "\n\n".join(recursive_summaries)
                return self.summarize_chunk(final_combined, final_prompt, is_partial=False)
        
        return None
    
    def summarize(self, 
                  text: str, 
                  custom_prompt: Optional[str] = None,
                  max_words: int = 200,
                  style: str = "neutral",
                  format_type: str = "paragraph") -> Dict[str, Any]:
        """
        Genera un resumen del texto proporcionado.
        
        Args:
            text: El texto a resumir
            custom_prompt: Prompt personalizado (opcional)
            max_words: Número máximo de palabras
            style: Estilo del resumen
            format_type: Formato de salida
            
        Returns:
            Dict[str, Any]: Resultado con el resumen y metadatos
        """
        if not self.is_available:
            return {
                'success': False,
                'error': 'Apple Intelligence service not available',
                'summary': None,
                'method': 'none',
                'chunks_processed': 0,
                'total_tokens_estimated': 0
            }
        
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'Empty text provided',
                'summary': None,
                'method': 'none',
                'chunks_processed': 0,
                'total_tokens_estimated': 0
            }
        
        # Crear prompt optimizado
        prompt = self.create_optimized_prompt(custom_prompt, max_words, style, format_type)
        
        # Estimación de tokens
        total_tokens = self.estimate_tokens(text)
        
        start_time = time.time()
        
        # Determinar estrategia basada en el tamaño del texto
        if self.can_fit_in_context(text, prompt):
            # Resumen directo - el texto cabe en la ventana de contexto
            logger.info("Using direct summarization (text fits in context window)")
            
            summary = self.summarize_chunk(text, prompt, is_partial=False)
            method = "direct"
            chunks_processed = 1
            
        else:
            # Resumen por fragmentos con combinación jerárquica
            logger.info("Using chunked summarization (text exceeds context window)")
            
            chunks = self.split_text_into_chunks(text, prompt)
            logger.info(f"Text split into {len(chunks)} chunks")
            
            # Resumir cada fragmento
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                chunk_summary = self.summarize_chunk(chunk, prompt, is_partial=True)
                if chunk_summary:
                    chunk_summaries.append(chunk_summary)
                else:
                    logger.warning(f"Failed to summarize chunk {i+1}")
            
            if not chunk_summaries:
                return {
                    'success': False,
                    'error': 'Failed to summarize any chunks',
                    'summary': None,
                    'method': 'chunked_failed',
                    'chunks_processed': 0,
                    'total_tokens_estimated': total_tokens
                }
            
            # Combinar resúmenes parciales
            final_prompt = self.create_optimized_prompt(
                f"Combina los siguientes resúmenes parciales en un resumen coherente y completo de máximo {max_words} palabras:",
                max_words, style, format_type
            )
            
            summary = self.hierarchical_summarize(chunk_summaries, final_prompt)
            method = "hierarchical"
            chunks_processed = len(chunks)
        
        processing_time = time.time() - start_time
        
        if summary:
            return {
                'success': True,
                'summary': summary,
                'method': method,
                'chunks_processed': chunks_processed,
                'total_tokens_estimated': total_tokens,
                'processing_time_seconds': round(processing_time, 2),
                'words_in_summary': len(summary.split()) if summary else 0,
                'compression_ratio': round(len(text) / len(summary), 2) if summary else 0
            }
        else:
            return {
                'success': False,
                'error': 'Failed to generate summary',
                'summary': None,
                'method': method,
                'chunks_processed': chunks_processed,
                'total_tokens_estimated': total_tokens,
                'processing_time_seconds': round(processing_time, 2)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado del servicio Apple Intelligence.
        
        Returns:
            Dict[str, Any]: Estado del servicio
        """
        return {
            'available': self.is_available,
            'openai_library_installed': OPENAI_AVAILABLE,
            'server_url': self.config.base_url,
            'model_name': self.config.model_name,
            'max_context_tokens': self.config.max_context_tokens,
            'max_output_tokens': self.config.max_output_tokens,
            'estimated_max_input_chars': int(
                (self.config.max_context_tokens - self.config.max_output_tokens) * 
                self.config.chars_per_token
            )
        }

# Instancia global del servicio
_apple_intelligence_service = None

def get_apple_intelligence_service() -> AppleIntelligenceSummarizer:
    """
    Obtiene la instancia global del servicio Apple Intelligence.
    
    Returns:
        AppleIntelligenceSummarizer: Instancia del servicio
    """
    global _apple_intelligence_service
    if _apple_intelligence_service is None:
        _apple_intelligence_service = AppleIntelligenceSummarizer()
    return _apple_intelligence_service

def is_apple_intelligence_available() -> bool:
    """
    Verifica si Apple Intelligence está disponible.
    
    Returns:
        bool: True si está disponible
    """
    service = get_apple_intelligence_service()
    return service.is_available

def summarize_with_apple_intelligence(text: str, 
                                    custom_prompt: Optional[str] = None,
                                    **kwargs) -> Dict[str, Any]:
    """
    Función de conveniencia para resumir texto con Apple Intelligence.
    
    Args:
        text: Texto a resumir
        custom_prompt: Prompt personalizado
        **kwargs: Argumentos adicionales para el método summarize
        
    Returns:
        Dict[str, Any]: Resultado del resumen
    """
    service = get_apple_intelligence_service()
    return service.summarize(text, custom_prompt, **kwargs)

if __name__ == "__main__":
    # Ejemplo de uso y prueba
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    # Crear servicio
    service = AppleIntelligenceSummarizer()
    
    # Mostrar estado
    status = service.get_status()
    print("=== Apple Intelligence Service Status ===")
    for key, value in status.items():
        print(f"{key}: {value}")
    
    if service.is_available:
        # Texto de prueba
        test_text = """
        Apple Intelligence represents a breakthrough in on-device AI processing, bringing powerful language
        models directly to users' devices while maintaining privacy. The system uses a 3-billion parameter
        model that runs locally on Apple Silicon, providing fast, secure, and cost-effective AI capabilities.
        
        Key features include text summarization, writing assistance, and intelligent content analysis.
        The Foundation Models framework allows developers to integrate these capabilities into their
        applications with minimal code, typically requiring just three lines of Swift code.
        
        However, the on-device model has limitations, including a 4096-token context window and
        reduced reasoning capabilities compared to larger cloud-based models. This makes it ideal
        for focused tasks like summarization and text editing, but may struggle with complex
        reasoning or very long documents.
        """
        
        print("\n=== Testing Apple Intelligence Summarization ===")
        print(f"Input text length: {len(test_text)} characters")
        print(f"Estimated tokens: {service.estimate_tokens(test_text)}")
        
        # Probar resumen
        result = service.summarize(
            text=test_text,
            max_words=100,
            style="academic",
            format_type="paragraph"
        )
        
        print(f"\nSummarization result:")
        for key, value in result.items():
            print(f"{key}: {value}")
            
        if result['success']:
            print(f"\n=== Generated Summary ===")
            print(result['summary'])
    else:
        print("\nApple Intelligence service not available. Please ensure:")
        print("1. macOS Sequoia 15.1+ is installed")
        print("2. Apple Intelligence is enabled in System Settings")
        print("3. AppleOnDeviceOpenAI server is running on localhost:11535")
        print("4. OpenAI Python library is installed (pip install openai)")
