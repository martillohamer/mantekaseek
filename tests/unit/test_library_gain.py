from mantekaseek.library.gain import (
    AudioLevelInfo,
    calculate_safe_gain_db,
    plan_batch_leveling,
)


def test_calculate_safe_gain_raises_quiet_and_lowers_loud_tracks() -> None:
    quiet = AudioLevelInfo(track_id="1", integrated_lufs=-20.0, peak_dbfs=-6.0)
    loud = AudioLevelInfo(track_id="2", integrated_lufs=-8.0, peak_dbfs=-0.2)

    assert calculate_safe_gain_db(quiet, target_lufs=-14.0, max_peak_dbfs=-1.0) == 6.0
    assert calculate_safe_gain_db(loud, target_lufs=-14.0, max_peak_dbfs=-1.0) == -6.0


def test_calculate_safe_gain_prevents_clipping() -> None:
    quiet_high_peak = AudioLevelInfo(track_id="3", integrated_lufs=-22.0, peak_dbfs=-2.0)
    # Subir +8 dB llevaria el pico a +6.0 dBFS; debe limitarse a +1.0 dB para no pasar de -1.0 dBFS
    assert calculate_safe_gain_db(quiet_high_peak, target_lufs=-14.0, max_peak_dbfs=-1.0) == 1.0


def test_plan_batch_leveling_aligns_tracks() -> None:
    tracks = [
        AudioLevelInfo(track_id="a", integrated_lufs=-18.0, peak_dbfs=-4.0),
        AudioLevelInfo(track_id="b", integrated_lufs=-10.0, peak_dbfs=-1.5),
    ]
    plans = plan_batch_leveling(tracks, target_lufs=-14.0, max_peak_dbfs=-1.0)
    assert plans["a"].gain_db == 3.0
    assert plans["b"].gain_db == -4.0
