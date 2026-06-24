from dataclasses import dataclass, field
from pathlib import Path
import re

from .binary_string_scanner import LocatedString, LocatedUUID, scan_printable_strings, scan_uuids
from .rtf_parser import rtf_to_text


SECTION_PATTERN = re.compile(r"^(?:Intro|Verse(?: \d+)?|Chorus(?: \d+)?|Bridge(?: \d+)?|Tag(?: \d+)?|Outro|Instrumental|Pre[- ]Chorus(?: \d+)?|Refrain(?: \d+)?)$", re.IGNORECASE)
DATE_PATTERN = re.compile(rb"20\d{6}(?:-\d+)?")


@dataclass(frozen=True, slots=True)
class RTFBlock:
    offset: int
    length: int
    text: str


@dataclass(frozen=True, slots=True)
class Inference:
    relationship: str
    confidence: float
    reason: str


@dataclass(slots=True)
class SectionFinding:
    uuid: str
    name: str
    offset: int
    slide_uuids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SlideFinding:
    uuid: str
    section_uuid: str | None
    offset: int
    sung_text: str = ""
    translation: str = ""


@dataclass(slots=True)
class ArrangementFinding:
    name: str
    section_uuids: list[str]
    slide_uuids: list[str]
    is_default: bool
    confidence: float


@dataclass(slots=True)
class ProFileInspection:
    path: Path
    title: str
    source_id: str
    strings: list[LocatedString]
    uuids: list[LocatedUUID]
    rtf_blocks: list[RTFBlock]
    sections: list[SectionFinding]
    slides: list[SlideFinding]
    arrangements: list[ArrangementFinding]
    inferences: list[Inference]
    unmatched_uuids: list[LocatedUUID]
    unmatched_rtf_blocks: list[RTFBlock]
    fallback_decisions: list[str]

    def render(self, debug: bool = False) -> str:
        lines = [f"Song title: {self.title}", f"Source: {self.path}", f"Source ID: {self.source_id}", f"Strings: {len(self.strings)}  UUID occurrences: {len(self.uuids)}  RTF blocks: {len(self.rtf_blocks)}", "", "Sections:"]
        lines.extend(f"  0x{item.offset:08x} {item.uuid} -> {item.name} ({len(item.slide_uuids)} slides)" for item in self.sections)
        lines.append("\nSlides:")
        lines.extend(f"  0x{item.offset:08x} {item.uuid} section={item.section_uuid or '?'} sung={item.sung_text!r} translation={item.translation!r}" for item in self.slides)
        lines.append("\nArrangements:")
        lines.extend(f"  {item.name}{' [default]' if item.is_default else ''}: {len(item.slide_uuids)} slides confidence={item.confidence:.2f}" for item in self.arrangements)
        if debug:
            lines.append("\nPrintable strings:")
            lines.extend(f"  0x{item.offset:08x} {item.value!r}" for item in self.strings)
            lines.append("\nRTF blocks:")
            lines.extend(f"  0x{item.offset:08x} length={item.length} text={item.text!r}" for item in self.rtf_blocks)
            lines.append("\nArrangement mappings:")
            for item in self.arrangements:
                lines.append(f"  {item.name}: sections={item.section_uuids!r}")
                lines.append(f"  {item.name}: ordered_slides={item.slide_uuids!r}")
            lines.append("\nConfidence / decisions:")
            lines.extend(f"  {item.confidence:.2f} {item.relationship}: {item.reason}" for item in self.inferences)
            lines.extend(f"  fallback: {item}" for item in self.fallback_decisions)
            lines.append(f"\nUnmatched UUID occurrences ({len(self.unmatched_uuids)}):")
            lines.extend(f"  0x{item.offset:08x} {item.value}" for item in self.unmatched_uuids)
            lines.append(f"\nUnmatched RTF blocks ({len(self.unmatched_rtf_blocks)}):")
            lines.extend(f"  0x{item.offset:08x} length={item.length} text={item.text!r}" for item in self.unmatched_rtf_blocks)
        return "\n".join(lines)


def extract_rtf_blocks(data: bytes) -> list[RTFBlock]:
    blocks: list[RTFBlock] = []
    cursor = 0
    marker = b"{\\rtf"
    while (start := data.find(marker, cursor)) >= 0:
        depth = 0
        escaped = False
        end = start
        while end < len(data):
            value = data[end]
            if value == 0x5C:
                escaped = not escaped
            else:
                if value == 0x7B and not escaped:
                    depth += 1
                elif value == 0x7D and not escaped:
                    depth -= 1
                    if depth == 0:
                        end += 1
                        break
                escaped = False
            end += 1
        raw = data[start:end]
        blocks.append(RTFBlock(start, len(raw), rtf_to_text(raw)))
        cursor = max(end, start + 1)
    return blocks


