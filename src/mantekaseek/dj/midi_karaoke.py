from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MidiNoteEvent:
    delta_ticks: int
    channel: int
    note: int
    velocity: int


@dataclass(frozen=True)
class MidiKaraokeTrack:
    title: str
    path: Path
    ticks_per_beat: int
    karaoke_enabled: bool
    notes: tuple[MidiNoteEvent, ...]


def _read_vlq(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    pos = offset
    while pos < len(data):
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return value, pos
    msg = "Secuencia VLQ incompleta en archivo MIDI"
    raise ValueError(msg)


def _parse_track_notes(track_data: bytes) -> list[MidiNoteEvent]:
    notes: list[MidiNoteEvent] = []
    pos = 0
    running_status: int | None = None

    while pos < len(track_data):
        delta, pos = _read_vlq(track_data, pos)
        if pos >= len(track_data):
            break

        status_byte = track_data[pos]
        if status_byte >= 0x80:
            pos += 1
            if status_byte < 0xF0:
                running_status = status_byte
        elif running_status is not None:
            status_byte = running_status
        else:
            msg = f"Byte de estado MIDI invalido en posicion {pos}"
            raise ValueError(msg)

        if status_byte == 0xFF:
            if pos >= len(track_data):
                break
            _meta_type = track_data[pos]
            pos += 1
            meta_len, pos = _read_vlq(track_data, pos)
            pos += meta_len
            continue

        if status_byte in (0xF0, 0xF7):
            sysex_len, pos = _read_vlq(track_data, pos)
            pos += sysex_len
            continue

        msg_type = status_byte & 0xF0
        channel = status_byte & 0x0F

        if msg_type in (0xC0, 0xD0):
            pos += 1
        else:
            if pos + 1 >= len(track_data):
                break
            data1 = track_data[pos]
            data2 = track_data[pos + 1]
            pos += 2
            if msg_type == 0x90 and data2 > 0:
                notes.append(
                    MidiNoteEvent(
                        delta_ticks=delta,
                        channel=channel,
                        note=data1,
                        velocity=data2,
                    )
                )

    return notes


def load_midi_karaoke_track(
    midi_path: str | Path,
    karaoke_enabled: bool = True,
) -> MidiKaraokeTrack:
    resolved = Path(midi_path)
    raw = resolved.read_bytes()
    if len(raw) < 14 or raw[:4] != b"MThd":
        msg = f"Archivo MIDI invalido o cabecera MThd ausente: {resolved}"
        raise ValueError(msg)

    header_len = int.from_bytes(raw[4:8], "big")
    ticks_per_beat = int.from_bytes(raw[12:14], "big")
    pos = 8 + header_len

    all_notes: list[MidiNoteEvent] = []
    while pos + 8 <= len(raw):
        chunk_id = raw[pos : pos + 4]
        chunk_len = int.from_bytes(raw[pos + 4 : pos + 8], "big")
        chunk_start = pos + 8
        chunk_end = chunk_start + chunk_len
        if chunk_end > len(raw):
            break
        if chunk_id == b"MTrk":
            all_notes.extend(_parse_track_notes(raw[chunk_start:chunk_end]))
        pos = chunk_end

    return MidiKaraokeTrack(
        title=resolved.stem,
        path=resolved,
        ticks_per_beat=ticks_per_beat,
        karaoke_enabled=karaoke_enabled,
        notes=tuple(all_notes),
    )
