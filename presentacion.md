# mantekaseek: Presentación y Visión General

## ¿Qué es mantekaseek?

**mantekaseek** es una aplicación personalizada en Python 3.12 orientada a la gestión musical inteligente, diseñada para el flujo de trabajo del **MartilloDJ**. Proporciona un ecosistema integrado que cubre todo el ciclo de vida de la música en un entorno DJ:

- **Descarga y respaldo:** Integración con Soulseek (`slskd`) y YouTube/Spotify (`yt-dlp`) para búsqueda y descarga de audio.
- **Catálogo y persistencia:** Base de datos SQLite para el catálogo musical, con metadatos ID3, información BPM, tonalidad (Camelot/OpenKey), género y más.
- **Análisis musical:** Detección de tonalidad, conversión Camelot ↔ OpenKey, análisis BPM, detección de duplicados basados en firmas normalizadas.
- **Nivelación de ganancia:** Análisis `loudnorm` con `ffmpeg`, cálculo de gan segura con protección de picos (`level_probe.py`, `gain.py`), procesamiento por lotes.
- **Cabina DJ (MartilloDJ):** Control de dos decks con estado BPM/tonalidad, mezclas armónicas sugeridas, automatización de auto-mix, modulación de 3 microfones, grabación de sesiones, pads de sonido y eventos MIDI.
- **Mini Studio (Editor no destructivo):** Línea de tiempo para operaciones de *cut*, *paste* y *merge*; plan de exportación con estimación de duración, tamaño y formato (WAV/MP3/FLAC); comprobación de readiness; soporte de tempo, barras y beats.

### Propósito Principal

Proporcionar a **MartilloDJ** un conjunto de herramientas integradas que reemplaza la necesidad de múltiples aplicaciones desconectadas, ofreciendo desde la búsqueda y descarga de música hasta la preparación de mezclas armónicas, nivelación de ganancia y edición no destructiva para presentaciones en vivo y sesiones grabadas.

### Problema que Resuelve

- Gestión fragmentada de música entre diferentes herramientas sin integración.
- Falta de análisis armónico automático para transiciones DJ fluidas.
- Necesidad de nivelación de ganancia consistente en todas las pistas.
- Dificultad para mantener un catálogo musical organizado con metadatos ricos.
- Falta de flujo de trabajo coherente para edición y exportación de sesiones DJ.

## Arquitectura y Módulos

El proyecto se organiza en los siguientes módulos principales:

| Módulo | Descripción |
|--------|-------------|
| **`core`** | Núcleo: configuración (`config.py`), base de datos SQLite (`database.py`), sistema de logs (`logging.py`). |
| **`library`** | Lógica de biblioteca: metadatos ID3 (`metadata.py`), análisis de clave musical (`keys.py`), nivelación de ganancia (`gain.py`, `level_probe.py`), detección de duplicados (`duplicates.py`). |
| **`downloads`** | Gestión de descargas: cliente Soulseek (`slskd_client.py`), cliente yt-dlp (`ytdlp_client.py`), coordinador de búsqueda (`coordinator.py`), pipeline de planificación (`pipeline.py`). |
| **`dj`** | Cabina DJ: mezclador (`mixer.py`), booth/estado (`booth.py`), controlador MIDI/MartilloDJ (`controller.py`), karaoke MIDI (`midi_karaoke.py`), sound pads (`sound_pads.py`). |
| **`studio`** | Mini Studio editor no destructivo: editor (`editor.py`) con operaciones de línea de tiempo, formato de exportación, estimación de duración/tamaño, comprobación de readiness, formato de barras y beats. |
| **`spotify`** | Integración Spotify: parser de URLs (`parser.py`), resolución en catálogo (`resolver.py`). |
| **`cli`** | Interfaz de línea de comandos con **Typer**: comandos `info`, `db-init`, `spotify-inspect`, `key-convert`, `dj-suggest`, `gain-plan`, `gain-probe`, `booth-status`, `midi-karaoke`, `sound-pad`, `studio-plan`. |

