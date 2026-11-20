import json
import re

from mantekaseek.library.gain import AudioLevelInfo, GainPlan, plan_batch_leveling

_JSON_BLOCK_RE = re.compile(r"\{[^{}]*\}", re.DOTALL)


def parse_loudnorm_output(track_id: str, raw_output: str) -> AudioLevelInfo:
    matches = _JSON_BLOCK_RE.findall(raw_output)
    data: dict[str, object] | None = None
    for block in reversed(matches):
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and "input_i" in parsed and "input_tp" in parsed:
            data = parsed
            break

    if data is None:
        msg = "No se encontraron metricas loudnorm (input_i / input_tp) en la salida."
        raise ValueError(msg)

    try:
        integrated_lufs = float(str(data["input_i"]).strip())
        peak_dbfs = float(str(data["input_tp"]).strip())
    except (TypeError, ValueError) as exc:
        msg = "Valores invalidos para input_i o input_tp en la salida loudnorm."
        raise ValueError(msg) from exc

    return AudioLevelInfo(
        track_id=track_id,
        integrated_lufs=round(integrated_lufs, 1),
        peak_dbfs=round(peak_dbfs, 1),
    )


def plan_gain_from_loudnorm(
    track_id: str,
    raw_output: str,
    target_lufs: float = -14.0,
    max_peak_dbfs: float = -1.0,
) -> GainPlan:
    info = parse_loudnorm_output(track_id=track_id, raw_output=raw_output)
    plans = plan_batch_leveling(
        [info],
        target_lufs=target_lufs,
        max_peak_dbfs=max_peak_dbfs,
    )
    return plans[track_id]
