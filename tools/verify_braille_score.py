#!/usr/bin/env python3
"""Read-only consistency checks for a MusicXML score and its Braille exports.

This checker deliberately separates deterministic checks from musical claims that
would require an independent Music Braille decoder or a qualified transcriber.
It never writes to any input file and verifies input hashes before exiting.

Exit codes:
  0  deterministic checks passed (warnings may still be present)
  1  one or more confirmed errors
  2  no confirmed error, but independent musical verification is incomplete
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable


DEFAULT_NABCC_TABLES = (
    Path("/Applications/SM BungSang.app/Contents/Resources/tables/en-nabcc.utb"),
    Path("/Applications/SM BungSang.app/Contents/Resources/liblouis/tables/en-nabcc.utb"),
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    location: str = ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element if local_name(child.tag) == name]


def child(element: ET.Element, name: str) -> ET.Element | None:
    return next((item for item in element if local_name(item.tag) == name), None)


def child_text(element: ET.Element, name: str, default: str = "") -> str:
    item = child(element, name)
    return (item.text or "").strip() if item is not None else default


def descendants(element: ET.Element, name: str) -> list[ET.Element]:
    return [item for item in element.iter() if local_name(item.tag) == name]


def add(
    findings: list[Finding], severity: str, code: str, message: str, location: str = ""
) -> None:
    findings.append(Finding(severity, code, message, location))


def decode_utf8(path: Path, findings: list[Finding], label: str) -> str | None:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        add(findings, "WARNING", "UTF8_BOM", f"{label} starts with a UTF-8 BOM.", str(path))
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        add(
            findings,
            "ERROR",
            "INVALID_UTF8",
            f"{label} is not valid UTF-8: {exc}.",
            str(path),
        )
        return None


def check_unicode_braille(
    path: Path, findings: list[Finding], max_cells: int, max_lines: int
) -> dict:
    text = decode_utf8(path, findings, "Unicode Braille file")
    if text is None:
        return {"readable": False}

    bad: list[tuple[int, str]] = []
    for offset, char in enumerate(text):
        codepoint = ord(char)
        if char in " \n\r\f" or 0x2800 <= codepoint <= 0x283F:
            continue
        bad.append((offset, f"U+{codepoint:04X}"))
    if bad:
        sample = ", ".join(f"offset {offset}: {code}" for offset, code in bad[:12])
        add(
            findings,
            "ERROR",
            "NON_BRAILLE_CHARACTER",
            f"Found {len(bad)} character(s) outside six-dot Braille and permitted layout controls: {sample}.",
            str(path),
        )

    pages = text.replace("\r\n", "\n").replace("\r", "\n").split("\f")
    widths: list[int] = []
    line_counts: list[int] = []
    for page_number, page in enumerate(pages, 1):
        lines = page.splitlines()
        line_counts.append(len(lines))
        for line_number, line in enumerate(lines, 1):
            width = len(line)
            widths.append(width)
            if width > max_cells:
                add(
                    findings,
                    "ERROR",
                    "BRAILLE_LINE_TOO_WIDE",
                    f"Line has {width} cells; limit is {max_cells}.",
                    f"{path}: page {page_number}, line {line_number}",
                )
        if len(lines) > max_lines:
            add(
                findings,
                "ERROR",
                "BRAILLE_PAGE_TOO_LONG",
                f"Page has {len(lines)} lines; limit is {max_lines}.",
                f"{path}: page {page_number}",
            )

    return {
        "readable": True,
        "pages": len(pages),
        "form_feeds": text.count("\f"),
        "max_line_cells": max(widths, default=0),
        "max_page_lines": max(line_counts, default=0),
        "invalid_character_count": len(bad),
        "text": text,
    }


def parse_nabcc_table(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    pattern = re.compile(r"^sign\s+\\x([0-9a-fA-F]{4})\s+([0-8]+)\b")
    for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        codepoint = int(match.group(1), 16)
        if not 0x20 <= codepoint <= 0x7E:
            continue
        dots = match.group(2)
        if dots == "0":
            cell = "\u2800"
        else:
            # en-nabcc.utb is an eight-dot display table. BRF uses ASCII
            # capitals for pagination, but the Unicode export is six-dot;
            # dots 7 and 8 are display-case markers and must be discarded.
            six_dots = [dot for dot in dots if dot in "123456"]
            cell = chr(0x2800 + sum(1 << (int(dot) - 1) for dot in six_dots))
        mapping[chr(codepoint)] = cell
    return mapping


def locate_nabcc_table(explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit if explicit.is_file() else None
    return next((path for path in DEFAULT_NABCC_TABLES if path.is_file()), None)


def normalize_braille_lines(text: str) -> list[list[str]]:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace(" ", "\u2800")
    pages: list[list[str]] = []
    for page in text.split("\f"):
        lines = [line.rstrip("\u2800") for line in page.split("\n")]
        while lines and not lines[-1]:
            lines.pop()
        pages.append(lines)
    return pages


def convert_brf_to_unicode(brf: str, mapping: dict[str, str], findings: list[Finding], path: Path) -> str:
    output: list[str] = []
    unknown: Counter[str] = Counter()
    for char in brf.replace("\r\n", "\n").replace("\r", "\n"):
        if char in "\n\f":
            output.append(char)
        elif char in mapping:
            output.append(mapping[char])
        else:
            unknown[char] += 1
            output.append("\ufffd")
    if unknown:
        rendered = ", ".join(f"{repr(char)}×{count}" for char, count in unknown.most_common())
        add(
            findings,
            "ERROR",
            "UNKNOWN_BRF_CHARACTER",
            f"BRF contains characters absent from the NABCC table: {rendered}.",
            str(path),
        )
    return "".join(output)


def remove_known_export_metadata(
    pages: list[list[str]], mapping: dict[str, str]
) -> tuple[list[list[str]], Counter[str]]:
    """Remove only the two metadata placeholders documented as BRF omissions."""
    targets = {
        "Project Copyright": ",project ,copyright",
        "Project Lyricist": ",project ,lyricist",
    }
    cells_to_label = {
        "".join(mapping[char] for char in brf_text).strip("\u2800"): label
        for label, brf_text in targets.items()
    }
    removed: Counter[str] = Counter()
    cleaned: list[list[str]] = []
    for page_number, lines in enumerate(pages):
        new_lines: list[str] = []
        for line in lines:
            label = cells_to_label.get(line.strip("\u2800")) if page_number == 0 else None
            if label:
                removed[label] += 1
            else:
                new_lines.append(line)
        cleaned.append(new_lines)
    return cleaned, removed


def compare_unicode_and_brf(
    unicode_text: str,
    brf_path: Path,
    table_path: Path | None,
    findings: list[Finding],
) -> dict:
    try:
        brf = brf_path.read_text(encoding="ascii", errors="strict")
    except UnicodeError as exc:
        add(findings, "ERROR", "BRF_NOT_ASCII", f"BRF is not strict ASCII: {exc}.", str(brf_path))
        return {"compared": False}

    if table_path is None:
        add(
            findings,
            "REVIEW",
            "NABCC_TABLE_MISSING",
            "No en-nabcc.utb table was found; BRF-to-Unicode dot comparison was not run.",
            str(brf_path),
        )
        return {"compared": False, "brf_text": brf}

    mapping = parse_nabcc_table(table_path)
    missing_ascii = sorted(set(brf) - set(mapping) - {"\n", "\r", "\f"})
    if len(mapping) < 95 or missing_ascii:
        add(
            findings,
            "ERROR",
            "NABCC_TABLE_INCOMPLETE",
            f"NABCC mapping has {len(mapping)} printable ASCII entries; missing BRF characters: {missing_ascii!r}.",
            str(table_path),
        )
        return {"compared": False, "brf_text": brf}

    converted = convert_brf_to_unicode(brf, mapping, findings, brf_path)
    unicode_pages = normalize_braille_lines(unicode_text)
    brf_pages = normalize_braille_lines(converted)
    unicode_clean, removed = remove_known_export_metadata(unicode_pages, mapping)
    # Vertical whitespace is checked independently against max_lines. Ignore
    # empty rows here because removing title metadata legitimately reflows them.
    unicode_clean = [[line for line in page if line] for page in unicode_clean]
    brf_pages = [[line for line in page if line] for page in brf_pages]

    if removed:
        labels = ", ".join(f"{label}×{count}" for label, count in sorted(removed.items()))
        add(
            findings,
            "WARNING",
            "PLACEHOLDER_METADATA_IN_UNICODE",
            f"Unicode title page contains placeholder metadata omitted from BRF: {labels}.",
            "Unicode Braille title page",
        )

    mismatch = None
    max_pages = max(len(unicode_clean), len(brf_pages))
    for page_index in range(max_pages):
        u_lines = unicode_clean[page_index] if page_index < len(unicode_clean) else []
        b_lines = brf_pages[page_index] if page_index < len(brf_pages) else []
        max_lines = max(len(u_lines), len(b_lines))
        for line_index in range(max_lines):
            u_line = u_lines[line_index] if line_index < len(u_lines) else ""
            b_line = b_lines[line_index] if line_index < len(b_lines) else ""
            if u_line != b_line:
                first_cell = next(
                    (
                        cell_index + 1
                        for cell_index, pair in enumerate(zip(u_line, b_line))
                        if pair[0] != pair[1]
                    ),
                    min(len(u_line), len(b_line)) + 1,
                )
                mismatch = (page_index + 1, line_index + 1, first_cell, u_line, b_line)
                break
        if mismatch:
            break

    if mismatch:
        page, line, cell_number, u_line, b_line = mismatch
        add(
            findings,
            "ERROR",
            "BRF_UNICODE_MISMATCH",
            "BRF and Unicode Braille differ after NABCC conversion and the two documented metadata omissions. "
            f"First mismatch at page {page}, line {line}, cell {cell_number}; "
            f"Unicode length={len(u_line)}, BRF length={len(b_line)}.",
            f"{brf_path} / Unicode Braille",
        )

    return {
        "compared": True,
        "match_after_documented_metadata_omissions": mismatch is None,
        "nabcc_table": str(table_path),
        "removed_metadata": dict(removed),
        "brf_pages": len(brf_pages),
        "brf_text": brf,
    }


NUMBER_CELLS = {"a": "1", "b": "2", "c": "3", "d": "4", "e": "5", "f": "6", "g": "7", "h": "8", "i": "9", "j": "0"}


def decode_braille_number(text: str) -> int | None:
    if not text or any(char not in NUMBER_CELLS for char in text):
        return None
    return int("".join(NUMBER_CELLS[char] for char in text))


def decode_brf_label(label: str) -> str:
    label = re.sub(r"'+", " ", label)
    output: list[str] = []
    number_mode = False
    for char in label:
        if char == "#":
            number_mode = True
        elif number_mode and char in NUMBER_CELLS:
            output.append(NUMBER_CELLS[char])
        else:
            number_mode = False
            if char == ",":
                continue
            if char == "7":
                output.append(" ")
            elif char.isalnum() or char.isspace():
                output.append(char.lower())
    return " ".join("".join(output).split())


def canonical_label(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def check_brf_structure(
    brf_text: str,
    expected_parts: list[str],
    expected_measures: int,
    findings: list[Finding],
    path: Path,
) -> dict:
    normalized = brf_text.replace("\r\n", "\n").replace("\r", "\n")
    pages = normalized.split("\f")
    lines = normalized.splitlines()

    header_index = next((index for index, line in enumerate(lines) if ",'?7" in line), len(lines))
    instrument_pattern = re.compile(r"^(?!>)(.*?)\s+(>[a-z]+')\s*$")
    labels: list[str] = []
    abbreviations: list[str] = []
    for line in lines[:header_index]:
        match = instrument_pattern.match(line.strip())
        if match:
            labels.append(decode_brf_label(match.group(1)))
            abbreviations.append(match.group(2))

    expected_labels = [canonical_label(name) for name in expected_parts]
    if labels != expected_labels:
        mismatch_at = next(
            (index for index, pair in enumerate(zip(labels, expected_labels), 1) if pair[0] != pair[1]),
            min(len(labels), len(expected_labels)) + 1,
        )
        actual = labels[mismatch_at - 1] if mismatch_at <= len(labels) else "<missing>"
        expected = expected_labels[mismatch_at - 1] if mismatch_at <= len(expected_labels) else "<none>"
        add(
            findings,
            "ERROR",
            "INSTRUMENT_LIST_MISMATCH",
            f"Braille instrument list differs from MusicXML at item {mismatch_at}: expected {expected!r}, got {actual!r}. "
            f"Counts: MusicXML={len(expected_labels)}, Braille={len(labels)}.",
            str(path),
        )

    headings: list[int] = []
    for line in lines[header_index:]:
        stripped = line.strip()
        if re.fullmatch(r"[a-j]+", stripped):
            number = decode_braille_number(stripped)
            if number is not None:
                headings.append(number)
    expected_headings = list(range(1, expected_measures + 1))
    if headings != expected_headings:
        add(
            findings,
            "ERROR",
            "MEASURE_HEADING_MISMATCH",
            f"Expected Braille measure headings {expected_headings}; found {headings}.",
            str(path),
        )

    unknown_abbreviations = sorted(
        {
            match.group(1)
            for line in lines[header_index:]
            if (match := re.match(r"^(>[a-z]+')", line.strip()))
        }
        - set(abbreviations)
    )
    if unknown_abbreviations:
        add(
            findings,
            "ERROR",
            "UNKNOWN_INSTRUMENT_ABBREVIATION",
            f"Music body uses abbreviations absent from the instrument list: {unknown_abbreviations}.",
            str(path),
        )

    return {
        "pages": len(pages),
        "form_feeds": normalized.count("\f"),
        "instrument_count": len(labels),
        "instrument_labels": labels,
        "instrument_abbreviations": abbreviations,
        "measure_headings": headings,
    }


def check_musicxml(path: Path, findings: list[Finding]) -> dict:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        add(findings, "ERROR", "MUSICXML_NOT_WELL_FORMED", str(exc), str(path))
        return {"well_formed": False, "part_names": [], "measure_count": 0}

    root_name = local_name(root.tag)
    version = root.get("version", "")
    if root_name != "score-partwise":
        add(findings, "ERROR", "MUSICXML_ROOT", f"Expected score-partwise; found {root_name!r}.", str(path))
    if version != "4.0":
        add(findings, "WARNING", "MUSICXML_VERSION", f"Expected MusicXML 4.0; found {version!r}.", str(path))

    part_list = next((item for item in root if local_name(item.tag) == "part-list"), None)
    score_parts = descendants(part_list, "score-part") if part_list is not None else []
    part_names = [child_text(item, "part-name") for item in score_parts]
    declared_ids = [item.get("id", "") for item in score_parts]
    parts = children(root, "part")
    actual_ids = [item.get("id", "") for item in parts]
    if declared_ids != actual_ids:
        add(
            findings,
            "ERROR",
            "PART_ID_MISMATCH",
            f"part-list IDs {declared_ids!r} do not match score part IDs {actual_ids!r}.",
            str(path),
        )

    measure_sequences = [[measure.get("number", "") for measure in children(part, "measure")] for part in parts]
    reference_sequence = measure_sequences[0] if measure_sequences else []
    for index, sequence in enumerate(measure_sequences[1:], 2):
        if sequence != reference_sequence:
            add(
                findings,
                "ERROR",
                "MEASURE_SEQUENCE_MISMATCH",
                f"Part {index} measure numbers differ from part 1.",
                str(path),
            )

    tag_counts = Counter(local_name(item.tag) for item in root.iter())
    duration_errors = 0
    for part_index, part in enumerate(parts, 1):
        divisions = 1
        meter: Fraction | None = None
        for measure in children(part, "measure"):
            attributes = child(measure, "attributes")
            if attributes is not None:
                divisions_text = child_text(attributes, "divisions")
                if divisions_text:
                    divisions = int(divisions_text)
                time = child(attributes, "time")
                if time is not None:
                    beats_text = child_text(time, "beats")
                    beat_type_text = child_text(time, "beat-type")
                    if beats_text.isdigit() and beat_type_text.isdigit():
                        meter = Fraction(int(beats_text) * 4, int(beat_type_text))

            cursor = Fraction(0)
            maximum_end = Fraction(0)
            previous_onset = Fraction(0)
            for event in measure:
                name = local_name(event.tag)
                duration_text = child_text(event, "duration")
                duration = Fraction(int(duration_text), divisions) if duration_text else Fraction(0)
                if name == "backup":
                    cursor -= duration
                    if cursor < 0:
                        add(
                            findings,
                            "ERROR",
                            "NEGATIVE_MUSICXML_CURSOR",
                            "A backup moves before the start of the measure.",
                            f"{path}: part {part_index}, measure {measure.get('number')}",
                        )
                elif name == "forward":
                    cursor += duration
                    maximum_end = max(maximum_end, cursor)
                elif name == "note":
                    is_chord = child(event, "chord") is not None
                    onset = previous_onset if is_chord else cursor
                    maximum_end = max(maximum_end, onset + duration)
                    if not is_chord:
                        previous_onset = onset
                        cursor += duration

            if meter is not None and maximum_end != meter:
                duration_errors += 1
                add(
                    findings,
                    "ERROR",
                    "MEASURE_DURATION_MISMATCH",
                    f"Encoded span is {maximum_end} quarter notes; meter requires {meter}.",
                    f"{path}: part {part_index}, measure {measure.get('number')}",
                )

    for element_name in ("tie", "tied", "slur"):
        types = Counter(item.get("type", "") for item in descendants(root, element_name))
        if types["start"] != types["stop"]:
            add(
                findings,
                "ERROR",
                f"UNBALANCED_{element_name.upper()}",
                f"{element_name} starts={types['start']}, stops={types['stop']}.",
                str(path),
            )

    wedge_types = Counter(item.get("type", "") for item in descendants(root, "wedge"))
    wedge_starts = wedge_types["crescendo"] + wedge_types["diminuendo"]
    if wedge_starts != wedge_types["stop"]:
        add(
            findings,
            "ERROR",
            "UNBALANCED_WEDGE",
            f"Wedge starts={wedge_starts}, stops={wedge_types['stop']}.",
            str(path),
        )

    placeholder_values: list[str] = []
    metadata_nodes = descendants(root, "movement-title") + descendants(root, "credit-words")
    for item in metadata_nodes:
        value = (item.text or "").strip()
        if value.lower() in {"test", "project copyright", "project lyricist"}:
            placeholder_values.append(value)
    if placeholder_values:
        placeholder_counts = Counter(placeholder_values)
        rendered_placeholders = ", ".join(
            f"{value!r}×{count}" for value, count in sorted(placeholder_counts.items())
        )
        add(
            findings,
            "WARNING",
            "PLACEHOLDER_METADATA_IN_MUSICXML",
            f"Suspicious placeholder metadata remains: {rendered_placeholders}.",
            str(path),
        )

    semantic_elements = (
        "pitch", "unpitched", "rest", "duration", "dot", "accidental", "tie", "tied",
        "slur", "articulations", "dynamics", "wedge", "time-modification", "tuplet",
        "transpose", "key", "time", "clef",
    )
    present_semantics = {name: tag_counts[name] for name in semantic_elements if tag_counts[name]}
    review_features = (
        "unpitched", "accidental", "tie", "tied", "slur", "articulations",
        "dynamics", "wedge", "time-modification", "tuplet", "transpose", "clef",
    )
    feature_locations: dict[str, list[str]] = {}
    for feature in review_features:
        locations: list[str] = []
        for part_index, part in enumerate(parts):
            part_label = part_names[part_index] if part_index < len(part_names) else f"part {part_index + 1}"
            for measure in children(part, "measure"):
                if descendants(measure, feature):
                    locations.append(f"{part_label} m.{measure.get('number', '?')}")
        if locations:
            feature_locations[feature] = locations
    if present_semantics:
        add(
            findings,
            "REVIEW",
            "MUSICAL_EQUIVALENCE_NOT_INDEPENDENTLY_DECODED",
            "MusicXML musical events were checked internally, but their pitch, duration, accidental, articulation, "
            "dynamic, slur/tie, tuplet, clef, key, and transposition meanings were not independently decoded back "
            "from Music Braille. A qualified transcriber or independent reverse decoder is still required.",
            str(path),
        )

    tempos = sorted({item.get("tempo", "") for item in descendants(root, "sound") if item.get("tempo")})
    return {
        "well_formed": True,
        "root": root_name,
        "version": version,
        "part_count": len(parts),
        "part_names": part_names,
        "measure_count_per_part": len(reference_sequence),
        "total_measure_elements": tag_counts["measure"],
        "duration_error_count": duration_errors,
        "tag_counts": dict(sorted(tag_counts.items())),
        "present_musical_semantics": present_semantics,
        "feature_locations": feature_locations,
        "tempos": tempos,
        "placeholder_metadata": placeholder_values,
    }


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--musicxml", required=True, type=Path)
    parser.add_argument("--braille", required=True, type=Path, help="Unicode Braille TXT")
    parser.add_argument("--brf", type=Path, help="Optional NABCC/BRF export")
    parser.add_argument("--nabcc-table", type=Path, help="Path to en-nabcc.utb")
    parser.add_argument("--max-cells", type=int, default=40)
    parser.add_argument("--max-lines", type=int, default=25)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    paths = [args.musicxml, args.braille] + ([args.brf] if args.brf else [])
    findings: list[Finding] = []
    missing = [path for path in paths if not path.is_file()]
    if missing:
        for path in missing:
            add(findings, "ERROR", "INPUT_MISSING", "Input file does not exist.", str(path))
        result = {"status": "FAIL", "findings": [asdict(item) for item in findings]}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    hashes_before = {str(path): sha256(path) for path in paths}
    xml = check_musicxml(args.musicxml, findings)
    braille = check_unicode_braille(args.braille, findings, args.max_cells, args.max_lines)

    brf_result: dict = {"provided": False}
    if args.brf and braille.get("readable"):
        table_path = locate_nabcc_table(args.nabcc_table)
        brf_result = compare_unicode_and_brf(
            braille["text"], args.brf, table_path, findings
        )
        brf_result["provided"] = True
        if "brf_text" in brf_result:
            brf_result["structure"] = check_brf_structure(
                brf_result.pop("brf_text"),
                xml.get("part_names", []),
                xml.get("measure_count_per_part", 0),
                findings,
                args.brf,
            )
    else:
        add(
            findings,
            "REVIEW",
            "BRF_NOT_PROVIDED",
            "No BRF was supplied, so a second encoding could not corroborate Unicode Braille cell content.",
        )

    hashes_after = {str(path): sha256(path) for path in paths}
    inputs_unchanged = hashes_before == hashes_after
    if not inputs_unchanged:
        add(findings, "ERROR", "INPUT_CHANGED", "An input hash changed during the read-only check.")

    severities = Counter(item.severity for item in findings)
    if severities["ERROR"]:
        status = "FAIL"
        exit_code = 1
    elif severities["REVIEW"]:
        status = "NEEDS_EXPERT_REVIEW"
        exit_code = 2
    else:
        status = "PASS"
        exit_code = 0

    braille.pop("text", None)
    result = {
        "status": status,
        "inputs_unchanged": inputs_unchanged,
        "input_sha256": hashes_after,
        "musicxml": xml,
        "unicode_braille": braille,
        "brf": brf_result,
        "finding_counts": dict(severities),
        "findings": [asdict(item) for item in findings],
    }
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Status: {status}")
        print(f"Inputs unchanged: {inputs_unchanged}")
        print(
            f"MusicXML: {xml.get('part_count', 0)} parts × "
            f"{xml.get('measure_count_per_part', 0)} measures; "
            f"duration errors={xml.get('duration_error_count', 0)}"
        )
        print(
            f"Unicode Braille: {braille.get('pages', 0)} pages; "
            f"max {braille.get('max_line_cells', 0)} cells × {braille.get('max_page_lines', 0)} lines"
        )
        for item in findings:
            suffix = f" [{item.location}]" if item.location else ""
            print(f"{item.severity}: {item.code}: {item.message}{suffix}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
