# PyPodcast 🎧

Una aplicación de escritorio para generar podcasts automáticamente a partir de contenido web y videos de YouTube.

## Características Principales

- 📺 **Soporte para YouTube**: Extrae transcripciones de videos de YouTube automáticamente
- 🌐 **Feeds RSS**: Monitorea feeds RSS de blogs y sitios web
- 📄 **Extracción web**: Procesa páginas web individuales
- 🤖 **Resúmenes automáticos**: Genera resúmenes inteligentes del contenido
- 🗣️ **Síntesis de voz**: Convierte texto a audio usando las capacidades nativas de macOS
- 🎵 **Reproductor integrado**: Escucha los podcasts directamente en la aplicación
- 💾 **Base de datos local**: Almacena todo localmente con SQLite
- 🎨 **Interfaz moderna**: GUI construida con PySide6

## Requisitos del Sistema

- **macOS** (requerido para síntesis de voz nativa)
- **Python 3.9+**
- Conexión a internet para feeds RSS y YouTube

## Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd pyPodcast
```

### 2. Configurar entorno virtual
```bash
chmod +x setup_env.sh
./setup_env.sh
```

### 3. Activar entorno virtual
```bash
source venv/bin/activate
```

### 4. Ejecutar la aplicación
```bash
python main.py
```

## Uso

### Añadir Fuentes de Datos

1. Haz clic en "Añadir" en el panel de fuentes de datos
2. Selecciona el tipo de fuente:
   - **Canal YouTube**: Pega la URL del canal
   - **Feed RSS**: URL del feed RSS
   - **Página Web**: URL de una página específica
3. Opcionalmente añade un nombre y descripción
4. Haz clic en "Probar" para validar la fuente
5. Guarda la fuente

### Procesar Contenido

1. Selecciona una fuente de datos del panel derecho
2. En el panel izquierdo verás todos los elementos de esa fuente
3. Haz clic derecho en un elemento y selecciona "Procesar"
4. El sistema extraerá el contenido, generará un resumen y creará el audio
5. Una vez procesado, podrás reproducir el podcast

### Estados de Contenido

- **Nuevo**: Recién descubierto, pendiente de procesamiento
- **Procesado**: Resumen y audio generados
- **Escuchado**: Marcado como escuchado
- **Ignorar**: Contenido que no deseas procesar

## Estructura del Proyecto

```
pyPodcast/
├── main.py                 # Punto de entrada
├── app/                    # Interfaz gráfica
│   ├── main_window.py     # Ventana principal
│   └── widgets/           # Widgets personalizados
├── models/                 # Modelos de datos
│   ├── database.py        # Gestión de base de datos
│   ├── data_source.py     # Modelo de fuentes
│   └── content_item.py    # Modelo de contenido
├── services/              # Servicios de negocio
│   ├── rss_manager.py     # Gestión de RSS
│   ├── web_extractor.py   # Extracción web
│   ├── youtube_transcriber.py # Transcripción YouTube
│   ├── text_to_speech.py  # Síntesis de voz
│   └── audio_player.py    # Reproductor audio
├── utils/                 # Utilidades
│   ├── config.py          # Configuración
│   └── logger.py          # Logging
├── data/                  # Base de datos (creado automáticamente)
├── podcasts/              # Archivos de audio generados
├── logs/                  # Archivos de log
└── requirements.txt       # Dependencias
```

## Configuración

La aplicación genera automáticamente un archivo `config.json` en la primera ejecución. Puedes modificar:

- **Voz de síntesis**: Cambiar entre las voces disponibles en macOS
- **Calidad de audio**: Ajustar velocidad y calidad
- **Intervalos de actualización**: Frecuencia de actualización automática
- **Directorios**: Ubicación de archivos generados

## Desarrollo

### Añadir nuevas características

1. **Nuevos extractores**: Implementa en `services/`
2. **Nuevos widgets**: Añade en `app/widgets/`
3. **Nuevos modelos**: Añade en `models/`

### Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-qt

# Ejecutar tests
pytest tests/
```

### Logging

Los logs se almacenan en `logs/` con rotación diaria. Niveles:
- **INFO**: Operaciones normales
- **WARNING**: Situaciones no críticas
- **ERROR**: Errores que requieren atención

## Limitaciones Conocidas

- Solo funciona en macOS (dependencia de `say` para TTS)
- pygame no soporta seek preciso en archivos de audio
- Algunos videos de YouTube pueden no tener transcripciones disponibles
- La extracción web puede fallar en sitios con contenido dinámico (JavaScript)

## Roadmap

- [ ] Soporte para otros sistemas operativos
- [ ] Integración con servicios de TTS en la nube
- [ ] Soporte para más formatos de audio
- [ ] Detección automática de idioma
- [ ] Clasificación automática de contenido
- [ ] Exportación de podcasts
- [ ] Interfaz web opcional

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Soporte

Si encuentras bugs o tienes sugerencias:

1. Revisa los logs en `logs/`
2. Consulta `bugs.csv` para problemas conocidos
3. Abre un issue en GitHub

---

Desarrollado con ❤️ usando Python y PySide6
