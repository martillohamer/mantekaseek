from mantekaseek.dj.booth import BoothState, toggle_auto_mix


def test_three_mics_and_blinking_red_automix_button() -> None:
    booth = BoothState()
    assert len(booth.mics) == 3
    assert [m.channel for m in booth.mics] == ["mic_1", "mic_2", "mic_3"]
    assert booth.auto_mix_active is False
    assert booth.auto_mix_button_color == "off"
    assert booth.auto_mix_blinking is False

    active_booth = toggle_auto_mix(booth)
    assert active_booth.auto_mix_active is True
    assert active_booth.auto_mix_button_color == "red"
    assert active_booth.auto_mix_blinking is True


def test_configure_mic_voice_style_and_karaoke() -> None:
    from mantekaseek.dj.booth import BoothState, configure_mic

    booth = BoothState()
    updated = configure_mic(
        booth,
        channel="mic_2",
        voice_style="robot",
        gain_db=3.5,
        karaoke_mode=True,
    )
    mics_by_channel = {m.channel: m for m in updated.mics}
    assert mics_by_channel["mic_2"].voice_style == "robot"
    assert mics_by_channel["mic_2"].gain_db == 3.5
    assert mics_by_channel["mic_2"].karaoke_mode is True
    assert mics_by_channel["mic_1"].voice_style == "natural"


def test_toggle_session_recording_in_booth() -> None:
    from mantekaseek.dj.booth import BoothState, toggle_session_recording

    booth = BoothState()
    assert booth.recording_active is False
    assert booth.session_label is None

    rec_booth = toggle_session_recording(booth, session_label="fiesta_karaoke_01")
    assert rec_booth.recording_active is True
    assert rec_booth.session_label == "fiesta_karaoke_01"

    stopped_booth = toggle_session_recording(rec_booth)
    assert stopped_booth.recording_active is False


def test_summarize_booth_status() -> None:
    from mantekaseek.dj.booth import (
        BoothState,
        configure_mic,
        summarize_booth_status,
        toggle_auto_mix,
        toggle_session_recording,
    )
    from mantekaseek.dj.sound_pads import SoundPadBank, trigger_sound_pad

    booth = BoothState()
    booth = configure_mic(booth, channel="mic_1", voice_style="echo")
    booth = toggle_auto_mix(booth)
    booth = toggle_session_recording(booth, session_label="noche_trio")
    pads = trigger_sound_pad(SoundPadBank(), pad_name="airhorn", level_db=-2.0)

    summary = summarize_booth_status(booth, sound_pads=pads)
    assert "mic_1:echo" in summary
    assert "automix=RED_BLINK" in summary
    assert "rec=noche_trio" in summary
    assert "pad=airhorn" in summary


def test_cli_booth_status_command() -> None:
    from typer.testing import CliRunner

    from mantekaseek.cli.app import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "booth-status",
            "--auto-mix",
            "--record-label",
            "karaoke_viernes",
            "--pad",
            "riser",
        ],
    )
    assert result.exit_code == 0
    assert "automix=RED_BLINK" in result.stdout
    assert "rec=karaoke_viernes" in result.stdout
    assert "pad=riser" in result.stdout


def test_plan_automix_transition_respects_auto_mix_state() -> None:
    from mantekaseek.dj.booth import BoothState, plan_automix_transition, toggle_auto_mix
    from mantekaseek.dj.mixer import MixSuggestion

    candidates = [
        MixSuggestion(track_id="t_baja", bpm_diff=0.5, harmonic_score=0.2),
        MixSuggestion(track_id="t_top", bpm_diff=1.0, harmonic_score=0.95),
    ]
    off_booth = BoothState()
    assert plan_automix_transition(off_booth, candidates) is None

    on_booth = toggle_auto_mix(off_booth)
    chosen = plan_automix_transition(on_booth, candidates)
    assert chosen is not None
    assert chosen.track_id == "t_top"