### Flujo de Datos

1. **Descarga:** `SearchCoordinator` intenta primero Soulseek (`slskd_client`), si no encuentra, cae back a `yt-dlp`.
2. **Catálogo:** Pistas insertadas en SQLite con metadatos enriquecidos (BPM, clave, género).
3. **Análisis:** `level_probe.py` parsea salida `loudnorm` de `ffmpeg` → `AudioLevelInfo` → `calculate_safe_gain_db`.
4. **DJ Mix:** `mixer.suggest_next_tracks` y `mixer.select_best_mix_suggestions` usan compatibilidad armónica (`controller.harmonic_compatible`) y coincidencia de BPM.
5. **Mini Studio:** `editor.cut_segment` / `editor.paste_segment` / `editor.merge_tracks` operan sobre `StudioProject`; `build_export_plan` genera el plan de exportación con duración, formato y tamaño estimado.

## Historial y Evolución

El proyecto comenzó con un enfoque en CLI básico y ha evolucionado a través de fases bien definidas, cada una integrando nuevas capacidades:

### Fase 1: Núcleo CLI y Entorno (fase1-nucleo-cli)
- Configuración de entorno WSL/Python 3.12.
- Establecimiento de Git con ramas `dev` y `main`.
- Flujo de fusiones `--no-ff` y commits en castellano.
- Estructura de paquetes `src/mantekaseek` y `tests/`.
- Typer para CLI, SQLite para persistencia básica.

### Fase 2: Entrada de Fuentes (fase2-entrada-spotify)
- Integración Spotify mediante `yt-dlp` y `spotify-parser`.
- Resolución y validación de URLs de Spotify.

### Fase 3: Descargas (fase3-descargas)
- Cliente `slskd` (Soulseek) totalmente implementado.
- Cliente `ytdlp` con ranking de candidatos y selección de fallback.
- `SearchCoordinator` que prioriza Soulseek y cae back a YouTube.
- `DownloadPlan` con bitrate y seguimiento de fallback.

### Fase 4: Biblioteca Musical (fase4-biblioteca)
- Catálogo en SQLite con tabla `tracks`.
- `LibraryTrack` dataclass con BPM, clave musical y género.
- Análisis de clave: conversión Camelot ↔ OpenKey.
- Detección de duplicados basada en firmas normalizadas (ignorando *mixes*).
- Metaetiquetas ID3 (`build_id3_tags`).

### Fase 5: Cabina DJ MartilloDJ (fase5-martillodj)
- `BoothState` con 3 canales de microfono (`mic_1`, `mic_2`, `mic_3`).
- `toggle_auto_mix` con indicador visual "RED" cuando está activo.
- `configure_mic` con `gain_db`, `voice_style`, `karaoke_mode`.
- `summarize_booth_status` para reporte de estado.
- `SoundPadBank` con pads: `airhorn`, `riser`, `impact`, `scratch`.
- `MartilloDJEngine` manejando eventos MIDI: `play_pause`, `cue`, `sync_bpm`.
- Mezclas armónicas via `harmonic_compatible` y sugerencias de BPM.

### Evolución del Mini Studio (fases posteriores)
- **Línea de tiempo (`timeline`):** Operaciones `StudioOperation` con `kind` (cut/paste/merge), `targets`, `start_sec`, `end_sec`, `at_sec`, `repeat`, `crossfade_sec`.
- **Formato de exportación:** `SUPPORTED_EXPORT_FORMATS` = (`wav`, `mp3`, `flac`).
- **Exportación no destructiva:** `build_export_plan` genera `output_path`, estimación de duración y tamaño en MB.
- **Métricas del timeline:** `estimate_timeline_duration`, `estimate_bars`, `estimate_beats`, `format_timeline_span`, `format_timeline_active`, `format_timeline_gap`, `format_timeline_active_pct`, `format_timeline_gap_pct`.
- **Readiness y validación:** `is_ready_to_export` valida tempo (20-300 BPM), formato de salida y operaciones presentes.
- **Reportes completos:** `format_studio_report`, `format_export_summary`, `format_export_diagnostic`, `build_export_summary`.
- **Gestión de proyecto:** `rename_project`, `set_output_format`, `set_project_tempo`, `undo_last_operation`, `clear_operations`.
- **Contador de huecos:** `has_timeline_gaps`, `count_timeline_gaps`, `get_timeline_gap_sec`, `format_timeline_gap`, `get_timeline_gap_ratio`, `format_timeline_gap_pct`.
- **Actividad:** `get_timeline_active_sec`, `format_timeline_active`, `get_timeline_active_ratio`, `format_timeline_active_pct`.

