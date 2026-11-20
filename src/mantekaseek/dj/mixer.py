from dataclasses import dataclass

from mantekaseek.dj.controller import harmonic_compatible


@dataclass(slots=True, frozen=True)
class TrackCandidateDJ:
    track_id: str
    title: str
    bpm: float
    camelot: str


def suggest_next_tracks(
    current_bpm: float,
    current_camelot: str,
    candidates: list[TrackCandidateDJ],
    max_bpm_delta: float = 4.0,
) -> list[TrackCandidateDJ]:
    compatible: list[tuple[float, TrackCandidateDJ]] = []
    for cand in candidates:
        bpm_diff = abs(cand.bpm - current_bpm)
        if bpm_diff > max_bpm_delta:
            continue
        if not harmonic_compatible(current_camelot, cand.camelot):
            continue
        exact_key_bonus = 0.0 if cand.camelot.strip().upper() == current_camelot.strip().upper() else 0.5
        compatible.append((bpm_diff + exact_key_bonus, cand))

    compatible.sort(key=lambda item: item[0])
    return [item[1] for item in compatible]
