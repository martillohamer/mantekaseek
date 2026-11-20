from mantekaseek.dj.controller import (
    DeckState,
    MartilloDJEngine,
    MidiControlEvent,
    harmonic_compatible,
)


def test_deck_play_toggle_and_bpm_sync() -> None:
    engine = MartilloDJEngine()
    engine.load_track("A", title="Track A", bpm=126.0, camelot="8A")
    engine.load_track("B", title="Track B", bpm=128.0, camelot="8A")

    engine.handle_event(MidiControlEvent(deck="A", control="play_pause", value=127))
    assert engine.decks["A"].playing is True

    engine.handle_event(MidiControlEvent(deck="A", control="play_pause", value=127))
    assert engine.decks["A"].playing is False

    engine.handle_event(MidiControlEvent(deck="B", control="sync_bpm", value=127))
    assert engine.decks["B"].current_bpm == 126.0


def test_harmonic_compatibility_camelot() -> None:
    assert harmonic_compatible("8A", "8A") is True
    assert harmonic_compatible("8A", "9A") is True
    assert harmonic_compatible("12A", "1A") is True
    assert harmonic_compatible("8A", "8B") is True
    assert harmonic_compatible("8A", "2B") is False
    assert isinstance(DeckState(deck_id="A"), DeckState)