## Estado Actual Verificable

- **Ramas activas:** `dev` (rama actual), `main` (protegida, flujo `--no-ff`).
- **Último commit:** *Merge de `format_export_plan` en dev* (e565192), que integra `build_export_plan` con formateo de planes de exportación.
- **Suite de tests:** **158 tests pasando** (todos los tests unitarios), confirmados con `.venv/bin/pytest`.
- **Linter:** **`ruff` sin advertencias** (`ruff check src tests` pasa limpio).
- **Convenciones:** Mensajes de commit en castellano; nunca *push* directo a `main`; ramas de trabajo siempre desde `dev`; fusiones `--no-ff`.
- **Entorno de ejecución:** Python 3.12.3 en WSL; `.venv/bin/pytest` para tests; `.venv/bin/ruff` para linting.

## Guía Rápida para IA o Desarrollador

### Reglas de Oro del Repositorio

1. **Tests primero:** 158 tests (unitarios e integración); `pytest` en `.venv/bin/pytest`. Todo nuevo código debe tener tests correspondientes.
2. **Linter estricto:** `ruff` con `--select E,F,I,UP,B`; cero advertencias. Ejecutar `.venv/bin/ruff check src tests` antes de commit.
3. **Flujo Git:** Ramas de features desde `dev`; merge `--no-ff` a `main`; commits en castellano; *never* push directo a `main`.
4. **Tipo de Python:** `target-version = "py312"` en `pyproject.toml`; uso de `dataclasses` frozen/slots; type hints completos.
5. **Estructura de carpetas:**
   - `src/mantekaseek/` → paquetes: `core`, `dj`, `downloads`, `library`, `spotify`, `studio`, `cli`.
   - `tests/unit/` → 47 tests unitarios enfocados.
   - `README.md` → presentación principal.
   - `presentacion.md` → visión arquitectónica (este archivo).
   - `HANDOFF.md` → esta guía (a crear/actualizar).

### Entorno de Ejecución

- `.venv/bin/pytest` → ejecuta la suite completa (158 tests, ~2s).
- `.venv/bin/ruff check src tests` → verifica estilo y calidad.
- `.venv/bin/ruff check src tests --select E,F,I,UP,B` → modo estricto.
- Python 3.12.3 requerida (`requires-python = ">=3.12"` en pyproject.toml).
- Dependencias principales: `typer>=0.12`, `pytest>=8.0`, `ruff>=0.6` (opcionales dev).

### Próximos Pasos Recomendados

1. Explorar `tests/` para entender los contratos de prueba esperados.
2. Ejecutar `.venv/bin/pytest --tb=short` para ver el desglose por módulo.
3. Revisar `docs/` (actualmente vacío) para futuras documentación técnica.
4. Familiarizarse con `core/config.py` para perfilado de configuración.
5. Revisar `dj/booth.py` para el estado de la cabina y configuración de microfonos.
6. Revisar `studio/editor.py` para el modelo de línea de tiempo y exportación.
7. Considerar agregar más protocolos (`Protocol`) en `downloads/` y `spotify/` para facilitar testing y mocking.

---
*Documento generado a partir de la inspección en vivo del repositorio `/mnt/c/Users/astur/Desktop/mantekaseek` el 2026-11-21.*