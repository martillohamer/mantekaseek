from mantekaseek.library.gain import AudioLevelInfo
from mantekaseek.library.level_probe import parse_loudnorm_output


def test_parse_loudnorm_output_extracts_lufs_and_peak() -> None:
    sample_output = """
    [Parsed_loudnorm_0 @ 0x55a1]
    {
        "input_i" : "-18.50",
        "input_tp" : "-2.30",
        "input_lra" : "7.40",
        "input_thresh" : "-28.90",
        "output_i" : "-14.00",
        "output_tp" : "-1.00",
        "target_offset" : "0.00"
    }
    """
    info = parse_loudnorm_output(track_id="pista_01", raw_output=sample_output)

    assert isinstance(info, AudioLevelInfo)
    assert info.track_id == "pista_01"
    assert info.integrated_lufs == -18.5
    assert info.peak_dbfs == -2.3
