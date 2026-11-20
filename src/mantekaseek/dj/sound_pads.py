from dataclasses import dataclass, field

DEFAULT_SOUND_PADS: tuple[str, ...] = ("airhorn", "riser", "impact", "scratch")


def _default_pad_levels() -> dict[str, float]:
    return {pad: 0.0 for pad in DEFAULT_SOUND_PADS}


@dataclass(frozen=True)
class SoundPadBank:
    pad_levels_db: dict[str, float] = field(default_factory=_default_pad_levels)
    last_triggered: str | None = None


def trigger_sound_pad(
    bank: SoundPadBank,
    pad_name: str,
    level_db: float | None = None,
) -> SoundPadBank:
    updated_levels = dict(bank.pad_levels_db)
    current_level = updated_levels.get(pad_name, 0.0)
    updated_levels[pad_name] = current_level if level_db is None else level_db
    return SoundPadBank(
        pad_levels_db=updated_levels,
        last_triggered=pad_name,
    )
