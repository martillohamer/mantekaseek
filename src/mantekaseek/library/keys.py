import re

# Valor Camelot (1..12) para tonalidades mayores (modo B)
_MAJOR_CAMELOT: dict[str, int] = {
    "B": 1,
    "CB": 1,
    "F#": 2,
    "GB": 2,
    "DB": 3,
    "C#": 3,
    "AB": 4,
    "G#": 4,
    "EB": 5,
    "D#": 5,
    "BB": 6,
    "A#": 6,
    "F": 7,
    "E#": 7,
    "C": 8,
    "B#": 8,
    "G": 9,
    "D": 10,
    "A": 11,
    "E": 12,
    "FB": 12,
}

# Valor Camelot (1..12) para tonalidades menores (modo A)
_MINOR_CAMELOT: dict[str, int] = {
    "G#M": 1,
    "ABM": 1,
    "D#M": 2,
    "EBM": 2,
    "A#M": 3,
    "BBM": 3,
    "FM": 4,
    "E#M": 4,
    "CM": 5,
    "GM": 6,
    "DM": 7,
    "AM": 8,
    "EM": 9,
    "FBM": 9,
    "BM": 10,
    "CBM": 10,
    "F#M": 11,
    "GBM": 11,
    "C#M": 12,
    "DBM": 12,
}

_KEY_RE = re.compile(r"^\s*([A-Ga-g])([#b♯♭]?)\s*(m|min|minor)?\s*$")


def _parse_key_camelot_number(musical_key: str) -> tuple[int, bool]:
    match = _KEY_RE.match(musical_key.strip())
    if not match:
        raise ValueError(f"Tonalidad musical no reconocida: {musical_key}")

    note = match.group(1).upper()
    accidental = match.group(2).replace("♯", "#").replace("♭", "b").upper()
    is_minor = bool(match.group(3))

    if is_minor:
        lookup_key = f"{note}{accidental}M"
        camelot_num = _MINOR_CAMELOT.get(lookup_key)
    else:
        lookup_key = f"{note}{accidental}"
        camelot_num = _MAJOR_CAMELOT.get(lookup_key)

    if camelot_num is None:
        raise ValueError(f"Tonalidad musical no soportada: {musical_key}")
    return camelot_num, is_minor


def key_to_camelot(musical_key: str) -> str:
    camelot_num, is_minor = _parse_key_camelot_number(musical_key)
    letter = "A" if is_minor else "B"
    return f"{camelot_num}{letter}"


def key_to_open_key(musical_key: str) -> str:
    camelot_num, is_minor = _parse_key_camelot_number(musical_key)
    # En OpenKey: 8 en Camelot (C mayor / Am menor) equivale a 1d / 1m
    open_num = ((camelot_num - 8) % 12) + 1
    suffix = "m" if is_minor else "d"
    return f"{open_num}{suffix}"
