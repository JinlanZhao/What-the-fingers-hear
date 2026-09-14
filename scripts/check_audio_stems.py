#!/usr/bin/env python3
"""Read-only technical validation for the project's WAV stem delivery.

The WAV and MusicXML inputs are only read. Optional output paths create a
Markdown report and draft JSON manifests; they never overwrite audio files.

Requires: numpy, soundfile
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import soundfile as sf


SAMPLE_RATE = 48_000
BIT_DEPTH = 24
CHANNELS = 2
SAMPLE_COUNT = 1_280_000
BPM = 144
BAR_COUNT = 16
SAMPLES_PER_BAR = 80_000
SILENCE_DBFS = -90.0
DC_WARNING = 0.001
CLIP_VALUE = 1.0 - 1.0 / (2**23)

# Canonical stem identity is the slug, not the current filename number.
# This lets the checker diagnose a global numbering offset without losing the
# MusicXML relationship. Percussion filenames and XML order intentionally differ.
TRACKS = (
    (1, "WW_fl1", "score", "P1", "Flute 1"),
    (2, "WW_fl2", "score", "P2", "Flute 2"),
    (3, "WW_ob1", "score", "P3", "Oboe 1"),
    (4, "WW_ob2", "score", "P4", "Oboe 2"),
    (5, "WW_cl1", "score", "P5", "Clarinet (B Flat) 1"),
    (6, "WW_cl2", "score", "P6", "Clarinet (B Flat) 2"),
    (7, "WW_bsn1", "score", "P7", "Bassoon 1"),
    (8, "WW_bsn2", "score", "P8", "Bassoon 2"),
    (9, "BRS_fh1", "score", "P9", "Horn  (F) 1"),
    (10, "BRS_fh2", "score", "P10", "Horn  (F) 2"),
    (11, "BRS_fh3", "score", "P11", "Horn  (F) 3"),
    (12, "BRS_fh4", "score", "P12", "Horn  (F) 4"),
    (13, "BRS_tpt1", "score", "P13", "Trumpet (C) 1"),
    (14, "BRS_tpt2", "score", "P14", "Trumpet (C) 2"),
    (15, "BRS_tbn1", "score", "P15", "Trombone 1"),
    (16, "BRS_tbn2", "score", "P16", "Trombone 2"),
    (17, "BRS_tb", "score", "P17", "Tuba"),
    (18, "PRC_glk", "score", "P18", "Glockenspiel"),
    (19, "PRC_bd", "score", "P20", "Bass Drum"),
    (20, "PRC_sn", "score", "P19", "Snare Drum"),
    (21, "STR_vln1", "score", "P21", "Violin 1"),
    (22, "STR_vln2", "score", "P22", "Violin 2"),
    (23, "STR_vla", "score", "P23", "Viola"),
    (24, "STR_vc", "score", "P24", "Violoncello"),
    (25, "STR_cb", "score", "P25", "Double Bass"),
    (26, "OTH_crash", "effect", None, "Crash effect"),
    (27, "OTH_riser", "effect", None, "Riser effect"),
    (28, "OTH_room", "effect", None, "Room effect"),
    (29, "OTH_stem", "effect", None, "Other stem effect"),
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


def dbfs(value: float) -> float | None:
    return round(20.0 * math.log10(value), 4) if value > 0 else None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_lfs_pointer(path: Path) -> bool:
    with path.open("rb") as handle:
        head = handle.read(256)
    return head.startswith(b"version https://git-lfs.github.com/spec/v1")


def parse_stem_name(path: Path) -> tuple[int | None, str | None, str]:
    prefix = re.fullmatch(r"(\d{2})_(.+)\.wav", path.name, flags=re.IGNORECASE)
    if prefix:
        return int(prefix.group(1)), prefix.group(2), "number_prefix"
    suffix = re.fullmatch(r"(.+?)__(\d{2})\.wav", path.name, flags=re.IGNORECASE)
    if suffix:
        return int(suffix.group(2)), suffix.group(1).rstrip("_"), "double_underscore_suffix"
    return None, None, "unrecognized"


def longest_true_run(values: np.ndarray) -> int:
    if values.size == 0 or not np.any(values):
        return int(values.size if values.size and bool(values[0]) else 0)
    padded = np.concatenate(([False], values, [False]))
    edges = np.flatnonzero(padded[1:] != padded[:-1])
    return int(np.max(edges[1::2] - edges[::2]))


def audio_metrics(path: Path) -> tuple[dict, np.ndarray | None, str | None]:
    if is_lfs_pointer(path):
        return {"filename": path.name, "git_lfs_pointer": True}, None, None
    try:
        info = sf.info(path)
        audio, sample_rate = sf.read(path, dtype="float64", always_2d=True)
    except Exception as exc:
        return {"filename": path.name, "git_lfs_pointer": False}, None, str(exc)

    if len(audio) != info.frames:
        return {"filename": path.name, "git_lfs_pointer": False}, None, (
            f"decoder returned {len(audio)} frames but header reports {info.frames}"
        )

    peak = np.max(np.abs(audio), axis=0) if len(audio) else np.zeros(info.channels)
    rms = np.sqrt(np.mean(audio * audio, axis=0)) if len(audio) else np.zeros(info.channels)
    dc = np.mean(audio, axis=0) if len(audio) else np.zeros(info.channels)
    frame_peak = np.max(np.abs(audio), axis=1) if len(audio) else np.array([], dtype=float)
    silent = frame_peak <= 10 ** (SILENCE_DBFS / 20.0)

    correlation = None
    dual_mono = None
    balance = None
    max_lr_difference = None
    if info.channels == 2 and len(audio):
        left = audio[:, 0] - dc[0]
        right = audio[:, 1] - dc[1]
        denominator = float(np.sqrt(np.dot(left, left) * np.dot(right, right)))
        correlation = float(np.dot(left, right) / denominator) if denominator else None
        max_lr_difference = float(np.max(np.abs(audio[:, 0] - audio[:, 1])))
        dual_mono = max_lr_difference <= 1.0 / (2**BIT_DEPTH)
        balance = dbfs(float(rms[1] / rms[0])) if rms[0] > 0 else None

    metrics = {
        "filename": path.name,
        "bytes": path.stat().st_size,
        "git_lfs_pointer": False,
        "format": info.format,
        "subtype": info.subtype,
        "sample_rate_hz": sample_rate,
        "bit_depth": 24 if info.subtype == "PCM_24" else None,
        "channels": info.channels,
        "sample_count": int(info.frames),
        "duration_seconds": round(float(info.duration), 9),
        "peak_dbfs": [dbfs(float(value)) for value in peak],
        "rms_dbfs": [dbfs(float(value)) for value in rms],
        "dc_offset": [round(float(value), 10) for value in dc],
        "clipped_samples": int(np.count_nonzero(np.abs(audio) >= CLIP_VALUE)),
        "silent_frame_percent": round(float(np.mean(silent) * 100.0), 4) if len(silent) else 100.0,
        "longest_silence_samples": longest_true_run(silent),
        "longest_silence_seconds": round(longest_true_run(silent) / sample_rate, 6),
        "lr_rms_balance_db_right_minus_left": balance,
        "stereo_correlation": round(correlation, 6) if correlation is not None else None,
        "dual_mono": dual_mono,
        "max_lr_sample_difference": round(max_lr_difference, 10) if max_lr_difference is not None else None,
        "stereo_difference_detected": bool(
            dual_mono is False
            and ((balance is not None and abs(balance) >= 0.25) or (correlation is not None and correlation < 0.999))
        ),
    }
    return metrics, audio, None


def read_musicxml_parts(path: Path) -> list[dict]:
    root = ET.parse(path).getroot()
    return [
        {
            "id": part.get("id"),
            "name": (part.findtext("part-name") or "").strip(),
        }
        for part in root.findall("./part-list/score-part")
    ]


def make_bar_times() -> dict:
    bars = []
    for bar in range(1, BAR_COUNT + 1):
        start = (bar - 1) * SAMPLES_PER_BAR
        end = bar * SAMPLES_PER_BAR
        bars.append(
            {
                "bar": bar,
                "start_sample": start,
                "end_sample_exclusive": end,
                "start_seconds": round(start / SAMPLE_RATE, 9),
                "end_seconds": round(end / SAMPLE_RATE, 9),
            }
        )
    return {
        "sample_rate_hz": SAMPLE_RATE,
        "tempo_bpm": BPM,
        "time_signature": {"beats": 4, "beat_unit": 4},
        "bar_count": BAR_COUNT,
        "samples_per_beat": 20_000,
        "samples_per_bar": SAMPLES_PER_BAR,
        "total_samples": SAMPLE_COUNT,
        "duration_seconds": round(SAMPLE_COUNT / SAMPLE_RATE, 9),
        "bars": bars,
    }


def validate(stems_dir: Path, musicxml: Path) -> dict:
    findings: list[Finding] = []
    wavs = sorted(stems_dir.glob("*.wav")) if stems_dir.is_dir() else []
    input_paths = wavs + ([musicxml] if musicxml.is_file() else [])
    hashes_before = {str(path): sha256(path) for path in input_paths}

    if not stems_dir.is_dir():
        findings.append(Finding("ERROR", "STEMS_DIRECTORY_MISSING", str(stems_dir)))
    if len(wavs) != 29:
        findings.append(Finding("ERROR", "WAV_COUNT", f"Expected 29 WAV files; found {len(wavs)}."))

    parsed = []
    for path in wavs:
        number, slug, convention = parse_stem_name(path)
        parsed.append({"path": path, "number": number, "slug": slug, "convention": convention})
        if number is None:
            findings.append(Finding("ERROR", "UNRECOGNIZED_FILENAME", path.name))

    numbers = [item["number"] for item in parsed if item["number"] is not None]
    counts = Counter(numbers)
    duplicates = sorted(number for number, count in counts.items() if count > 1)
    missing_numbers = sorted(set(range(1, 30)) - set(numbers))
    unexpected_numbers = sorted(set(numbers) - set(range(1, 30)))
    if duplicates:
        findings.append(Finding("ERROR", "DUPLICATE_NUMBERS", str(duplicates)))
    if missing_numbers or unexpected_numbers:
        findings.append(
            Finding(
                "ERROR",
                "NUMBERING_MISMATCH",
                f"Expected 01–29; missing={missing_numbers}, unexpected={unexpected_numbers}.",
            )
        )

    slug_to_items: dict[str, list[dict]] = {}
    for item in parsed:
        if item["slug"]:
            slug_to_items.setdefault(item["slug"], []).append(item)
    expected_slugs = {track[1] for track in TRACKS}
    duplicate_slugs = sorted(slug for slug, items in slug_to_items.items() if len(items) > 1)
    missing_slugs = sorted(expected_slugs - set(slug_to_items))
    unexpected_slugs = sorted(set(slug_to_items) - expected_slugs)
    if duplicate_slugs or missing_slugs or unexpected_slugs:
        findings.append(
            Finding(
                "ERROR",
                "TRACK_IDENTITY_MISMATCH",
                f"duplicate={duplicate_slugs}, missing={missing_slugs}, unexpected={unexpected_slugs}.",
            )
        )

    numbering_differences = []
    track_rows = []
    metrics_by_file: dict[str, dict] = {}
    score_mix = np.zeros((SAMPLE_COUNT, CHANNELS), dtype=np.float64)
    score_mix_usable = True
    for expected_number, slug, role, part_id, label in TRACKS:
        item = slug_to_items.get(slug, [None])[0]
        actual_number = item["number"] if item else None
        filename = item["path"].name if item else None
        if actual_number != expected_number:
            numbering_differences.append(
                {"slug": slug, "expected": expected_number, "actual": actual_number, "filename": filename}
            )

        metrics = None
        if item:
            metrics, audio, error = audio_metrics(item["path"])
            metrics_by_file[filename] = metrics
            if error:
                findings.append(Finding("ERROR", "CORRUPT_OR_UNREADABLE_WAV", f"{filename}: {error}"))
            elif metrics.get("git_lfs_pointer"):
                findings.append(Finding("ERROR", "GIT_LFS_POINTER", filename))
            else:
                expected_format = (
                    metrics["sample_rate_hz"] == SAMPLE_RATE
                    and metrics["bit_depth"] == BIT_DEPTH
                    and metrics["channels"] == CHANNELS
                    and metrics["sample_count"] == SAMPLE_COUNT
                )
                if not expected_format:
                    findings.append(
                        Finding(
                            "ERROR",
                            "AUDIO_FORMAT_OR_LENGTH",
                            f"{filename}: {metrics['sample_rate_hz']} Hz, {metrics['subtype']}, "
                            f"{metrics['channels']} ch, {metrics['sample_count']} samples.",
                        )
                    )
                if metrics["sample_count"] == 0 or all(value is None for value in metrics["peak_dbfs"]):
                    findings.append(Finding("ERROR", "EMPTY_AUDIO", filename))
                if metrics["clipped_samples"]:
                    findings.append(
                        Finding("ERROR", "STEM_CLIPPING", f"{filename}: {metrics['clipped_samples']} samples")
                    )
                if max(abs(value) for value in metrics["dc_offset"]) > DC_WARNING:
                    findings.append(
                        Finding("WARNING", "DC_OFFSET", f"{filename}: {metrics['dc_offset']}")
                    )
                if role == "score" and metrics["silent_frame_percent"] >= 90.0:
                    findings.append(
                        Finding(
                            "WARNING",
                            "ABNORMAL_SCORE_STEM_SILENCE",
                            f"{filename}: {metrics['silent_frame_percent']}% silent frames.",
                        )
                    )
                if metrics["dual_mono"]:
                    findings.append(Finding("WARNING", "DUAL_MONO", filename))
                if role == "score" and audio is not None and audio.shape == score_mix.shape:
                    score_mix += audio
                elif role == "score":
                    score_mix_usable = False

        track_row = {
            "expected_number": expected_number,
            "actual_number": actual_number,
            "slug": slug,
            "role": role,
            "filename": filename,
            "musicxml_part_id": part_id,
            "musicxml_part_name": label if role == "score" else None,
            "include_in_score_sum": role == "score",
        }
        track_rows.append(track_row)

    if numbering_differences:
        findings.append(
            Finding(
                "ERROR",
                "TRACK_NUMBER_ASSIGNMENTS",
                f"{len(numbering_differences)} track(s) do not carry their expected number.",
            )
        )

    try:
        xml_parts = read_musicxml_parts(musicxml)
    except Exception as exc:
        xml_parts = []
        findings.append(Finding("ERROR", "MUSICXML_READ", str(exc)))
    expected_xml = {
        part_id: label
        for _, _, role, part_id, label in TRACKS
        if role == "score"
    }
    actual_xml = {part["id"]: part["name"] for part in xml_parts}
    xml_mapping_ok = len(xml_parts) == 25 and actual_xml == expected_xml
    if not xml_mapping_ok:
        findings.append(
            Finding("ERROR", "MUSICXML_PART_MAPPING", "Expected 25 mapped score parts do not match part-list.")
        )

    mix = {"computed": score_mix_usable}
    if score_mix_usable:
        mix_peak = float(np.max(np.abs(score_mix)))
        peak_db = dbfs(mix_peak)
        clipped = int(np.count_nonzero(np.abs(score_mix) >= 1.0))
        raw_peak_db = 20.0 * math.log10(mix_peak) if mix_peak > 0 else -math.inf
        minimum_attenuation = max(0.0, raw_peak_db)
        recommended_attenuation = max(0.0, raw_peak_db + 1.0)
        mix = {
            "computed": True,
            "score_stem_count": 25,
            "effects_excluded": 4,
            "peak_linear": round(mix_peak, 9),
            "peak_dbfs": peak_db,
            "samples_at_or_above_0_dbfs": clipped,
            "minimum_attenuation_db_to_avoid_clipping": round(minimum_attenuation, 3),
            "recommended_global_attenuation_db_for_minus_1_dbfs_ceiling": round(recommended_attenuation, 3),
        }
        if clipped:
            findings.append(
                Finding(
                    "ERROR",
                    "SCORE_SUM_CLIPPING",
                    f"25-stem sum has {clipped} samples at/above 0 dBFS; apply at least {minimum_attenuation:.2f} dB attenuation.",
                )
            )

    hashes_after = {str(path): sha256(path) for path in input_paths}
    inputs_unchanged = hashes_before == hashes_after
    if not inputs_unchanged:
        findings.append(Finding("ERROR", "INPUT_CHANGED_DURING_CHECK", "Input SHA-256 changed."))

    findings.append(
        Finding(
            "REVIEW",
            "MUSICAL_CONTENT_REQUIRES_LISTENING",
            "Automation cannot prove that each rendered stem contains the correct notes, instrument, articulation, balance, or intended pan position.",
        )
    )
    counts_by_severity = Counter(item.severity for item in findings)
    status = "FAIL" if counts_by_severity["ERROR"] else (
        "PASS WITH WARNINGS" if counts_by_severity["WARNING"] or counts_by_severity["REVIEW"] else "PASS"
    )
    return {
        "status": status,
        "inputs_unchanged": inputs_unchanged,
        "expectations": {
            "wav_count": 29,
            "score_numbers": "01-25",
            "effect_numbers": "26-29",
            "sample_rate_hz": SAMPLE_RATE,
            "bit_depth": BIT_DEPTH,
            "channels": CHANNELS,
            "sample_count": SAMPLE_COUNT,
            "duration_seconds": round(SAMPLE_COUNT / SAMPLE_RATE, 9),
            "tempo_bpm": BPM,
            "time_signature": "4/4",
            "bar_count": BAR_COUNT,
            "samples_per_bar": SAMPLES_PER_BAR,
        },
        "inventory": {
            "directory": str(stems_dir),
            "wav_count": len(wavs),
            "numbers": sorted(numbers),
            "missing_numbers": missing_numbers,
            "unexpected_numbers": unexpected_numbers,
            "duplicate_numbers": duplicates,
            "missing_slugs": missing_slugs,
            "unexpected_slugs": unexpected_slugs,
            "duplicate_slugs": duplicate_slugs,
            "numbering_differences": numbering_differences,
        },
        "musicxml_mapping_ok": xml_mapping_ok,
        "tracks": track_rows,
        "audio_metrics": [metrics_by_file[name] for name in sorted(metrics_by_file)],
        "score_sum": mix,
        "finding_counts": dict(counts_by_severity),
        "findings": [asdict(item) for item in findings],
        "input_sha256": hashes_after,
    }


def render_report(result: dict) -> str:
    status = result["status"]
    inventory = result["inventory"]
    mix = result["score_sum"]
    lines = [
        f"# {status} — Audio Stem Validation",
        "",
        "The WAV and MusicXML inputs were checked read-only; their SHA-256 values were unchanged.",
        "Automated results cover file identity, synchronization, PCM structure and signal statistics. Musical accuracy still requires listening.",
        "",
        "## Summary",
        "",
        f"- WAV count: {inventory['wav_count']} (expected 29).",
        f"- Observed numbers: {inventory['numbers']} (expected 01–29).",
        f"- Missing numbers: {inventory['missing_numbers']}; unexpected numbers: {inventory['unexpected_numbers']}; duplicates: {inventory['duplicate_numbers']}.",
        f"- MusicXML mapping: {'25/25 mapped' if result['musicxml_mapping_ok'] else 'mismatch'}; four `OTH` effects excluded.",
        f"- Score-stem sum peak: {mix.get('peak_dbfs')} dBFS; clipped samples: {mix.get('samples_at_or_above_0_dbfs')}.",
        f"- Suggested global attenuation for a −1 dBFS ceiling: {mix.get('recommended_global_attenuation_db_for_minus_1_dbfs_ceiling')} dB.",
        "",
        "## Findings",
        "",
    ]
    for finding in result["findings"]:
        lines.append(f"- **{finding['severity']} — {finding['code']}**: {finding['message']}")

    lines += [
        "",
        "## Per-file measurements",
        "",
        "| File | Format | Samples | Peak L/R dBFS | RMS L/R dBFS | R−L dB | Corr. | Dual mono | Silent % | Clip |",
        "|---|---:|---:|---:|---:|---:|---:|:---:|---:|---:|",
    ]
    for item in result["audio_metrics"]:
        peak = "/".join("—" if value is None else f"{value:.2f}" for value in item.get("peak_dbfs", []))
        rms = "/".join("—" if value is None else f"{value:.2f}" for value in item.get("rms_dbfs", []))
        balance = item.get("lr_rms_balance_db_right_minus_left")
        correlation = item.get("stereo_correlation")
        lines.append(
            f"| `{item['filename']}` | {item.get('sample_rate_hz')} Hz / {item.get('subtype')} / {item.get('channels')} ch "
            f"| {item.get('sample_count')} | {peak} | {rms} | {balance if balance is not None else '—'} "
            f"| {correlation if correlation is not None else '—'} | {'yes' if item.get('dual_mono') else 'no'} "
            f"| {item.get('silent_frame_percent')} | {item.get('clipped_samples')} |"
        )

    lines += [
        "",
        "`Silent %` means stereo frames at or below −90 dBFS; musical rests and sparse effects can legitimately produce high values.",
        "Correlation and L/R level differences prove channel differences, but do not prove that an intended orchestral pan position is correct.",
        "",
        "## Score-stem ↔ MusicXML mapping",
        "",
        "| Expected | Actual | File | MusicXML part | Included in score sum |",
        "|---:|---:|---|---|:---:|",
    ]
    for track in result["tracks"]:
        part = (
            f"{track['musicxml_part_id']} — {track['musicxml_part_name']}"
            if track["musicxml_part_id"] else "OTH effect (not a score part)"
        )
        lines.append(
            f"| {track['expected_number']:02d} | "
            f"{track['actual_number']:02d} | `{track['filename']}` | {part} "
            f"| {'yes' if track['include_in_score_sum'] else 'no'} |"
        )

    lines += [
        "",
        "## Human confirmation still required",
        "",
        "- Audition every score stem against its MusicXML part for notes, rests, timing, articulation and instrument identity.",
        "- Confirm that the measured L/R balance matches the intended orchestral seating; stereo difference alone is not proof of correct panning.",
        "- Audition bar boundaries and tails, especially effects, percussion, pickup-like attacks and the final release.",
        "- Keep `17_BRS_tb.wav` unchanged under the accepted 01–29 naming convention.",
        "",
    ]
    return "\n".join(lines)


def tracks_manifest(result: dict) -> dict:
    return {
        "draft": True,
        "status": result["status"],
        "base_directory": result["inventory"]["directory"],
        "numbering_note": "Accepted numbering: 01–25 score stems and 26–29 OTH effects; actual filenames are retained.",
        "tracks": result["tracks"],
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    repository = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stems", type=Path, default=repository / "Audio" / "STEMs")
    parser.add_argument(
        "--musicxml",
        type=Path,
        default=repository / "Score-prep" / "Score_Bars16_4-4_144bpm.musicxml",
    )
    parser.add_argument("--report", type=Path, help="Optional Markdown output path")
    parser.add_argument("--tracks-json", type=Path, help="Optional tracks manifest output path")
    parser.add_argument("--bar-times-json", type=Path, help="Optional bar timing output path")
    parser.add_argument("--json", action="store_true", help="Print full result JSON")
    args = parser.parse_args()

    result = validate(args.stems, args.musicxml)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_report(result), encoding="utf-8")
    if args.tracks_json:
        write_json(args.tracks_json, tracks_manifest(result))
    if args.bar_times_json:
        write_json(args.bar_times_json, make_bar_times())

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["status"])
        print(
            f"WAVs={result['inventory']['wav_count']}; "
            f"numbers={result['inventory']['numbers'][0] if result['inventory']['numbers'] else '—'}–"
            f"{result['inventory']['numbers'][-1] if result['inventory']['numbers'] else '—'}; "
            f"score sum={result['score_sum'].get('peak_dbfs')} dBFS"
        )
        for finding in result["findings"]:
            print(f"{finding['severity']}: {finding['code']}: {finding['message']}")
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
