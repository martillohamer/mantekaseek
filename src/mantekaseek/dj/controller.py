import re
from dataclasses import dataclass, field

_CAMELOT_RE = re.compile(r"^([1-9]|1[0-2])([AB])$")


def _parse_camelot(code: str) -> tuple[int, str]:
    cleaned = code.strip().upper()
    match = _CAMELOT_RE.match(cleaned)
    if not match:
        raise ValueError(f"Codigo Camelot no valido: {code}")
    return int(match.group(1)), match.group(2)


def harmonic_compatible(code_a: str, code_b: str) -> bool:
    num_a, mode_a = _parse_camelot(code_a)
    num_b, mode_b = _parse_camelot(code_b)

    if num_a == num_b and mode_a == mode_b:
        return True
    if mode_a == mode_b:
        diff = abs(num_a - num_b)
        if diff in (1, 11):
            return True
    if num_a == num_b and mode_a != mode_b:
        return True
    return False


@dataclass(slots=True)
class DeckState:
    deck_id: str
    title: str | None = None
    bpm: float | None = None
    current_bpm: float | None = None
    camelot: str | None = None
    playing: bool = False
    cue_ms: int = 0


@dataclass(slots=True, frozen=True)
class MidiControlEvent:
    deck: str
    control: str
    value: int = 127
    channel: int = 1


@dataclass(slots=True)
class MartilloDJEngine:
    decks: dict[str, DeckState] = field(
        default_factory=lambda: {"A": DeckState("A"), "B": DeckState("B")}
    )

    def load_track(
        self,
        deck_id: str,
        title: str,
        bpm: float,
        camelot: str | None = None,
    ) -> None:
        key = deck_id.strip().upper()
        if key not in self.decks:
            self.decks[key] = DeckState(deck_id=key)
        deck = self.decks[key]
        deck.title = title
        deck.bpm = bpm
        deck.current_bpm = bpm
        deck.camelot = camelot.strip().upper() if camelot else None
        deck.playing = False

    def handle_event(self, event: MidiControlEvent) -> None:
        deck_key = event.deck.strip().upper()
        if deck_key not in self.decks:
            raise KeyError(f"Deck no registrado: {event.deck}")
        deck = self.decks[deck_key]

        if event.control == "play_pause" and event.value > 0:
            deck.playing = not deck.playing
        elif event.control == "cue" and event.value > 0:
            deck.playing = False
        elif event.control == "sync_bpm" and event.value > 0:
            other_key = "B" if deck_key == "A" else "A"
            other_deck = self.decks.get(other_key)
            if other_deck and other_deck.current_bpm is not None:
                deck.current_bpm = other_deck.current_bpm
