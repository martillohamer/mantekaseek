from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AudioLevelInfo:
    track_id: str
    integrated_lufs: float
    peak_dbfs: float


@dataclass(slots=True, frozen=True)
class GainPlan:
    track_id: str
    gain_db: float
    projected_peak_dbfs: float


def calculate_safe_gain_db(
    info: AudioLevelInfo,
    target_lufs: float = -14.0,
    max_peak_dbfs: float = -1.0,
) -> float:
    desired_gain = target_lufs - info.integrated_lufs
    peak_headroom = max_peak_dbfs - info.peak_dbfs
    safe_gain = min(desired_gain, peak_headroom)
    return round(safe_gain, 1)


def plan_batch_leveling(
    tracks: list[AudioLevelInfo],
    target_lufs: float = -14.0,
    max_peak_dbfs: float = -1.0,
) -> dict[str, GainPlan]:
    plans: dict[str, GainPlan] = {}
    for track in tracks:
        gain_db = calculate_safe_gain_db(
            track,
            target_lufs=target_lufs,
            max_peak_dbfs=max_peak_dbfs,
        )
        projected_peak = round(track.peak_dbfs + gain_db, 1)
        plans[track.track_id] = GainPlan(
            track_id=track.track_id,
            gain_db=gain_db,
            projected_peak_dbfs=projected_peak,
        )
    return plans
