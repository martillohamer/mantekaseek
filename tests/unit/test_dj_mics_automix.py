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
