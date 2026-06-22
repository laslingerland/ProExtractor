from dataclasses import dataclass
import re


UUID_PATTERN = re.compile(rb"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}")


@dataclass(frozen=True, slots=True)
class LocatedString:
    offset: int
    value: str


@dataclass(frozen=True, slots=True)
class LocatedUUID:
    offset: int
    value: str


def scan_printable_strings(data: bytes, minimum_length: int = 4) -> list[LocatedString]:
    pattern = re.compile(rb"[\x20-\x7e\x80-\xff]{%d,}" % minimum_length)
    return [LocatedString(match.start(), match.group().decode("cp1252", errors="replace")) for match in pattern.finditer(data)]


def scan_uuids(data: bytes) -> list[LocatedUUID]:
    return [LocatedUUID(match.start(), match.group().decode("ascii").upper()) for match in UUID_PATTERN.finditer(data)]

