# mantekaseek: HANDOFF Guide

## Propósito

Esta guía tiene como objetivo permitir que cualquier desarrollador o agente IA reanude el trabajo sobre **mantekaseek** desde cero, en cualquier máquina, sin necesidad de conocimiento previo profundo del códigobase. Cubre el entorno, flujo de trabajo, convenciones y pasos para retomar la productividad.

---

## Entorno de Ejecución

### Python y Entorno Virtual

- **Versión:** Python 3.12.3
- **Entorno virtual:** `.venv/` (creado con `python -m venv .venv`)
- **Activar entorno:**
  ```bash
  source .venv/bin/activate
  ```
- **Herramientas clave en `.venv/bin/`:**
  - `pytest` — Ejecutar suite de tests (131 tests unitarios)
  - `ruff` — Linter y formateador (`ruff check` y `ruff format`)
  - `python` — Interpretador Python 3.12

### Dependencias

- **Principal:** `typer>=0.12`
- **Desarrollo (opcional):** `pytest>=8.0`, `ruff>=0.6`
- Definidas en `pyproject.toml` bajo `[project.optional-dependencies] dev`.

### Comandos Útiles

```bash
# Desde el directorio del proyecto (sin activar venv explícitamente):
.venv/bin/pytest              # Ejecutar todos los tests unitarios
.venv/bin/pytest --tb=short   # Con tracebacks acortados
.venv/bin/ruff check src tests  # Linter: verificar código fuente y tests
.venv/bin/ruff check src tests --select E,F,I,UP,B  # Modo estricto
mantekaseek --help          # Ver comandos CLI disponibles
```

---

## Flujo de Trabajo Git

### Ramas y Convenciones

| Rama | Propósito |
|---|---|
| `main` | Rama protegida. Nunca hacer *push* directo. Solo fusiones `--no-ff` desde `dev`. |
| `dev` | Rama de desarrollo principal. Todas las ramas de features se crean desde aquí. |
| `feature/*` | Ramas de trabajo para nuevas funcionalidades. Se crean desde `dev`. |

### Comandos Git Recomendados

```bash
# Ver estado y ramas
git status
git branch -a
git log --oneline -15 --graph

# Crear y trabajar en una nueva feature
git checkout dev
git checkout -b feature/nueva-funcionalidad
# ... hacer cambios ...
git add .
git commit -m "feat: descripcion de la funcionalidad en castellano"
git push origin feature/nueva-funcionalidad

# Fusionar a dev (luego de code review / tests)
git checkout dev
git merge --no-ff feature/nueva-funcionalidad
git push origin dev

# Fusionar a main (solo mantenedor, con tag/version bump)
git checkout main
git merge --no-ff dev
git push origin main
```

### Mensajes de Commit (en castellano)

- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Documentación (md, comentarios, etc.)
- `style`: Formato, PEP 8, sin funcionalidad nueva
- `refactor`: Refactorización sin cambio de comportamiento
- `test`: Añadir o mejorar tests
- `chore`: Tareas auxiliares (configuración, dependencias, etc.)

**Nunca** hacer *push* directo a `main`. Siempre flujo `feature` → `dev` → `main` con `--no-ff`.

---

## Estructura del Proyecto

