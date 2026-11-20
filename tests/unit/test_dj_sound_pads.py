from mantekaseek.dj.sound_pads import SoundPadBank, trigger_sound_pad


def test_trigger_sound_pad_records_last_triggered_and_level() -> None:
    bank = SoundPadBank()
    assert bank.last_triggered is None

    updated = trigger_sound_pad(bank, pad_name="airhorn", level_db=-1.5)
    assert updated.last_triggered == "airhorn"
    assert updated.pad_levels_db["airhorn"] == -1.5
