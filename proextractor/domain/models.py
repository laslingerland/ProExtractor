"""Pure domain data and behavior. This module has no infrastructure dependencies."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Section:
    id: int | None
    uuid: str
    name: str


@dataclass(slots=True)
class Slide:
    id: int | None
    uuid: str
    section_uuid: str | None
    sung_text: str
    translation: str = ""


@dataclass(slots=True)
class ArrangementSlideRef:
    slide_uuid: str
    sequence: int


@dataclass(slots=True)
class Arrangement:
    id: int | None
    name: str
    slide_refs: list[ArrangementSlideRef] = field(default_factory=list)
    is_default: bool = False


@dataclass(slots=True)
class Song:
    id: int | None
    title: str
    source_id: str
    sections: list[Section] = field(default_factory=list)
    slides: list[Slide] = field(default_factory=list)
    arrangements: list[Arrangement] = field(default_factory=list)

    def default_arrangement(self) -> Arrangement | None:
        return next((item for item in self.arrangements if item.is_default), self.arrangements[0] if self.arrangements else None)

    def arranged_slides(self) -> list[Slide]:
        arrangement = self.default_arrangement()
        if arrangement is None:
            return list(self.slides)
        by_uuid = {slide.uuid: slide for slide in self.slides}
        return [by_uuid[ref.slide_uuid] for ref in sorted(arrangement.slide_refs, key=lambda ref: ref.sequence) if ref.slide_uuid in by_uuid]


@dataclass(frozen=True, slots=True)
class SongSummary:
    id: int
    title: str
    source_id: str


@dataclass(frozen=True, slots=True)
class SongSearchResult:
    id: int
    title: str
    source_id: str
    snippet: str = ""