```
/mnt/c/Users/astur/Desktop/mantekaseek/
├── .venv/                      # Entorno virtual Python
├── .git/                       # Repositorio Git
├── .github/                    # (Posible futuro) flujos CI
├── docs/                       # Documentación técnica (actualmente vacío)
│   └── ...
├── NOTICE.md                   # Atribuciones y licencias
├── pyproject.toml              # Configuración: dependencies, pytest, ruff
├── README.md                   # Presentación principal del proyecto
├── presentacion.md             # Visión arquitectónica completa (nuevo)
├── src/mantekaseek/            # Código fuente principal
│   ├── __init__.py             # Paquete: __version__ = "0.1.0"
│   ├── core/                   # Núcleo: config, database, logging
│   │   ├── config.py           # AppConfig y load_config
│   │   ├── database.py         # Database class (SQLite)
│   │   └── logging.py          # setup_logging
│   ├── dj/                     # Cabina DJ y equipos
│   │   ├── booth.py            # BoothState, 3 mics, auto-mix, sound pads
│   │   ├── controller.py       # DeckState, MidiControlEvent, MartilloDJEngine
│   │   ├── mixer.py            # TrackCandidateDJ, suggest_next_tracks
│   │   ├── midi_karaoke.py     # MIDI parsing, Karaoke track loading
│   │   └── sound_pads.py       # SoundPadBank, trigger_sound_pad
│   ├── downloads/              # Descarga y búsqueda de audio
│   │   ├── coordinator.py      # SearchCoordinator (slskd → yt-dlp fallback)
│   │   ├── pipeline.py         # plan_track_download (slskd + youtube fallback)
│   │   ├── ranking.py          # rank_candidates, effective_output_bitrate
│   │   ├── slskd_client.py     # SlskdClient, búsquedas Soulseek
│   │   ├── ytdlp_client.py     # YtdlpSearcher, búsquedas YouTube/Spotify
│   │   └── transcode.py        # (posible futuro) transcodificación
│   ├── library/                # Lógica de biblioteca musical
│   │   ├── metadata.py         # build_id3_tags
│   │   ├── keys.py             # key_to_camelot, key_to_open_key
│   │   ├── gain.py             # AudioLevelInfo, calculate_safe_gain_db
│   │   ├── level_probe.py      # parse_loudnorm_output, plan_gain_from_loudnorm
│   │   └── duplicates.py       # find_duplicates, normalize_track_signature
│   ├── spotify/                # Integración Spotify
│   │   ├── parser.py           # parse_spotify_url, SpotifyTarget
│   │   └── resolver.py         # resolve_spotify_target, SpotifyCatalog
│   └── studio/                 # Mini Studio editor no destructivo
│       └── editor.py           # StudioProject, StudioOperation, timeline ops
│           └── (todas las funciones de formato, estimación, readiness)
├── tests/
│   ├── unit/                   # 47 tests unitarios
│   │   ├── test_cli.py
│   │   ├── test_core.py
│   │   ├── test_dj_controller.py
│   │   ├── test_dj_mics_automix.py
│   │   ├── test_dj_midi_karaoke.py
│   │   ├── test_dj_mixer.py
│   │   ├── test_dj_sound_pads.py
│   │   ├── test_downloads_pipeline.py
│   │   ├── test_downloads_ranking.py
│   │   ├── test_downloads_transcode.py
│   │   ├── test_ffmpeg_level_parser.py
│   │   ├── test_library_gain.py
│   │   ├── test_library_keys_and_dupes.py
│   │   ├── test_library_metadata.py
│   │   ├── test_search_coordinator.py
│   │   ├── test_slskd_client.py
│   │   ├── test_spotify.py
│   │   ├── test_spotify_resolver.py
│   │   └── test_studio_timeline.py
│   └── ...
└── README.md                   # ( duplicado/overlap - mantener consistencia )
```

---

## Reanudar el Trabajo desde Cero

### 1. Clonar el Repositorio

```bash
git clone https://github.com/martillohamer/mantekaseek.git
cd mantekaseek
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"  # instala typer, pytest, ruff y dev deps
```

### 2. Verificar el Estado

```bash
git status                    # Debe estar limpio
git branch -a                 # Ver ramas: dev, main, feature/*
.venv/bin/pytest              # Todos los tests deben pasar (131)
.venv/bin/ruff check src tests  # Sin advertencias
```

### 3. Crear una Nueva Feature Branch

```bash
git checkout dev
git checkout -b feature/nombre-caracteristica
# ... implementar ...
git add .
git commit -m "feat: nombre de la característica en castellano"
git push origin feature/nombre-caracteristica
```

### 4. Antes de Fusionar a `dev`

```bash
.venv/bin/pytest              # Verificar que todos los tests pasan
.venv/bin/ruff check src tests  # Verificar linting sin advertencias
# Si hay problemas, corregir antes de commit/push
```

### 5. Fusionar a `dev` (flujo --no-ff)

```bash
git checkout dev
git merge --no-ff feature/nombre-caracteristica
git push origin dev
# Luego, el mantenedor fusiona dev a main con --no-ff
```

---

## Convenciones y Golden Rules

### Python

- **Type hints completos:** Toda función debe tener annotations de tipo donde sea posible.
- **Dataclasses frozen/slots:** Usar `frozen=True` y `slots=True` para dataclasses inmutables (pattern consistente en todo el código).
- **Target Python:** `py312` en `pyproject.toml`; usar características compatibles con Python 3.12.
- **Selección ruff:** `--select E,F,I,UP,B` (errores, fonts, imports, unused, best practices).

### Tests

- **131 tests unitarios** en `tests/unit/`.
- Usar `.venv/bin/pytest` para ejecutar.
- Los tests deben pasar limpio antes de cualquier commit.
- Agregar tests para nueva funcionalidad; no modificar tests existentes sin necesidad.

### Estilo de Código

- `ruff check src tests` debe salir limpio (zero warnings).
- Línea máxima: 100 caracteres (`line-length = 100` en pyproject.toml).
- Formato de fecha en logs: `%Y-%m-%d %H:%M:%S`.
- Commits en castellano.
- Sin *push* directo a `main`.

---

## Módulos Clave y Puntos de Entrada

### CLI (`src/mantekaseek/cli/app.py`)

13 comandos Typer disponibles:

