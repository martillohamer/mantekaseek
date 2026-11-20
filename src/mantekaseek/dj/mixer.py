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
        is_exact_key = cand.camelot.strip().upper() == current_camelot.strip().upper()
        exact_key_bonus = 0.0 if is_exact_key else 0.5
        compatible.append((bpm_diff + exact_key_bonus, cand))

    compatible.sort(key=lambda item: item[0])
    return [item[1] for item in compatible]


@dataclass(frozen=True)
class MixSuggestion:
    track_id: str
    bpm_diff: float
    harmonic_score: float


def rank_mix_suggestions(suggestions: list[MixSuggestion]) -> list[MixSuggestion]:
    return sorted(
        suggestions,
        key=lambda item: (-item.harmonic_score, item.bpm_diff),
    )


def filter_mix_suggestions(
    suggestions: list[MixSuggestion],
    min_harmonic_score: float = 0.5,
    max_bpm_diff: float = 4.0,
) -> list[MixSuggestion]:
    bpm_limit = max(0.0, max_bpm_diff)
    return [
        item
        for item in suggestions
        if item.harmonic_score >= min_harmonic_score and item.bpm_diff <= bpm_limit
    ]


def select_best_mix_suggestions(
    suggestions: list[MixSuggestion],
    min_harmonic_score: float = 0.5,
    max_bpm_diff: float = 4.0,
    limit: int | None = None,
) -> list[MixSuggestion]:
    filtered = filter_mix_suggestions(
        suggestions,
        min_harmonic_score=min_harmonic_score,
        max_bpm_diff=max_bpm_diff,
    )
    ranked = rank_mix_suggestions(filtered)
    if limit is not None and limit >= 0:
        return ranked[:limit]
    return ranked
