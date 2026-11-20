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
    recording_active: bool = False
    session_label: str | None = None

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
        recording_active=state.recording_active,
        session_label=state.session_label,
    )


def configure_mic(
    state: BoothState,
    channel: str,
    voice_style: str | None = None,
    gain_db: float | None = None,
    karaoke_mode: bool | None = None,
    active: bool | None = None,
) -> BoothState:
    found = False
    updated_mics: list[MicChannel] = []
    for mic in state.mics:
        if mic.channel == channel:
            found = True
            updated_mics.append(
                MicChannel(
                    channel=mic.channel,
                    active=mic.active if active is None else active,
                    gain_db=mic.gain_db if gain_db is None else gain_db,
                    karaoke_mode=mic.karaoke_mode if karaoke_mode is None else karaoke_mode,
                    voice_style=mic.voice_style if voice_style is None else voice_style,
                )
            )
        else:
            updated_mics.append(mic)
    if not found:
        msg = f"Canal de microfono desconocido: {channel}"
        raise ValueError(msg)
    return BoothState(
        mics=tuple(updated_mics),
        auto_mix_active=state.auto_mix_active,
        recording_active=state.recording_active,
        session_label=state.session_label,
    )


def toggle_session_recording(
    state: BoothState,
    session_label: str | None = None,
) -> BoothState:
    next_active = not state.recording_active
    next_label = session_label if next_active else None
    return BoothState(
        mics=state.mics,
        auto_mix_active=state.auto_mix_active,
        recording_active=next_active,
        session_label=next_label,
    )