| Comando | Descripción |
|---|---|
| `info` | Muestra versión y configuración cargada. |
| `db-init` | Inicializa SQLite y sistema de logs. |
| `spotify-inspect` | Valida y muestra tipo/ID de URL de Spotify. |
| `key-convert` | Convierte tonalidad a Camelot y OpenKey. |
| `dj-suggest` | Sugerencias armónicas y BPM para la siguiente mezcla. |
| `gain-plan` | Calcula ganancia segura dado LUFS y pico. |
| `gain-probe` | Plan de ganancia desde salida loudnorm de ffmpeg. |
| `booth-status` | Estado completo de la cabina (mics, auto-mix, rec, pads). |
| `midi-karaoke` | Carga y muestra información de un track MIDI karaoke. |
| `sound-pad` | Dispara un sound pad y muestra su nivel. |
| `studio-plan` | Crea un proyecto Mini Studio y muestra el plan de exportación. |

### Mini Studio (`src/mantekaseek/studio/editor.py`)

Funciones clave para editor no destructivo:

- `cut_segment(project, source_id, start_sec, end_sec)` — Cortar segmento.
- `paste_segment(project, source_id, at_sec, repeat=1)` — Pegar segmento.
- `merge_tracks(project, track_ids, crossfade_sec=0.0)` — Fusionar pistas.
- `build_export_plan(project, output_dir)` — Generar plan de exportación dict.
- `format_export_plan(plan)` — Formatear plan a string legible.
- `is_ready_to_export(project)` — Verificar readiness (tempo + operations + format).
- `has_timeline_gaps(project)` — Detectar huecos en la línea de tiempo.
- `format_timeline_active_pct(project)` — Porcentaje de tiempo activo.
- `format_timeline_gap_pct(project)` — Porcentaje de huecos.
- `format_studio_report(project)` — Reporte completo del proyecto.

### Mezclas Armónicas (`src/mantekaseek/dj/controller.py`)

- `harmonic_compatible(code_a, code_b)` — Verificar compatibilidad entre dos tonalidades Camelot.
- `MartilloDJEngine` — Motor de estado de dos decks (A y B), eventos MIDI (play_pause, cue, sync_bpm).
- `DeckState` — Estado individual por deck (BPM, clave, playing, cue_ms).

### Búsqueda y Descarga (`src/mantekaseek/downloads/`)

- `SearchCoordinator` — Intenta Soulseek primero, cae back a yt-dlp.
- `SlskdClient` — Cliente API Soulseek (búsqueda por artista/título, ranking por velocidad + bitrate).
- `YtdlpSearcher` — Cliente yt-dlp con búsqueda `ytsearch{limit}` y ranking de candidatos.
- `plan_track_download` — Planificar descarga con fallback coordinado.

### Nivelación de Ganancia (`src/mantekaseek/library/`)

- `calculate_safe_gain_db(info, target_lufs, max_peak_dbfs)` — Ganancia segura con protección de pico.
- `plan_batch_leveling(tracks, target_lufs, max_peak_dbfs)` — Procesamiento por lotes.
- `parse_loudnorm_output(track_id, raw_output)` — Parsear JSON de ffmpeg loudnorm.
- `analyze_audio_file_gain(track_id, audio_path, runner)` — Analizar archivo completo con ffmpeg.

---

## Solución de Problemas Comunes

### Tests Fallan

```bash
.venv/bin/pytest --tb=long  # Ver tracebacks completos
# Verificar que las dependencias estén instaladas:
pip install -e ".[dev]"
```

### Ruff Advertencias

```bash
.venv/bin/ruff check src tests --select E,F,I,UP,B  # Modo estricto
.venv/bin/ruff format src tests  # Auto-formatear (si está disponible)
```

### No se Puede Hacer Push a `main`

```bash
# Flujo correcto:
git checkout dev
git merge --no-ff feature/x
git push origin dev
# El mantenedor luego hará:
git checkout main
git merge --no-ff dev
git push origin main
```

### Entorno WSL

- Los rutas mezcladas Windows/WSL suelen funcionar; usar rutas absolutas o `wslpath` para convertir.
- Los comandos `python`, `pytest`, `ruff` deben invocarse desde `.venv/bin/` o después de `source .venv/bin/activate`.

---

## Próximos Pasos Recomendados

1. **Explorar `tests/unit/`** para entender los contratos de prueba esperados para cada módulo.
2. **Revisar `core/config.py`** para perfilado y anulación de configuración por archivo TOML.
3. **Familiarizarse con `dj/booth.py`** para el estado de la cabina y configuración de 3 microfonos.
4. **Revisar `studio/editor.py`** para el modelo de línea de tiempo y funciones de exportación.
5. **Considerar agregar protocolos** (`Protocol` de typing) en `downloads/` y `spotify/` para facilitar testing y mocking.
6. **Explorar `docs/`** (actualmente vacío) para documentación técnica futura.
7. **Añadir más tests** de integración para flujos end-to-end (descarga → análisis → catálogo → exportación).
8. **Considerar** agregar soporte de configuración `.env` o archivo TOML adicional para credenciales de Soulseek.

---
*Guía generada el 2026-11-21 basada en la inspección completa del repositorio en `/mnt/c/Users/astur/Desktop/mantekaseek`.*