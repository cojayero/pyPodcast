# PyPodcast - Generador de Podcasts Automático

Una aplicación en Python 3.9 con interfaz gráfica PySide que genera podcasts automáticamente a partir de contenido web y videos de YouTube.

## Especificación Detallada

### Objetivos
- Crear una aplicación GUI para generar podcasts automáticamente
- Procesar contenido de múltiples fuentes (YouTube, RSS, páginas web)
- Utilizar capacidades de ML de macOS para generar resúmenes
- Convertir texto a audio usando síntesis de voz de macOS

### Características Principales

#### Fuentes de Datos
- [x] Videos de canales de YouTube (vía RSS)
- [x] Feeds RSS de páginas web
- [x] Páginas web individuales

#### Interfaz de Usuario
- [x] Panel derecho: Lista de orígenes de datos con nombre, número de items y thumbnail
- [x] Panel izquierdo: Lista de items con estados (nuevo, procesado, escuchado, ignorar)
- [x] Reproductor integrado para contenido generado

#### Procesamiento de Contenido
- [x] Generación automática de resúmenes usando ML
- [x] Transcripción de videos de YouTube
- [x] Extracción de texto de páginas web
- [x] Conversión texto-a-voz usando síntesis de macOS

#### Base de Datos
- [x] SQLite para almacenamiento persistente
- [x] Gestión de estados de contenido
- [x] Metadatos de podcasts

### Estado de Implementación

| Componente | Estado | Descripción |
|------------|--------|-------------|
| Interfaz Principal | ✅ Completado | GUI con PySide6, layout de dos paneles |
| Base de Datos | ✅ Completado | SQLite con tablas para fuentes, items y configuración |
| Gestor de RSS | ✅ Completado | Lectura de feeds RSS y YouTube |
| Extractor Web | ✅ Completado | Extracción de contenido de páginas web |
| Transcriptor YouTube | ✅ Completado | Obtención de transcripciones de videos |
| Generador TTS | ✅ Completado | Síntesis de voz usando macOS |
| Reproductor Audio | ✅ Completado | Reproductor integrado con controles |
| Sistema Configuración | ✅ Completado | Archivo de configuración JSON |

### Archivos del Proyecto

#### Aplicación Principal
- `main.py` - Punto de entrada de la aplicación
- `app/main_window.py` - Ventana principal de la interfaz
- `app/widgets/` - Widgets personalizados de la UI

#### Modelos y Base de Datos
- `models/database.py` - Configuración y modelos de base de datos
- `models/data_source.py` - Modelo de fuentes de datos
- `models/content_item.py` - Modelo de items de contenido

#### Servicios
- `services/rss_manager.py` - Gestión de feeds RSS
- `services/web_extractor.py` - Extracción de contenido web
- `services/youtube_transcriber.py` - Transcripción de YouTube
- `services/text_to_speech.py` - Conversión texto-a-voz
- `services/audio_player.py` - Reproductor de audio

#### Utilidades
- `utils/config.py` - Gestión de configuración
- `utils/logger.py` - Sistema de logging

### Requisitos del Sistema
- Python 3.9+
- macOS (para síntesis de voz nativa)
- Conexión a internet para feeds RSS y YouTube

### Instalación
```bash
chmod +x setup_env.sh
./setup_env.sh
```

### Uso
```bash
source venv/bin/activate
python main.py
```

### Configuración
El archivo `config.json` se genera automáticamente en el primer uso y contiene:
- Directorios de salida para podcasts
- Configuración de TTS
- Preferencias de usuario
- Configuración de base de datos