class ProFileInspector:
    def inspect(self, path: Path) -> ProFileInspection:
        data = path.read_bytes()
        strings = scan_printable_strings(data)
        uuids = scan_uuids(data)
        rtfs = extract_rtf_blocks(data)
        title = path.stem
        source_id = uuids[0].value if uuids else path.stem
        labels = [LocatedString(item.offset, item.value.strip().strip('"')) for item in strings if SECTION_PATTERN.fullmatch(item.value.strip().strip('"'))]
        sections = self._sections(labels, uuids)
        slides, matched_rtfs = self._slides(data, sections, uuids, rtfs)
        arrangements, fallbacks = self._arrangements(data, sections, slides)
        used_values = {section.uuid for section in sections} | {uuid for section in sections for uuid in section.slide_uuids}
        used_offsets = {item.offset for item in uuids if item.value in used_values}
        inferences = [
            Inference("section UUID -> name", 0.98, "adjacent UUID and recognized section label in the section table"),
            Inference("section -> slide UUIDs", 0.95, "UUID references bounded by consecutive section records"),
            Inference("slide -> text layers", 0.96, "repeated slide UUID payload contains named sung/translation RTF layers"),
        ]
        if arrangements:
            inferences.append(Inference("default arrangement", arrangements[-1].confidence, "last explicit dated arrangement record; expanded through section slide references"))
        return ProFileInspection(path, title, source_id, strings, uuids, rtfs, sections, slides, arrangements, inferences, [item for item in uuids if item.offset not in used_offsets], [item for item in rtfs if item.offset not in matched_rtfs], fallbacks)

    @staticmethod
    def _sections(labels: list[LocatedString], uuids: list[LocatedUUID]) -> list[SectionFinding]:
        found: list[SectionFinding] = []
        found_uuids: set[str] = set()
        for label in labels:
            preceding = [item for item in uuids if item.offset < label.offset]
            if not preceding:
                continue
            section_uuid = preceding[-1]
            if label.offset - (section_uuid.offset + 36) > 16:
                continue
            # Some legacy files repeat a section label directly after the same
            # UUID. The UUID identifies the section; repeated labels are not
            # separate section records.
            if section_uuid.value in found_uuids:
                continue
            found.append(SectionFinding(section_uuid.value, label.value.strip(), section_uuid.offset))
            found_uuids.add(section_uuid.value)
        prior_slide_uuids: set[str] = set()
        section_uuids = {item.uuid for item in found}
        for index, section in enumerate(found):
            start = next(item.offset + len(item.value) for item in labels if item.value.strip() == section.name and item.offset > section.offset)
            end = found[index + 1].offset if index + 1 < len(found) else (start + 512)
            candidates = [item.value for item in uuids if start <= item.offset < end and item.value != section.uuid]
            if index + 1 == len(found):
                unique_candidates: list[str] = []
                for value in candidates:
                    if value in prior_slide_uuids or value in section_uuids:
                        break
                    unique_candidates.append(value)
                candidates = unique_candidates
            section.slide_uuids = candidates
            prior_slide_uuids.update(candidates)
        return found

    @staticmethod
    def _slides(data: bytes, sections: list[SectionFinding], uuids: list[LocatedUUID], rtfs: list[RTFBlock]) -> tuple[list[SlideFinding], set[int]]:
        section_by_slide = {slide_uuid: section.uuid for section in sections for slide_uuid in section.slide_uuids}
        references = set(section_by_slide)
        first_layer = data.find(b"Gezongen tekst")
        table_limit = first_layer if first_layer >= 0 else len(data)
        table_references = [item.offset for item in uuids if item.value in references and item.offset < table_limit]
        table_end = max(table_references, default=max((section.offset for section in sections), default=0))
        payloads: list[tuple[int, str]] = []
        for value in references:
            occurrences = [item.offset for item in uuids if item.value == value and item.offset > table_end]
            if occurrences:
                payloads.append((occurrences[0], value))
        payloads.sort()
        slides: list[SlideFinding] = []
        matched: set[int] = set()
        for index, (start, value) in enumerate(payloads):
            end = payloads[index + 1][0] if index + 1 < len(payloads) else len(data)
            blocks = [block for block in rtfs if start < block.offset < end]
            sung = ""
            translation = ""
            for block in blocks:
                matched.add(block.offset)
                # Legacy ProPresenter files can contain empty RTF placeholders
                # between the actual sung-text and translation layers. They
                # carry layout data, but must not erase text recovered from an
                # earlier block in the same slide payload.
                if not block.text.strip():
                    continue
                context = data[max(start, block.offset - 700):block.offset].decode("cp1252", errors="ignore")
                if context.rfind("Vertaling") > context.rfind("Gezongen tekst"):
                    translation = block.text
                else:
                    sung = block.text
            slides.append(SlideFinding(value, section_by_slide.get(value), start, sung, translation))
        return slides, matched

    @staticmethod
    def _arrangements(data: bytes, sections: list[SectionFinding], slides: list[SlideFinding]) -> tuple[list[ArrangementFinding], list[str]]:
        section_map = {section.uuid: section for section in sections}
        known_slides = {slide.uuid for slide in slides}
        boundary = min((section.offset for section in sections), default=len(data))
        candidates: list[ArrangementFinding] = []
        dates = list(DATE_PATTERN.finditer(data[:boundary]))
        for index, match in enumerate(dates):
            end = dates[index + 1].start() if index + 1 < len(dates) else boundary
            values = [item.value for item in scan_uuids(data[match.end():end])]
            section_values = [value for value in values if value in section_map]
            direct_slides = [value for value in values if value in known_slides]
            expanded = direct_slides or [slide for section_uuid in section_values for slide in section_map[section_uuid].slide_uuids]
            if expanded:
                candidates.append(ArrangementFinding(match.group().decode("ascii"), section_values, expanded, False, 0.92 if direct_slides else 0.88))
        fallbacks: list[str] = []
        if candidates:
            candidates[-1].is_default = True
        else:
            ordered = [slide.uuid for slide in sorted(slides, key=lambda item: item.offset)]
            candidates.append(ArrangementFinding("Default", [], ordered, True, 0.40))
            fallbacks.append("No explicit arrangement record was recovered; physical slide order was used.")
        return candidates, fallbacks
