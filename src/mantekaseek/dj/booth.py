from dataclasses import dataclass, field


@dataclass(frozen=True)
class MicChannel:
    channel: str
    active: bool = True
    gain_db: float = 0.0
    karaoke_mode: bool = True
    voice_style: str = "natural"


def _default_mics() -> tuple[MicChannel, MicChannel, MicChannel]:
    return (
        MicChannel(channel="mic_1"),
        MicChannel(channel="mic_2"),
        MicChannel(channel="mic_3"),
    )


@dataclass(frozen=True)
class BoothState:
    mics: tuple[MicChannel, ...] = field(default_factory=_default_mics)
    auto_mix_active: bool = False

    @property
    def auto_mix_button_color(self) -> str:
        return "red" if self.auto_mix_active else "off"

    @property
    def auto_mix_blinking(self) -> bool:
        return self.auto_mix_active


def toggle_auto_mix(state: BoothState) -> BoothState:
    return BoothState(
        mics=state.mics,
        auto_mix_active=not state.auto_mix_active,
    )
