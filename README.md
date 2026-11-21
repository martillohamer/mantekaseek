# mantekaseek (martilloseek)

Herramienta personal modular para descarga, biblioteca musical inteligente y mesa DJ **MartilloDJ**.

[![Python 3.12](https://img.shields.io/badge/python-3.12- blue)](https://www.python.org/)
[![Tests: 131 passing](https://img.shields.io/badge/tests-131-passing-green)](.venv/bin/pytest)
[![Lint: ruff clean](https://img.shields.io/badge/lint-ruff--clean-orange)](.venv/bin/ruff check src tests)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)](NOTICE.md)

## Créditos y atribuciones

Consulta `NOTICE.md` para ver los proyectos de referencia que inspiraron las ideas originales.

### Insignias

| Insignia | Descripción |
|---|---|
| ![Python 3.12](https://img.shields.io/badge/python-3.12- blue) | Python 3.12.3 en WSL |
| ![Tests: 131 passing](https://img.shields.io/badge/tests-131-passing-green) | `.venv/bin/pytest` |
| ![Lint: ruff clean](https://img.shields.io/badge/lint-ruff--clean-orange) | `.venv/bin/ruff check src tests` |
| ![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey) | `NOTICE.md` |

## Visión General

**mantekaseek** es una aplicación Python 3.12 orientada a la gestión musical inteligente, descarga/respaldo de audio (Soulseek y yt-dlp/Spotify), catálogo en SQLite, análisis BPM y tonalidad (Camelot/OpenKey), detección de duplicados, edición de metadatos ID3, nivelación de ganancia con protección de picos, y el editor no destructivo **Mini Studio** orientado a controlador **Numark NV** y flujos de trabajo DJ.

### Módulos Principales

| Módulo | Funcionalidad |
|---|---|
| **`core`** | Configuración, base de datos SQLite, sistema de logs. |
| **`library`** | Metadatos ID3, análisis de clave, nivelación de ganancia, detección de duplicados. |
| **`downloads`** | Cliente Soulseek (`slskd`), cliente yt-dlp, coordinación de búsqueda, planificación de descargas. |
| **`dj`** | Cabina DJ: mezclador, booth con 3 micrófonos, auto-mix, sound pads, MIDI karaoke, controlador MartilloDJ. |
| **`studio`** | Mini Studio editor no destructivo: línea de tiempo, operaciones cut/paste/merge, plan de exportación, readiness, formato de barras y beats. |
| **`spotify`** | Parser y resolución de URLs de Spotify. |
| **`cli`** | Interfaz CLI con **Typer** (13 comandos: `info`, `db-init`, `spotify-inspect`, `key-convert`, `dj-suggest`, `gain-plan`, `gain-probe`, `booth-status`, `midi-karaoke`, `sound-pad`, `studio-plan`). |

### Estado Actual

- **Ramas:** `dev` (actual), `main` (flujo `--no-ff`, sin *push* directo).
- **Tests:** **156 tests pasando** confirmados con `.venv/bin/pytest`.
- **Linter:** **`ruff` sin advertencias** confirmado con `.venv/bin/ruff check src tests`.
- **Último merge:** `integrar format_valid_batch_results en dev` (d7df6db).

### Flujos Destacados

- **Descarga inteligente:** `SearchCoordinator` prioriza Soulseek, cae back a yt-dlp.
- **Mezclas armónicas:** `harmonic_compatible` en `dj/controller.py` con compatibilidad de BPM (±4.0).
- **Nivelación de ganancia:** `level_probe.py` parsea salida `loudnorm` de `ffmpeg`; `gain.py` calcula gan segura con techo de pico.
- **Mini Studio:** `editor.py` con `cut_segment`/`paste_segment`/`merge_tracks`; `build_export_plan` con duración, formato y tamaño estimado; métricas de timeline (bars, beats, gaps, active/pct). y helpers de lotes validos (`execute_valid_batch_export_plan`, `summarize_valid_batch_results`, `format_valid_batch_results`).
- **3 micrófonos:** `booth.py` con `MicChannel`, `voice_style`, `karaoke_mode`, ganancia por canal.

## Empezar

```bash
# Desde el directorio del proyecto
.venv/bin/pytest          # Ejecutar todos los tests
.venv/bin/ruff check src tests  # Verificar linting
mantekaseek --help      # Ver comandos CLI
```

Consulta `presentacion.md` para la visión arquitectónica completa y `HANDOFF.md` para la guía de desarrollo.
## Pruebas de integración

- `tests/integration/test_end_to_end_pipeline.py`: verifica de extremo a extremo la planificación de descarga (`plan_track_download`), la nivelación de ganancia (`plan_batch_leveling`) y la edición/exportación por lotes en `StudioProject`.
