#!/usr/bin/env python3
"""Convert LaTeX or a text-based PDF to DOCX with real Word footnotes.

The LaTeX path is semantic and is the preferred path.  It expands ``\\input`` /
``\\include`` files, normalizes configurable custom footnote commands, lets
Pandoc parse the document into its AST, and then writes a DOCX.

The PDF path is necessarily heuristic because PDF does not normally retain the
relationship between a superscript marker and page-bottom text.  It uses glyph
coordinates, font sizes, and footnote separator rules; every match is recorded
in a JSON review report.  PDF conversion is strict by default.  Use
``--best-effort`` only when you accept low-confidence placements.

External requirements:
  * pandoc 3.x
  * latexpand (recommended for multi-file LaTeX)
  * pdfplumber (PDF input only)

Examples:
  python scripts/footnote_to_docx.py paper.tex -o paper.docx
  python scripts/footnote_to_docx.py paper.pdf -o paper.docx
  python scripts/footnote_to_docx.py scan-ocr.pdf --best-effort --keep-intermediate review
"""

from __future__ import annotations

import argparse
import collections
import copy
import dataclasses
import difflib
import hashlib
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
FOOTNOTE_REL = f"{R_NS}/footnotes"
FOOTNOTE_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument."
    "wordprocessingml.footnotes+xml"
)

DEFAULT_FOOTNOTE_COMMANDS = ("lrfootnote",)
DEFAULT_CITATION_COMMANDS = (
    "artcite",
    "bluecite",
    "bookcite",
    "casecite",
    "statcite",
)
MARKER_RE = re.compile(r"\[\[FN:([A-Za-z0-9_.-]+)\]\]")
RESIDUAL_MARKER_RE = re.compile(r"\[\[(?:FN|EN):[^]]+\]\]")
NOTE_START_RE = re.compile(
    r"^\s*(?:\[(?P<bracket>\d{1,4})\]|"
    r"(?P<number>\d{1,4})(?P<punc>[.)])?\s*|"
    r"(?P<symbol>[*†‡§¶])\s*)"
)
LIGATURES = str.maketrans({"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"})


class ConversionError(RuntimeError):
    """A user-facing conversion failure."""


@dataclasses.dataclass
class PdfLine:
    page: int
    text: str
    x0: float
    x1: float
    top: float
    bottom: float
    median_size: float
    max_size: float
    chars: list[dict[str, Any]]
    replacement_text: str | None = None

    @property
    def visible_text(self) -> str:
        return self.replacement_text if self.replacement_text is not None else self.text


@dataclasses.dataclass
class PdfNote:
    key: str
    page: int
    label: str
    lines: list[str]
    bbox: tuple[float, float, float, float]
    boundary_kind: str
    continued_from_previous_page: bool = False
    matched: bool = False
    last_content_page: int | None = None
    recovered_text: str | None = None
    url_repairs: list[dict[str, str]] = dataclasses.field(default_factory=list)

    @property
    def text(self) -> str:
        return self.recovered_text if self.recovered_text is not None else join_wrapped_lines(self.lines)


@dataclasses.dataclass
class PdfMarker:
    page: int
    label: str
    line: PdfLine
    char_start: int
    char_end: int
    text_start: int | None
    text_end: int | None
    bbox: tuple[float, float, float, float]
    size: float
    raised: float
    adjacent: bool
    plausible: bool
    matched: bool = False
    matched_note_key: str | None = None


@dataclasses.dataclass
class PdfPage:
    number: int
    width: float
    height: float
    body_size: float
    boundary_y: float | None
    boundary_kind: str
    body_lines: list[PdfLine]
    note_lines: list[PdfLine]
    notes: list[PdfNote]
    removed_running_lines: list[PdfLine] = dataclasses.field(default_factory=list)
    suspicious_bottom_lines: list[PdfLine] = dataclasses.field(default_factory=list)
    multi_column: bool = False


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text.translate(LIGATURES)).replace("\u00a0", " ")


def command_path(name_or_path: str, purpose: str) -> str:
    candidate = shutil.which(name_or_path)
    if candidate:
        return candidate
    path = Path(name_or_path).expanduser()
    if path.is_file() and os.access(path, os.X_OK):
        return str(path.resolve())
    raise ConversionError(f"找不到 {purpose}: {name_or_path}")


def run_command(
    args: Sequence[str],
    *,
    cwd: Path,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
    verbose: bool = False,
) -> subprocess.CompletedProcess[str]:
    if verbose:
        eprint("+", " ".join(args))
    completed = subprocess.run(
        list(args),
        cwd=str(cwd),
        input=stdin,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, **(env or {})},
        check=False,
    )
    if completed.returncode != 0:
        details = completed.stderr.strip() or completed.stdout.strip()
        raise ConversionError(
            f"命令失败（退出码 {completed.returncode}）: {' '.join(args)}\n{details}"
        )
    if verbose and completed.stderr.strip():
        eprint(completed.stderr.rstrip())
    return completed


def pandoc_version(pandoc: str, cwd: Path) -> str:
    completed = run_command([pandoc, "--version"], cwd=cwd)
    return completed.stdout.splitlines()[0].strip() if completed.stdout else "pandoc"


def strip_unescaped_comment(line: str) -> tuple[str, str]:
    escaped = False
    for index, char in enumerate(line):
        if char == "\\":
            escaped = not escaped
            continue
        if char == "%" and not escaped:
            return line[:index], line[index:]
        escaped = False
    return line, ""


INCLUDE_RE = re.compile(r"\\(?P<kind>input|include)\s*\{(?P<path>[^{}]+)\}")


def fallback_expand_latex(path: Path, stack: tuple[Path, ...] = ()) -> str:
    resolved = path.resolve()
    if resolved in stack:
        chain = " -> ".join(str(item) for item in (*stack, resolved))
        raise ConversionError(f"LaTeX include 出现循环: {chain}")
    try:
        source = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ConversionError(f"LaTeX 文件不是 UTF-8: {resolved}") from exc

    output: list[str] = []
    for line in source.splitlines(keepends=True):
        code, comment = strip_unescaped_comment(line)

        def replace(match: re.Match[str]) -> str:
            raw_target = match.group("path").strip()
            if "\\" in raw_target:
                return match.group(0)
            target = (resolved.parent / raw_target)
            if not target.suffix:
                target = target.with_suffix(".tex")
            if not target.exists():
                return match.group(0)
            return fallback_expand_latex(target, (*stack, resolved))

        output.append(INCLUDE_RE.sub(replace, code) + comment)
    return "".join(output)


def expand_latex(path: Path, latexpand: str | None, verbose: bool) -> tuple[str, str]:
    if latexpand:
        completed = run_command([latexpand, str(path)], cwd=path.parent, verbose=verbose)
        return completed.stdout, "latexpand"
    return fallback_expand_latex(path), "built-in include expander"


def normalize_latex_commands(
    source: str,
    footnote_commands: Iterable[str],
    citation_commands: Iterable[str],
) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    normalized = source
    for command in footnote_commands:
        if not re.fullmatch(r"[A-Za-z@]+", command):
            raise ConversionError(f"非法 LaTeX 命令名: {command}")
        pattern = re.compile(rf"\\{re.escape(command)}(?=\s*(?:\[|\{{))")
        normalized, count = pattern.subn(r"\\footnote", normalized)
        counts[f"footnote:{command}"] = count
    for command in citation_commands:
        if not re.fullmatch(r"[A-Za-z@]+", command):
            raise ConversionError(f"非法 LaTeX 命令名: {command}")
        pattern = re.compile(rf"\\{re.escape(command)}(?=\s*(?:\[|\{{))")
        normalized, count = pattern.subn(r"\\cite", normalized)
        counts[f"citation:{command}"] = count
    return normalized, counts


def detect_bibliographies(source: str, source_dir: Path) -> list[Path]:
    candidates: list[str] = []
    for match in re.finditer(r"\\addbibresource(?:\[[^]]*\])?\s*\{([^{}]+)\}", source):
        candidates.append(match.group(1).strip())
    for match in re.finditer(r"\\bibliography\s*\{([^{}]+)\}", source):
        candidates.extend(item.strip() for item in match.group(1).split(","))

    resolved: list[Path] = []
    seen: set[Path] = set()
    for raw in candidates:
        item = Path(raw)
        if not item.suffix:
            item = item.with_suffix(".bib")
        if not item.is_absolute():
            item = source_dir / item
        item = item.resolve()
        if item.exists() and item not in seen:
            seen.add(item)
            resolved.append(item)
    return resolved


def count_pandoc_notes(node: Any) -> int:
    if isinstance(node, dict):
        return (1 if node.get("t") == "Note" else 0) + sum(
            count_pandoc_notes(value) for value in node.values()
        )
    if isinstance(node, list):
        return sum(count_pandoc_notes(value) for value in node)
    return 0


def pandoc_note_texts(node: Any) -> list[str]:
    notes: list[str] = []

    def plain(value: Any) -> str:
        if isinstance(value, dict):
            tag = value.get("t")
            if tag == "Str":
                return str(value.get("c", ""))
            if tag in {"Space", "SoftBreak", "LineBreak"}:
                return " "
            return "".join(plain(item) for item in value.values())
        if isinstance(value, list):
            return "".join(plain(item) for item in value)
        return ""

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("t") == "Note":
                notes.append(re.sub(r"\s+", " ", plain(value.get("c", []))).strip())
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(node)
    return notes


def qname(namespace: str, local: str) -> str:
    return f"{{{namespace}}}{local}"


def validate_docx_footnotes(path: Path, expected_count: int | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "path": str(path),
        "valid": False,
        "errors": [],
        "warnings": [],
        "reference_ids": [],
        "definition_ids": [],
        "note_texts": [],
    }
    errors: list[str] = report["errors"]
    try:
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                errors.append(f"DOCX ZIP 成员损坏: {bad_member}")
            names = set(archive.namelist())
            required = {
                "word/document.xml",
                "word/_rels/document.xml.rels",
                "[Content_Types].xml",
            }
            missing = sorted(required - names)
            if missing:
                errors.append("DOCX 缺少必要部件: " + ", ".join(missing))
                return report

            document_root = ET.fromstring(archive.read("word/document.xml"))
            refs = [
                int(element.attrib[qname(W_NS, "id")])
                for element in document_root.findall(f".//{{{W_NS}}}footnoteReference")
                if int(element.attrib.get(qname(W_NS, "id"), "-1")) > 0
            ]
            report["reference_ids"] = refs

            footnotes_root: ET.Element | None = None
            if "word/footnotes.xml" in names:
                footnotes_root = ET.fromstring(archive.read("word/footnotes.xml"))
                if footnotes_root.tag != qname(W_NS, "footnotes"):
                    errors.append("word/footnotes.xml 根元素不是 w:footnotes")
            elif refs or (expected_count or 0) > 0:
                errors.append("存在脚注引用，但缺少 word/footnotes.xml")

            definitions: list[int] = []
            separators: dict[int, list[ET.Element]] = {-1: [], 0: []}
            if footnotes_root is not None:
                for note in footnotes_root.findall(f"{{{W_NS}}}footnote"):
                    raw_id = note.attrib.get(qname(W_NS, "id"), "")
                    try:
                        note_id = int(raw_id)
                    except ValueError:
                        errors.append(f"脚注定义使用非整数 ID: {raw_id!r}")
                        continue
                    if note_id > 0:
                        definitions.append(note_id)
                        if note.find(f".//{{{W_NS}}}footnoteRef") is None:
                            errors.append(f"脚注定义 ID {note_id} 缺少 w:footnoteRef")
                        text = "".join(
                            node.text or "" for node in note.findall(f".//{{{W_NS}}}t")
                        )
                        normalized_text = re.sub(r"\s+", " ", text).strip()
                        report["note_texts"].append(normalized_text)
                        if not normalized_text:
                            errors.append(f"脚注定义 ID {note_id} 没有文本内容")
                    elif note_id in separators:
                        separators[note_id].append(note)
                for special_id, tag in ((-1, "separator"), (0, "continuationSeparator")):
                    items = separators[special_id]
                    if len(items) != 1:
                        errors.append(f"脚注特殊定义 ID {special_id} 应恰好出现一次，实际 {len(items)} 次")
                    elif items[0].find(f".//{{{W_NS}}}{tag}") is None:
                        errors.append(f"脚注特殊定义 ID {special_id} 缺少 w:{tag}")
            report["definition_ids"] = definitions

            if collections.Counter(refs) != collections.Counter(definitions):
                missing_defs = sorted((collections.Counter(refs) - collections.Counter(definitions)).elements())
                orphan_defs = sorted((collections.Counter(definitions) - collections.Counter(refs)).elements())
                if missing_defs:
                    errors.append(f"脚注引用缺少定义: {missing_defs}")
                if orphan_defs:
                    errors.append(f"脚注定义没有正文引用: {orphan_defs}")
            if len(refs) != len(set(refs)):
                errors.append("生成型文档中出现重复脚注引用 ID")
            if len(definitions) != len(set(definitions)):
                errors.append("出现重复脚注定义 ID")
            rels_root = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
            footnote_rels = [
                rel
                for rel in rels_root.findall(f"{{{PKG_REL_NS}}}Relationship")
                if rel.attrib.get("Type") == FOOTNOTE_REL
            ]
            if refs or definitions:
                if len(footnote_rels) != 1:
                    errors.append(f"脚注 relationship 应恰好一个，实际 {len(footnote_rels)} 个")
                else:
                    footnote_rel = footnote_rels[0]
                    if footnote_rel.attrib.get("TargetMode", "Internal") == "External":
                        errors.append("脚注 relationship 不得使用外部 TargetMode")
                    if footnote_rel.attrib.get("Target") not in {
                        "footnotes.xml",
                        "/word/footnotes.xml",
                    }:
                        errors.append(
                            "脚注 relationship Target 错误: "
                            + str(footnote_rel.attrib.get("Target"))
                        )

            types_root = ET.fromstring(archive.read("[Content_Types].xml"))
            overrides = [
                item
                for item in types_root.findall(f"{{{CT_NS}}}Override")
                if item.attrib.get("PartName") == "/word/footnotes.xml"
            ]
            if refs or definitions:
                if len(overrides) != 1:
                    errors.append(f"脚注 Content-Type Override 应恰好一个，实际 {len(overrides)} 个")
                elif overrides[0].attrib.get("ContentType") != FOOTNOTE_CONTENT_TYPE:
                    errors.append("脚注 Content-Type 不正确")

            visible_text = "".join(node.text or "" for node in document_root.findall(f".//{{{W_NS}}}t"))
            if RESIDUAL_MARKER_RE.search(visible_text):
                errors.append("正文仍残留内部脚注 marker")
    except (OSError, zipfile.BadZipFile, ET.ParseError, KeyError, ValueError) as exc:
        errors.append(f"DOCX 结构无法读取: {exc}")

    if expected_count is not None and len(report["reference_ids"]) != expected_count:
        errors.append(
            f"脚注数量不一致：源 AST {expected_count} 条，DOCX {len(report['reference_ids'])} 条"
        )
    report["valid"] = not errors
    return report


def line_font_size(chars: Sequence[dict[str, Any]]) -> tuple[float, float]:
    sizes = [float(char.get("size", 0.0)) for char in chars if str(char.get("text", "")).strip()]
    if not sizes:
        return 0.0, 0.0
    return statistics.median(sizes), max(sizes)


def weighted_body_size(lines: Sequence[PdfLine], page_height: float) -> float:
    counts: collections.Counter[float] = collections.Counter()
    for line in lines:
        if not (page_height * 0.06 <= line.top <= page_height * 0.72):
            continue
        for char in line.chars:
            text = str(char.get("text", ""))
            size = float(char.get("size", 0.0))
            if text.strip() and 5.0 <= size <= 30.0:
                counts[round(size * 2.0) / 2.0] += len(text)
    if not counts:
        return 10.0
    return counts.most_common(1)[0][0]


def is_page_number(line: PdfLine, page_height: float) -> bool:
    return bool(re.fullmatch(r"\s*[ivxlcdmIVXLCDM]*\d*\s*", line.text)) and (
        line.bottom > page_height * 0.90 or line.top < page_height * 0.06
    )


def running_matter_fingerprint(text: str) -> str:
    """Normalize a likely running header/footer while retaining lexical content."""
    value = normalize_text(text).casefold()
    value = re.sub(r"\b(?:\d+|[ivxlcdm]+)\b", "#", value)
    value = re.sub(r"\s+", " ", value).strip(" -–—|·•")
    return value


def recurring_running_matter(
    raw_pages: Sequence[tuple[Any, list[PdfLine]]],
) -> set[tuple[str, str]]:
    """Find stable top/bottom strings repeated across physical PDF pages."""
    if len(raw_pages) < 2:
        return set()
    occurrences: collections.Counter[tuple[str, str]] = collections.Counter()
    for page, lines in raw_pages:
        seen_on_page: set[tuple[str, str]] = set()
        height = float(page.height)
        for line in lines:
            zone: str | None = None
            if line.top < height * 0.09:
                zone = "top"
            elif line.bottom > height * 0.91:
                zone = "bottom"
            if zone is None:
                continue
            fingerprint = running_matter_fingerprint(line.text)
            if fingerprint and fingerprint != "#":
                seen_on_page.add((zone, fingerprint))
        occurrences.update(seen_on_page)
    threshold = max(2, math.ceil(len(raw_pages) * 0.30))
    return {key for key, count in occurrences.items() if count >= threshold}


def is_recurring_running_line(
    line: PdfLine,
    page_height: float,
    recurring: set[tuple[str, str]],
) -> bool:
    if line.top < page_height * 0.09:
        zone = "top"
    elif line.bottom > page_height * 0.91:
        zone = "bottom"
    else:
        return False
    return (zone, running_matter_fingerprint(line.text)) in recurring


def detect_multi_column(lines: Sequence[PdfLine], page_width: float, page_height: float) -> bool:
    """Flag sustained multi-column prose or tabular rows this reflow path cannot order."""
    split_rows: list[PdfLine] = []
    for line in lines:
        visible = [char for char in line.chars if str(char.get("text", "")).strip()]
        for previous, current in zip(visible, visible[1:]):
            gap = float(current.get("x0", 0.0)) - float(previous.get("x1", 0.0))
            if (
                gap >= page_width * 0.08
                and float(previous.get("x1", 0.0)) <= page_width * 0.58
                and float(current.get("x0", 0.0)) >= page_width * 0.42
            ):
                split_rows.append(line)
                break
    if len(split_rows) >= 6:
        span = max(line.bottom for line in split_rows) - min(line.top for line in split_rows)
        if span >= page_height * 0.18:
            return True

    left = [
        line
        for line in lines
        if line.x0 < page_width * 0.20
        and line.x1 <= page_width * 0.58
        and len(line.text) >= 20
    ]
    right = [
        line
        for line in lines
        if page_width * 0.42 <= line.x0 <= page_width * 0.62
        and line.x1 <= page_width * 0.95
        and len(line.text) >= 20
    ]
    if len(left) < 8 or len(right) < 8:
        return False
    left_top, left_bottom = min(line.top for line in left), max(line.bottom for line in left)
    right_top, right_bottom = min(line.top for line in right), max(line.bottom for line in right)
    overlap = max(0.0, min(left_bottom, right_bottom) - max(left_top, right_top))
    return overlap >= page_height * 0.22


def note_label_from_line(line: PdfLine, body_size: float) -> tuple[str, int] | None:
    match = NOTE_START_RE.match(line.text)
    if not match:
        return None
    label = match.group("bracket") or match.group("number") or match.group("symbol")
    if not label:
        return None
    if label.isdigit() and int(label) > 9999:
        return None
    if label.isdigit() and len(label) == 4 and 1800 <= int(label) <= 2200:
        return None

    non_space_chars = [char for char in line.chars if str(char.get("text", "")).strip()]
    label_chars = non_space_chars[: len(label)]
    label_size = statistics.median(
        [float(char.get("size", body_size)) for char in label_chars]
    ) if label_chars else line.median_size
    explicitly_delimited = bool(match.group("bracket") or match.group("punc") or match.group("symbol"))
    remainder = line.text[match.end():].lstrip()
    if match.group("punc") and remainder[:1].isdigit():
        # Decimal/statutory continuations such as ``5.71`` are not new notes.
        return None
    if match.group("symbol") and (
        label_size > body_size * 0.80 or label_size > max(1.0, line.median_size * 0.84)
    ):
        # A baseline section sign at the start of a wrapped citation is not a
        # symbolic footnote marker.
        return None
    if not explicitly_delimited:
        # TeX-style footnote starts are normally a visibly smaller raised number
        # glued to the first word (``12See``).  A continuation line that happens
        # to begin with a year or reporter page is note-size text, not a new note.
        if label_size > body_size * 0.80 or label_size > max(1.0, line.median_size * 0.84):
            return None
    return label, match.end()


def horizontal_rule_candidates(page: Any) -> list[tuple[float, float, float]]:
    candidates: list[tuple[float, float, float]] = []
    graphical_items = [
        *getattr(page, "lines", []),
        *getattr(page, "rects", []),
        *getattr(page, "curves", []),
    ]
    for item in graphical_items:
        width = abs(float(item.get("x1", 0.0)) - float(item.get("x0", 0.0)))
        height = abs(float(item.get("bottom", item.get("top", 0.0))) - float(item.get("top", 0.0)))
        top = float(item.get("top", 0.0))
        x0 = min(float(item.get("x0", 0.0)), float(item.get("x1", 0.0)))
        if (
            height <= 1.5
            and page.width * 0.07 <= width <= page.width * 0.80
            and page.height * 0.30 <= top <= page.height * 0.92
            and x0 <= page.width * 0.40
        ):
            candidates.append((top, x0, width))
    return sorted(set((round(top, 3), round(x0, 3), round(width, 3)) for top, x0, width in candidates))


def choose_note_boundary(page: Any, lines: Sequence[PdfLine], body_size: float) -> tuple[float | None, str]:
    best: tuple[float, float] | None = None
    for top, _x0, width in horizontal_rule_candidates(page):
        nearby = [
            line
            for line in lines
            if top + 1.0 < line.top < min(page.height * 0.94, top + body_size * 7.0)
            and not is_page_number(line, page.height)
        ]
        if not nearby:
            continue
        first = nearby[0]
        has_label = note_label_from_line(first, body_size) is not None
        small_text = any(line.median_size <= body_size * 0.92 for line in nearby[:3])
        if not (has_label or small_text):
            continue
        score = 0.0
        score += 4.0 if has_label else 0.0
        score += 2.0 if small_text else 0.0
        score += 1.5 if page.width * 0.12 <= width <= page.width * 0.45 else 0.0
        score += 1.0 if top >= page.height * 0.48 else 0.0
        score -= min((first.top - top) / max(body_size, 1.0), 3.0) * 0.15
        if best is None or score > best[0]:
            best = (score, top)
    if best is not None:
        return best[1], "separator-rule"

    for line in lines:
        if line.top < page.height * 0.52 or is_page_number(line, page.height):
            continue
        if line.median_size <= body_size * 0.92 and note_label_from_line(line, body_size):
            return line.top - max(1.0, body_size * 0.25), "font-and-label"
    return None, "none"


def pdf_line_from_raw(page_number: int, raw: dict[str, Any]) -> PdfLine:
    chars = list(raw.get("chars", []))
    median_size, max_size = line_font_size(chars)
    return PdfLine(
        page=page_number,
        text=str(raw.get("text", "")).strip(),
        x0=float(raw.get("x0", 0.0)),
        x1=float(raw.get("x1", 0.0)),
        top=float(raw.get("top", 0.0)),
        bottom=float(raw.get("bottom", 0.0)),
        median_size=median_size,
        max_size=max_size,
        chars=chars,
    )


def parse_page_notes(
    page_number: int,
    note_lines: Sequence[PdfLine],
    body_size: float,
    boundary_kind: str,
    previous_note: PdfNote | None,
) -> tuple[list[PdfNote], PdfNote | None, list[str]]:
    notes: list[PdfNote] = []
    warnings: list[str] = []
    current: PdfNote | None = None
    for line in note_lines:
        start = note_label_from_line(line, body_size)
        if start:
            label, end = start
            key = f"p{page_number}n{re.sub(r'[^A-Za-z0-9]+', '-', label).strip('-') or 'symbol'}"
            duplicate = sum(1 for note in notes if note.key == key)
            if duplicate:
                key = f"{key}-{duplicate + 1}"
            content = line.text[end:].strip()
            current = PdfNote(
                key=key,
                page=page_number,
                label=label,
                lines=[content] if content else [],
                bbox=(line.x0, line.top, line.x1, line.bottom),
                boundary_kind=boundary_kind,
                last_content_page=page_number,
            )
            notes.append(current)
            previous_note = current
            continue

        if current is not None:
            current.lines.append(line.text)
            current.bbox = (
                min(current.bbox[0], line.x0),
                min(current.bbox[1], line.top),
                max(current.bbox[2], line.x1),
                max(current.bbox[3], line.bottom),
            )
        elif previous_note is not None and (
            previous_note.last_content_page or previous_note.page
        ) == page_number - 1:
            previous_note.lines.append(line.text)
            previous_note.bbox = (
                min(previous_note.bbox[0], line.x0),
                previous_note.bbox[1],
                max(previous_note.bbox[2], line.x1),
                line.bottom,
            )
            previous_note.continued_from_previous_page = True
            previous_note.last_content_page = page_number
        elif line.text.strip():
            warnings.append(
                f"第 {page_number} 页脚注区有无法归属的非相邻续行: {line.text[:80]!r}"
            )
    return notes, previous_note, warnings


def extract_pdf_pages(path: Path) -> tuple[list[PdfPage], list[str]]:
    try:
        import pdfplumber  # type: ignore
    except ModuleNotFoundError as exc:
        raise ConversionError(
            "PDF 输入需要 pdfplumber。请运行: python -m pip install 'pdfplumber>=0.11'"
        ) from exc

    pages: list[PdfPage] = []
    warnings: list[str] = []
    previous_note: PdfNote | None = None
    total_chars = 0
    with pdfplumber.open(path) as pdf:
        raw_pages: list[tuple[Any, list[PdfLine]]] = []
        for index, page in enumerate(pdf.pages, start=1):
            raw_lines = page.extract_text_lines(
                layout=False,
                return_chars=True,
                strip=False,
                x_tolerance=1.5,
                y_tolerance=3.0,
            )
            lines = [pdf_line_from_raw(index, raw) for raw in raw_lines]
            lines = [line for line in lines if line.text.strip()]
            total_chars += sum(len(line.text) for line in lines)
            raw_pages.append((page, lines))

        recurring = recurring_running_matter(raw_pages)
        for index, (page, raw_lines) in enumerate(raw_pages, start=1):
            page_height = float(page.height)
            removed_running = [
                line
                for line in raw_lines
                if is_page_number(line, page_height)
                or is_recurring_running_line(line, page_height, recurring)
            ]
            lines = [line for line in raw_lines if line not in removed_running]
            body_size = weighted_body_size(lines, page_height)
            boundary_y, boundary_kind = choose_note_boundary(page, lines, body_size)
            body_lines: list[PdfLine] = []
            note_lines: list[PdfLine] = []
            for line in lines:
                if boundary_y is not None and line.top > boundary_y + 0.8 and line.bottom < page.height * 0.95:
                    note_lines.append(line)
                elif boundary_y is None or line.bottom < boundary_y - 0.8:
                    body_lines.append(line)

            notes, previous_note, page_warnings = parse_page_notes(
                index,
                note_lines,
                body_size,
                boundary_kind,
                previous_note,
            )
            warnings.extend(page_warnings)
            suspicious_bottom = []
            if boundary_y is not None and not notes:
                suspicious_bottom = list(note_lines)
            elif boundary_y is None:
                suspicious_bottom = [
                    line
                    for line in body_lines
                    if line.top >= page_height * 0.52
                    and 0 < line.median_size <= body_size * 0.92
                ]
            pages.append(
                PdfPage(
                    number=index,
                    width=float(page.width),
                    height=float(page.height),
                    body_size=body_size,
                    boundary_y=boundary_y,
                    boundary_kind=boundary_kind,
                    body_lines=body_lines,
                    note_lines=note_lines,
                    notes=notes,
                    removed_running_lines=removed_running,
                    suspicious_bottom_lines=suspicious_bottom,
                    multi_column=detect_multi_column(
                        body_lines,
                        float(page.width),
                        page_height,
                    ),
                )
            )
    if not pages:
        raise ConversionError("PDF 没有页面")
    if total_chars < max(20, len(pages) * 8):
        raise ConversionError(
            "PDF 缺少可用文本层，像是扫描件。请先用 OCRmyPDF/Adobe Acrobat OCR，"
            "再重新转换。"
        )
    for note in (note for page in pages for note in page.notes):
        note.recovered_text = join_wrapped_lines(note.lines, note.url_repairs)
    if sum(bool(page.body_lines or page.note_lines) for page in pages) < len(pages):
        blank_pages = [str(page.number) for page in pages if not (page.body_lines or page.note_lines)]
        warnings.append("以下页面没有可用文本层: " + ", ".join(blank_pages[:30]))
    return pages, warnings


def superscript_runs(line: PdfLine, body_size: float) -> list[tuple[str, int, int, tuple[float, float, float, float], float]]:
    chars = line.chars
    normal_bottoms = [
        float(char.get("bottom", 0.0))
        for char in chars
        if str(char.get("text", "")).strip()
        and float(char.get("size", 0.0)) >= body_size * 0.90
    ]
    normal_bottom = statistics.median(normal_bottoms) if normal_bottoms else line.bottom
    runs: list[tuple[str, int, int, tuple[float, float, float, float], float]] = []
    index = 0
    symbols = "*†‡§¶"
    while index < len(chars):
        char = chars[index]
        text = str(char.get("text", ""))
        size = float(char.get("size", 0.0))
        if not (text.isdigit() or text in symbols) or size > body_size * 0.84:
            index += 1
            continue
        start = index
        label = text
        last = char
        index += 1
        while index < len(chars):
            following = chars[index]
            following_text = str(following.get("text", ""))
            gap = float(following.get("x0", 0.0)) - float(last.get("x1", 0.0))
            if (
                following_text.isdigit()
                and float(following.get("size", 0.0)) <= body_size * 0.84
                and gap <= max(2.0, body_size * 0.45)
            ):
                label += following_text
                last = following
                index += 1
            else:
                break
        bbox = (
            float(char.get("x0", 0.0)),
            min(float(item.get("top", 0.0)) for item in chars[start:index]),
            float(last.get("x1", 0.0)),
            max(float(item.get("bottom", 0.0)) for item in chars[start:index]),
        )
        raised = max(0.0, normal_bottom - bbox[3])
        runs.append((label, start, index, bbox, raised))
    return runs


def char_run_to_text_range(line: PdfLine, start: int, end: int) -> tuple[int, int] | None:
    before_count = sum(
        len(str(char.get("text", "")))
        for char in line.chars[:start]
        if str(char.get("text", "")).strip()
    )
    run_count = sum(
        len(str(char.get("text", "")))
        for char in line.chars[start:end]
        if str(char.get("text", "")).strip()
    )
    positions = [index for index, char in enumerate(line.text) if not char.isspace()]
    if run_count <= 0 or not positions:
        return None

    raw = "".join(
        str(char.get("text", ""))
        for char in line.chars
        if str(char.get("text", "")).strip()
    )
    compact_text = "".join(line.text[index] for index in positions)
    target_start = before_count
    target_end = before_count + run_count
    matcher = difflib.SequenceMatcher(None, raw, compact_text, autojunk=False)
    mapped: list[int] = []
    for raw_start, text_start, length in matcher.get_matching_blocks():
        overlap_start = max(target_start, raw_start)
        overlap_end = min(target_end, raw_start + length)
        if overlap_start < overlap_end:
            mapped.extend(
                text_start + (raw_index - raw_start)
                for raw_index in range(overlap_start, overlap_end)
            )
    if len(mapped) == run_count and max(mapped) < len(positions):
        return positions[min(mapped)], positions[max(mapped)] + 1

    # Fallback for damaged font encodings: choose the matching label occurrence
    # closest to the glyph run's relative position in the extracted line.
    label = raw[target_start:target_end]
    occurrences = [match.start() for match in re.finditer(re.escape(label), compact_text)]
    if not occurrences:
        return None
    expected = target_start / max(len(raw), 1)
    chosen = min(occurrences, key=lambda item: abs(item / max(len(compact_text), 1) - expected))
    end_index = chosen + len(label) - 1
    if end_index >= len(positions):
        return None
    return positions[chosen], positions[end_index] + 1


def collect_page_markers(page: PdfPage) -> tuple[list[PdfMarker], list[str]]:
    markers: list[PdfMarker] = []
    warnings: list[str] = []
    for line in sorted(page.body_lines, key=lambda item: (item.top, item.x0)):
        for label, start, end, bbox, raised in superscript_runs(line, page.body_size):
            text_range = char_run_to_text_range(line, start, end)
            first_char = line.chars[start]
            previous_char = next(
                (
                    line.chars[index]
                    for index in range(start - 1, -1, -1)
                    if str(line.chars[index].get("text", "")).strip()
                ),
                None,
            )
            size = float(first_char.get("size", page.body_size))
            adjacent = bool(
                previous_char is not None
                and float(first_char.get("x0", 0.0)) - float(previous_char.get("x1", 0.0))
                <= page.body_size * 0.35
            )
            plausible = bool(
                size <= page.body_size * 0.80
                and raised >= page.body_size * 0.15
                and adjacent
            )
            if text_range is None and plausible:
                warnings.append(f"第 {page.number} 页疑似脚注号 {label} 无法映射回提取文本")
            markers.append(
                PdfMarker(
                    page=page.number,
                    label=label,
                    line=line,
                    char_start=start,
                    char_end=end,
                    text_start=text_range[0] if text_range else None,
                    text_end=text_range[1] if text_range else None,
                    bbox=bbox,
                    size=size,
                    raised=raised,
                    adjacent=adjacent,
                    plausible=plausible,
                )
            )
    return markers, warnings


def marker_review_item(marker: PdfMarker) -> dict[str, Any]:
    return {
        "page": marker.page,
        "label": marker.label,
        "bbox": [round(value, 2) for value in marker.bbox],
        "size": round(marker.size, 3),
        "raised": round(marker.raised, 3),
        "adjacent": marker.adjacent,
        "plausible": marker.plausible,
        "matched": marker.matched,
        "matched_note_key": marker.matched_note_key,
        "line_preview": marker.line.text[:160],
    }


def match_page_notes(
    page: PdfPage,
) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    matches: list[dict[str, Any]] = []
    markers, warnings = collect_page_markers(page)
    cursor = 0
    replacements_by_line: dict[int, tuple[PdfLine, list[tuple[int, int, str]]]] = {}

    # Notes and markers are paired once, in physical reading order.  Exact
    # labels are necessary but not sufficient evidence; unused plausible
    # markers remain visible to strict-mode review.
    for note in page.notes:
        chosen_index: int | None = None
        for index in range(cursor, len(markers)):
            marker = markers[index]
            if (
                not marker.matched
                and marker.label == note.label
                and marker.text_start is not None
                and marker.text_end is not None
            ):
                chosen_index = index
                break
        if chosen_index is None:
            continue
        marker = markers[chosen_index]
        cursor = chosen_index + 1
        marker.matched = True
        marker.matched_note_key = note.key
        note.matched = True
        bucket = replacements_by_line.setdefault(id(marker.line), (marker.line, []))[1]
        bucket.append((marker.text_start, marker.text_end, f"[[FN:{note.key}]]"))

        score = 0.25
        reasons = ["same-page-label", "one-to-one-order-match"]
        if marker.size <= page.body_size * 0.80:
            score += 0.25
            reasons.append("small-superscript-font")
        if marker.raised >= page.body_size * 0.15:
            score += 0.25
            reasons.append("raised-baseline")
        if marker.adjacent:
            score += 0.15
            reasons.append("adjacent-to-body-text")
        if page.boundary_kind == "separator-rule":
            score += 0.10
            reasons.append("separator-rule")
        evidence_score = round(min(score, 1.0), 3)
        matches.append(
            {
                "key": note.key,
                "page": page.number,
                "label": marker.label,
                "evidence_score": evidence_score,
                # Compatibility alias for schema_version=1 consumers.  This is
                # an evidence rubric, not a calibrated probability.
                "confidence": evidence_score,
                "reasons": reasons,
                "marker_bbox": [round(value, 2) for value in marker.bbox],
                "note_bbox": [round(value, 2) for value in note.bbox],
                "note_preview": note.text[:160],
            }
        )

    for line, replacements in replacements_by_line.values():
        text = line.text
        for start_pos, end_pos, replacement in sorted(replacements, reverse=True):
            text = text[:start_pos] + replacement + text[end_pos:]
        line.replacement_text = text
    return matches, warnings, [marker_review_item(marker) for marker in markers]


VISITED_URL_RE = re.compile(
    r"(https?://.*?)(?=\s*\((?:visited|accessed)\b)",
    re.IGNORECASE,
)
OBVIOUS_SPLIT_URL_LEFT_RE = re.compile(r"https?://www$", re.IGNORECASE)
OBVIOUS_SPLIT_URL_RIGHT_RE = re.compile(
    r"^\.[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?:[/:?#]|$)",
    re.IGNORECASE,
)
MALFORMED_INLINE_URL_RE = re.compile(
    r"https?://[^\s<>()\[\]{}]{0,240}\s+"
    r"\.[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?:[/:?#]|$)",
    re.IGNORECASE,
)


def url_continues_across_line(left: str, right: str) -> bool:
    if right.startswith(("(", "[", "{")):
        return False
    return re.search(r"https?://\S*$", left) is not None


def repair_visited_url_whitespace(
    text: str,
    repair_log: list[dict[str, str]] | None = None,
) -> str:
    def replace(match: re.Match[str]) -> str:
        raw = match.group(1)
        repaired = re.sub(r"\s+", "", raw)
        if repaired != raw and repair_log is not None:
            repair_log.append({"kind": "url-whitespace", "before": raw, "after": repaired})
        return repaired

    return VISITED_URL_RE.sub(replace, text)


def join_wrapped_lines(
    lines: Sequence[str],
    repair_log: list[dict[str, str]] | None = None,
) -> str:
    result = ""
    for raw in lines:
        text = normalize_text(raw.strip())
        if not text:
            continue
        if not result:
            result = text
        elif result.endswith("-") and text[:1].islower():
            # Preserve the source glyph.  A visible line-end hyphen may be a
            # semantic compound (``high-impact``), not a discretionary break.
            result += text
        elif url_continues_across_line(result, text):
            if repair_log is not None:
                repair_log.append(
                    {"kind": "url-line-wrap", "before": result[-80:] + " | " + text[:80], "after": "joined"}
                )
            result += text
        elif result.endswith(("/", "–", "—")):
            result += text
        else:
            result += " " + text
    result = repair_visited_url_whitespace(result, repair_log)
    return re.sub(r"\s+", " ", result).strip()


def line_is_heading(line: PdfLine, body_size: float) -> int | None:
    text = line.visible_text.strip()
    if not text or MARKER_RE.fullmatch(text):
        return None
    if line.max_size >= body_size * 1.75 and len(text) <= 180:
        return 1
    if line.max_size >= body_size * 1.28 and len(text) <= 180:
        return 2
    if len(text) <= 100 and text.isupper() and sum(char.isalpha() for char in text) >= 4:
        return 2
    return None


def page_paragraphs(
    page: PdfPage,
    preserved_hyphens: list[dict[str, Any]],
    url_repairs: list[dict[str, Any]] | None = None,
) -> list[tuple[str, int | None]]:
    lines = sorted(page.body_lines, key=lambda line: (line.top, line.x0))
    if not lines:
        return []
    ordinary = [line for line in lines if line_is_heading(line, page.body_size) is None]
    deltas = [
        current.top - previous.top
        for previous, current in zip(ordinary, ordinary[1:])
        if 0 < current.top - previous.top < page.body_size * 4.0
    ]
    typical_delta = statistics.median(deltas) if deltas else page.body_size * 1.25
    text_left = min((line.x0 for line in ordinary), default=min(line.x0 for line in lines))

    output: list[tuple[str, int | None]] = []
    current_text = ""
    previous: PdfLine | None = None

    def flush() -> None:
        nonlocal current_text
        if current_text.strip():
            current_text = repair_visited_url_whitespace(current_text, url_repairs)
            output.append((normalize_text(re.sub(r"\s+", " ", current_text).strip()), None))
        current_text = ""

    for line in lines:
        heading_level = line_is_heading(line, page.body_size)
        if heading_level is not None:
            flush()
            output.append((normalize_text(line.visible_text.strip()), heading_level))
            previous = line
            continue

        starts_new = False
        if previous is not None:
            gap = line.top - previous.top
            starts_new = gap > typical_delta * 1.38
            if line.x0 > text_left + page.body_size * 1.35 and previous.x0 <= text_left + page.body_size * 0.5:
                starts_new = True
        if starts_new:
            flush()

        text = line.visible_text.strip()
        if not current_text:
            current_text = text
        elif current_text.endswith("-") and text[:1].islower():
            preserved_hyphens.append(
                {
                    "page": page.number,
                    "left": current_text[-40:],
                    "right": text[:40],
                }
            )
            current_text += text
        elif url_continues_across_line(current_text, text):
            if url_repairs is not None:
                url_repairs.append(
                    {
                        "kind": "url-line-wrap",
                        "page": page.number,
                        "before": current_text[-80:] + " | " + text[:80],
                        "after": "joined",
                    }
                )
            current_text += text
        else:
            current_text += " " + text
        previous = line
    flush()
    return output


def repair_split_body_urls(
    paragraphs: Sequence[tuple[int, str, int | None]],
    repair_log: list[dict[str, Any]] | None = None,
) -> list[tuple[int, str, int | None]]:
    """Join only unmistakable URL splits across paragraph or page boundaries."""
    repaired: list[tuple[int, str, int | None]] = []
    for page, text, heading in paragraphs:
        if repaired:
            previous_page, previous_text, previous_heading = repaired[-1]
            adjacent_page = page in {previous_page, previous_page + 1}
            if (
                heading is None
                and previous_heading is None
                and adjacent_page
                and OBVIOUS_SPLIT_URL_LEFT_RE.search(previous_text)
                and OBVIOUS_SPLIT_URL_RIGHT_RE.match(text)
            ):
                joined = repair_visited_url_whitespace(previous_text + text, repair_log)
                repaired[-1] = (previous_page, joined, None)
                if repair_log is not None:
                    repair_log.append(
                        {
                            "kind": (
                                "url-page-wrap"
                                if page == previous_page + 1
                                else "url-paragraph-wrap"
                            ),
                            "page": previous_page,
                            "next_page": page,
                            "before": previous_text[-80:] + " | " + text[:80],
                            "after": "joined",
                        }
                    )
                continue
        repaired.append((page, text, heading))
    return repaired


def malformed_url_preview(text: str, offset: int) -> str:
    start = max(0, offset - 60)
    end = min(len(text), offset + 180)
    return text[start:end]


def find_residual_malformed_urls(
    paragraphs: Sequence[tuple[int, str, int | None]],
    notes: Sequence[PdfNote],
) -> list[dict[str, Any]]:
    """Inventory URL damage that remains after conservative automatic repairs."""
    findings: list[dict[str, Any]] = []
    for index, (page, text, _heading) in enumerate(paragraphs):
        for match in MALFORMED_INLINE_URL_RE.finditer(text):
            findings.append(
                {
                    "scope": "body",
                    "page": page,
                    "kind": "whitespace-before-domain-continuation",
                    "preview": malformed_url_preview(text, match.start()),
                }
            )
        incomplete = OBVIOUS_SPLIT_URL_LEFT_RE.search(text)
        if incomplete is None:
            continue
        next_page: int | None = None
        next_preview = ""
        kind = "incomplete-url-prefix"
        if index + 1 < len(paragraphs):
            candidate_page, candidate_text, _candidate_heading = paragraphs[index + 1]
            if OBVIOUS_SPLIT_URL_RIGHT_RE.match(candidate_text):
                next_page = candidate_page
                next_preview = candidate_text[:120]
                kind = "split-url-boundary"
        item: dict[str, Any] = {
            "scope": "body",
            "page": page,
            "kind": kind,
            "preview": malformed_url_preview(text, incomplete.start()),
        }
        if next_page is not None:
            item["next_page"] = next_page
            item["next_preview"] = next_preview
        findings.append(item)

    for note in notes:
        text = note.text
        for match in MALFORMED_INLINE_URL_RE.finditer(text):
            findings.append(
                {
                    "scope": f"footnote:{note.label}",
                    "page": note.page,
                    "kind": "whitespace-before-domain-continuation",
                    "preview": malformed_url_preview(text, match.start()),
                }
            )
        incomplete = OBVIOUS_SPLIT_URL_LEFT_RE.search(text)
        if incomplete is not None:
            findings.append(
                {
                    "scope": f"footnote:{note.label}",
                    "page": note.page,
                    "kind": "incomplete-url-prefix",
                    "preview": malformed_url_preview(text, incomplete.start()),
                }
            )
    return findings


def text_inlines(text: str) -> list[dict[str, Any]]:
    inlines: list[dict[str, Any]] = []
    for token in re.split(r"(\s+)", normalize_text(text)):
        if not token:
            continue
        if token.isspace():
            if inlines and inlines[-1].get("t") != "Space":
                inlines.append({"t": "Space"})
        else:
            inlines.append({"t": "Str", "c": token})
    if inlines and inlines[-1].get("t") == "Space":
        inlines.pop()
    return inlines


def inlines_with_notes(text: str, notes: dict[str, PdfNote]) -> list[dict[str, Any]]:
    inlines: list[dict[str, Any]] = []
    cursor = 0
    for match in MARKER_RE.finditer(text):
        inlines.extend(text_inlines(text[cursor:match.start()]))
        key = match.group(1)
        note = notes.get(key)
        if note is None:
            raise ConversionError(f"内部错误：找不到脚注 marker 对应内容 {key}")
        inlines.append(
            {
                "t": "Note",
                "c": [{"t": "Para", "c": text_inlines(note.text)}],
            }
        )
        cursor = match.end()
    inlines.extend(text_inlines(text[cursor:]))
    return inlines


def pandoc_api_version(pandoc: str, cwd: Path) -> list[int]:
    completed = run_command([pandoc, "-f", "markdown", "-t", "json"], cwd=cwd, stdin="")
    parsed = json.loads(completed.stdout)
    return list(parsed["pandoc-api-version"])


SUPRA_INFRA_RE = re.compile(r"\b(?:supra|infra)\s+notes?\s+\d+\b", re.IGNORECASE)


def pdf_numbering_issues(notes: Sequence[PdfNote]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    mapping: list[dict[str, Any]] = []
    expected = 1
    for output_number, note in enumerate(notes, start=1):
        mapping.append(
            {
                "key": note.key,
                "page": note.page,
                "source_label": note.label,
                "output_number": output_number,
            }
        )
        if not note.label.isdigit():
            issues.append(
                {
                    "page": note.page,
                    "label": note.label,
                    "kind": "non-numeric-source-label",
                }
            )
            continue
        value = int(note.label)
        if value != expected:
            issues.append(
                {
                    "page": note.page,
                    "label": note.label,
                    "expected": str(expected),
                    "kind": "reset-gap-or-non-one-start",
                }
            )
        expected = value + 1
    return issues, mapping


def find_supra_infra_references(pages: Sequence[PdfPage]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for page in pages:
        for line in page.body_lines:
            for match in SUPRA_INFRA_RE.finditer(line.visible_text):
                findings.append(
                    {"page": page.number, "scope": "body", "text": match.group(0)}
                )
        for note in page.notes:
            for match in SUPRA_INFRA_RE.finditer(note.text):
                findings.append(
                    {
                        "page": page.number,
                        "scope": f"footnote:{note.label}",
                        "text": match.group(0),
                    }
                )
    return findings


def pdf_to_pandoc_ast(
    path: Path,
    pandoc: str,
    *,
    strict: bool,
    min_confidence: float,
    verbose: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    pages, warnings = extract_pdf_pages(path)
    all_notes: dict[str, PdfNote] = {}
    all_matches: list[dict[str, Any]] = []
    marker_candidates: list[dict[str, Any]] = []
    for page in pages:
        for note in page.notes:
            all_notes[note.key] = note
        matches, page_warnings, page_markers = match_page_notes(page)
        all_matches.extend(matches)
        marker_candidates.extend(page_markers)
        warnings.extend(page_warnings)

    unmatched = [note for note in all_notes.values() if not note.matched]
    if unmatched and not strict:
        for note in unmatched:
            page = pages[note.page - 1]
            if not page.body_lines:
                warnings.append(f"第 {note.page} 页脚注 {note.label} 无正文可附着，已跳过")
                continue
            target = page.body_lines[-1]
            target.replacement_text = target.visible_text.rstrip() + f" [[FN:{note.key}]]"
            note.matched = True
            all_matches.append(
                {
                    "key": note.key,
                    "page": note.page,
                    "label": note.label,
                    "evidence_score": 0.4,
                    "confidence": 0.4,
                    "reasons": ["best-effort-end-of-page-placement"],
                    "marker_bbox": None,
                    "note_bbox": [round(value, 2) for value in note.bbox],
                    "note_preview": note.text[:160],
                }
            )
            warnings.append(
                f"第 {note.page} 页脚注 {note.label} 未找到正文标记，已按 best-effort 附到该页正文末尾"
            )

    unmatched_after = [note for note in all_notes.values() if not note.matched]
    low_confidence = [
        match
        for match in all_matches
        if match.get("evidence_score", match["confidence"]) < min_confidence
    ]
    unmatched_markers = [
        marker for marker in marker_candidates if marker["plausible"] and not marker["matched"]
    ]
    suspicious_bottom = [
        {
            "page": page.number,
            "boundary_kind": page.boundary_kind,
            "lines": [line.text[:160] for line in page.suspicious_bottom_lines[:10]],
        }
        for page in pages
        if page.suspicious_bottom_lines
    ]
    multi_column_pages = [page.number for page in pages if page.multi_column]
    ordered_notes = list(all_notes.values())
    numbering_issues, numbering_map = pdf_numbering_issues(ordered_notes)
    supra_infra_references = find_supra_infra_references(pages)
    preserved_hyphens: list[dict[str, Any]] = []
    body_url_repairs: list[dict[str, Any]] = []
    body_paragraphs: list[tuple[int, str, int | None]] = []
    for page in pages:
        body_paragraphs.extend(
            (page.number, text, heading)
            for text, heading in page_paragraphs(
                page,
                preserved_hyphens,
                body_url_repairs,
            )
            if text
        )
    body_paragraphs = repair_split_body_urls(body_paragraphs, body_url_repairs)
    residual_malformed_urls = find_residual_malformed_urls(
        body_paragraphs,
        ordered_notes,
    )
    strict_zero_notes = not ordered_notes
    if strict and (
        strict_zero_notes
        or unmatched_after
        or low_confidence
        or unmatched_markers
        or suspicious_bottom
        or multi_column_pages
        or numbering_issues
        or supra_infra_references
        or residual_malformed_urls
    ):
        details: list[str] = []
        if strict_zero_notes:
            details.append("没有检测到任何脚注，无法验证源 PDF 确实无脚注")
        if unmatched_after:
            details.append(
                "未配对脚注: "
                + ", ".join(f"p{note.page}:{note.label}" for note in unmatched_after[:20])
            )
        if low_confidence:
            details.append(
                "低置信度匹配: "
                + ", ".join(
                    f"p{item['page']}:{item['label']}={item['confidence']}"
                    for item in low_confidence[:20]
                )
            )
        if unmatched_markers:
            details.append(
                "未配对疑似正文脚注号: "
                + ", ".join(
                    f"p{item['page']}:{item['label']}" for item in unmatched_markers[:20]
                )
            )
        if suspicious_bottom:
            details.append(
                "页底存在未解释的小字或脚注区证据: "
                + ", ".join(f"p{item['page']}" for item in suspicious_bottom[:20])
            )
        if multi_column_pages:
            details.append(
                "检测到当前 PDF 重排器不支持的双栏或多列表格版面: "
                + ", ".join(map(str, multi_column_pages[:20]))
            )
        if numbering_issues:
            details.append(
                "源脚注编号不是从 1 连续递增，Word 自动编号会改变引用: "
                + ", ".join(
                    f"p{item['page']}:{item['label']}" for item in numbering_issues[:20]
                )
            )
        if supra_infra_references:
            details.append(
                f"检测到 {len(supra_infra_references)} 处 supra/infra note 文字引用，"
                "无法由 PDF 路径证明重编号后仍正确"
            )
        if residual_malformed_urls:
            details.append(
                f"自动修复后仍有 {len(residual_malformed_urls)} 处疑似断裂 URL"
            )
        raise ConversionError(
            "PDF 严格模式拒绝含歧义的脚注恢复。" + "；".join(details)
            + "。如已人工接受风险，可使用 --best-effort。"
        )

    blocks: list[dict[str, Any]] = []
    for _page, text, heading in body_paragraphs:
        inline = inlines_with_notes(text, all_notes)
        if heading is not None:
            blocks.append({"t": "Header", "c": [heading, ["", [], []], inline]})
        else:
            blocks.append({"t": "Para", "c": inline})

    note_url_repairs = [
        {"page": note.page, "note": note.label, **repair}
        for note in ordered_notes
        for repair in note.url_repairs
    ]
    url_repairs = [*note_url_repairs, *body_url_repairs]
    if url_repairs:
        warnings.append(
            f"自动拼接或清理了 {len(url_repairs)} 处跨行 URL；请在审阅报告中复核"
        )
    if unmatched_markers and not strict:
        warnings.append(
            f"有 {len(unmatched_markers)} 个疑似正文脚注号未配对；best-effort 未删除这些字符"
        )
    if suspicious_bottom and not strict:
        warnings.append(
            f"有 {len(suspicious_bottom)} 页存在未解释的页底小字或脚注区证据"
        )
    if multi_column_pages and not strict:
        warnings.append(
            "双栏或多列表格页面可能按行交错: "
            + ", ".join(map(str, multi_column_pages[:20]))
        )
    if numbering_issues and not strict:
        warnings.append("源脚注编号会被 Word 连续重编号；请核对 numbering_map")
    if supra_infra_references and not strict:
        warnings.append("检测到 supra/infra note 文字引用；请按 numbering_map 人工核对")
    if residual_malformed_urls and not strict:
        warnings.append(
            f"自动修复后仍有 {len(residual_malformed_urls)} 处疑似断裂 URL；"
            "请按 residual_malformed_urls 人工核对"
        )

    ast = {
        "pandoc-api-version": pandoc_api_version(pandoc, path.parent),
        "meta": {},
        "blocks": blocks,
    }
    review = {
        "pdf_pages": len(pages),
        "detected_notes": len(all_notes),
        "matched_notes": sum(1 for note in all_notes.values() if note.matched),
        "unmatched_notes": [
            {"page": note.page, "label": note.label, "preview": note.text[:160]}
            for note in unmatched_after
        ],
        "min_confidence": min_confidence,
        "score_semantics": (
            "evidence_score/confidence 是启发式证据分，不是校准后的正确概率；"
            "confidence 仅为 schema_version=1 兼容别名"
        ),
        "matches": all_matches,
        "marker_candidates": marker_candidates,
        "unmatched_markers": unmatched_markers,
        "suspicious_bottom_evidence": suspicious_bottom,
        "multi_column_pages": multi_column_pages,
        "numbering_issues": numbering_issues,
        "numbering_map": numbering_map,
        "supra_infra_references": supra_infra_references,
        "dehyphenations": [],
        "preserved_line_end_hyphens": preserved_hyphens,
        "url_repairs": url_repairs,
        "residual_malformed_urls": residual_malformed_urls,
        "removed_running_matter": [
            {
                "page": page.number,
                "text": line.text,
                "bbox": [round(line.x0, 2), round(line.top, 2), round(line.x1, 2), round(line.bottom, 2)],
            }
            for page in pages
            for line in page.removed_running_lines
        ],
        "pages": [
            {
                "page": page.number,
                "body_font_size": page.body_size,
                "footnote_boundary": page.boundary_y,
                "boundary_kind": page.boundary_kind,
                "detected_note_labels": [note.label for note in page.notes],
                "removed_running_lines": [line.text for line in page.removed_running_lines],
                "suspicious_bottom_lines": [line.text[:160] for line in page.suspicious_bottom_lines],
                "multi_column": page.multi_column,
            }
            for page in pages
        ],
        "warnings": warnings,
    }
    if verbose:
        eprint(
            f"PDF: {len(pages)} pages, {len(all_notes)} notes, "
            f"{len(all_matches)} placements"
        )
    return ast, review


def convert_ast_to_docx(
    ast_path: Path,
    docx_path: Path,
    pandoc: str,
    *,
    cwd: Path,
    reference_doc: Path | None,
    bibliographies: Sequence[Path] = (),
    csl: Path | None = None,
    citeproc: bool = False,
    resource_paths: Sequence[Path] = (),
    verbose: bool = False,
) -> str:
    args = [pandoc, str(ast_path), "--from=json", "--to=docx", "--standalone", "--output", str(docx_path)]
    if reference_doc:
        args.extend(["--reference-doc", str(reference_doc)])
    if resource_paths:
        args.extend(["--resource-path", os.pathsep.join(str(path) for path in resource_paths)])
    if citeproc:
        args.append("--citeproc")
        for bibliography in bibliographies:
            args.extend(["--bibliography", str(bibliography)])
        if csl:
            args.extend(["--csl", str(csl)])
    completed = run_command(args, cwd=cwd, verbose=verbose)
    return completed.stderr.strip()


def convert_latex_pandoc(
    source: Path,
    stage: Path,
    args: argparse.Namespace,
    pandoc: str,
) -> tuple[Path, dict[str, Any], int]:
    latexpand: str | None
    if args.no_latexpand:
        latexpand = None
    else:
        latexpand = shutil.which(args.latexpand)
    expanded, expander = expand_latex(source, latexpand, args.verbose)
    footnote_commands = tuple(dict.fromkeys((*DEFAULT_FOOTNOTE_COMMANDS, *args.footnote_command)))
    citation_commands = tuple(dict.fromkeys((*DEFAULT_CITATION_COMMANDS, *args.citation_command)))
    normalized, macro_counts = normalize_latex_commands(
        expanded,
        footnote_commands,
        citation_commands,
    )
    normalized_path = stage / "expanded.normalized.tex"
    normalized_path.write_text(normalized, encoding="utf-8")

    detected_bibs = detect_bibliographies(expanded, source.parent)
    explicit_bibs = [Path(item).expanduser().resolve() for item in args.bibliography]
    missing_bibs = [path for path in explicit_bibs if not path.exists()]
    if missing_bibs:
        raise ConversionError("找不到 bibliography: " + ", ".join(map(str, missing_bibs)))
    bibliographies = list(dict.fromkeys((*explicit_bibs, *detected_bibs)))

    ast_path = stage / "source.ast.json"
    parse_args = [
        pandoc,
        str(normalized_path),
        "--from=latex",
        "--to=json",
        "--standalone",
        "--output",
        str(ast_path),
        "--resource-path",
        os.pathsep.join(dict.fromkeys((str(source.parent), str(Path.cwd())))),
    ]
    parse_completed = run_command(parse_args, cwd=source.parent, verbose=args.verbose)
    ast = json.loads(ast_path.read_text(encoding="utf-8"))
    source_note_count = count_pandoc_notes(ast)
    source_note_texts = pandoc_note_texts(ast)
    if source_note_count == 0 and re.search(r"\\(?:footnote|footnotemark|footnotetext)\b", normalized):
        raise ConversionError(
            "源文件包含脚注命令，但 Pandoc AST 中没有脚注；转换已停止，以免静默丢注。"
        )

    staged_docx = stage / "converted.docx"
    output_warnings = convert_ast_to_docx(
        ast_path,
        staged_docx,
        pandoc,
        cwd=source.parent,
        reference_doc=args.reference_doc,
        bibliographies=bibliographies,
        csl=args.csl,
        citeproc=not args.no_citeproc and bool(bibliographies),
        resource_paths=(source.parent, Path.cwd()),
        verbose=args.verbose,
    )
    review = {
        "expander": expander,
        "macro_replacements": macro_counts,
        "detected_bibliographies": [str(path) for path in bibliographies],
        "pandoc_ast_notes": source_note_count,
        "pandoc_note_previews": [text[:200] for text in source_note_texts[:20]],
        "pandoc_parse_warnings": parse_completed.stderr.strip(),
        "pandoc_output_warnings": output_warnings,
    }
    review["latex_backend"] = "pandoc"
    return staged_docx, review, source_note_count


def tex_search_path(source_dir: Path) -> str:
    """Return a kpathsea path that includes the source tree and defaults."""
    return os.pathsep.join((".", str(source_dir), str(source_dir) + "//", ""))


def build_file_digest(directory: Path, stem: str) -> str:
    digest = hashlib.sha256()
    found = False
    for suffix in (".aux", ".toc", ".out", ".xref", ".bcf"):
        path = directory / f"{stem}{suffix}"
        if path.exists():
            found = True
            digest.update(path.name.encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest() if found else ""


def remove_element_preserving_tail(element: Any) -> None:
    parent = element.getparent()
    if parent is None:
        return
    previous = element.getprevious()
    tail = element.tail or ""
    parent.remove(element)
    if previous is None:
        parent.text = (parent.text or "") + tail
    else:
        previous.tail = (previous.tail or "") + tail


def merge_tex4ht_footnotes(main_html: Path, merged_html: Path) -> tuple[int, list[str]]:
    try:
        from lxml import etree, html  # type: ignore
    except ModuleNotFoundError as exc:
        raise ConversionError(
            "TeX4ht 后端需要 lxml。请运行: python -m pip install 'lxml>=5'"
        ) from exc

    base = main_html.parent.resolve()
    root = html.parse(str(main_html)).getroot()
    refs = root.xpath('//a[@role="doc-noteref" and not(ancestor::aside[@role="doc-footnote"])]')
    if not refs:
        # Older TeX4ht sometimes omits role on the body reference.
        refs = root.xpath(
            '//span[contains(concat(" ",normalize-space(@class)," "),'
            '" footnote-mark ")]/a[starts-with(@href,"#fn") '
            'and not(ancestor::aside[@role="doc-footnote"])]'
        )

    body_nodes = root.xpath("//body")
    if len(body_nodes) != 1:
        raise ConversionError(f"TeX4ht 主 HTML 应有一个 body，实际 {len(body_nodes)} 个")

    section = html.Element(
        "section",
        id="footnotes",
        **{
            "class": "footnotes footnotes-end-of-document",
            "role": "doc-endnotes",
        },
    )
    section.append(html.Element("hr"))
    ordered = html.Element("ol")
    section.append(ordered)

    source_asides: list[Any] = []
    previews: list[str] = []
    for number, ref in enumerate(refs, start=1):
        href = str(ref.get("href") or "")
        if "#" not in href:
            raise ConversionError(f"TeX4ht 脚注链接没有 fragment: {href!r}")
        relative, fragment = href.split("#", 1)
        if relative:
            note_path = (base / relative).resolve()
            try:
                note_path.relative_to(base)
            except ValueError as exc:
                raise ConversionError(f"TeX4ht 脚注链接越出输出目录: {relative}") from exc
            if not note_path.is_file():
                raise ConversionError(f"TeX4ht 脚注文件不存在: {note_path}")
            note_root = html.parse(str(note_path)).getroot()
        else:
            note_root = root

        targets = note_root.xpath('//*[@id=$fragment]', fragment=fragment)
        if len(targets) != 1:
            raise ConversionError(
                f"TeX4ht 脚注目标 {href!r} 应唯一，实际 {len(targets)} 个"
            )
        asides = targets[0].xpath('ancestor-or-self::aside[@role="doc-footnote"]')
        if len(asides) != 1:
            raise ConversionError(f"TeX4ht 脚注目标不在 doc-footnote aside 中: {href}")
        aside = asides[0]
        if note_root is root:
            source_asides.append(aside)

        item = html.Element("li", id=f"fn{number}", role="doc-endnote")
        for child in aside:
            if isinstance(child.tag, str):
                item.append(copy.deepcopy(child))
        if len(item) == 0:
            paragraph = html.Element("p")
            paragraph.text = aside.text_content()
            item.append(paragraph)

        marks = item.xpath(
            './/*[contains(concat(" ",normalize-space(@class)," ")," footnote-mark ")]'
        )
        for mark in marks:
            remove_element_preserving_tail(mark)
        back = html.Element(
            "a",
            href=f"#fnref{number}",
            **{"class": "footnote-back", "role": "doc-backlink"},
        )
        back.text = "↩︎"
        if len(item):
            item[-1].append(back)
        else:
            item.append(back)
        ordered.append(item)
        preview = re.sub(r"\s+", " ", item.text_content()).strip()
        previews.append(preview[:200])

        new_ref = html.Element(
            "a",
            href=f"#fn{number}",
            id=f"fnref{number}",
            **{"class": "footnote-ref", "role": "doc-noteref"},
        )
        for child in ref:
            new_ref.append(copy.deepcopy(child))
        if len(new_ref) == 0:
            new_ref.text = ref.text_content() or str(number)
        wrapper = ref.getparent()
        if (
            wrapper is not None
            and wrapper.tag == "span"
            and "footnote-mark" in str(wrapper.get("class") or "").split()
        ):
            new_ref.tail = wrapper.tail
            wrapper.getparent().replace(wrapper, new_ref)
        else:
            ref.getparent().replace(ref, new_ref)

    # fn-in leaves the original asides at the end.  Remove them after copying so
    # Pandoc sees one canonical footnote section, not duplicate visible notes.
    seen_asides: set[int] = set()
    for aside in source_asides:
        identity = id(aside)
        if identity in seen_asides:
            continue
        seen_asides.add(identity)
        parent = aside.getparent()
        if parent is not None:
            parent.remove(aside)
    for container in root.xpath(
        '//*[contains(concat(" ",normalize-space(@class)," ")," footnotes ")]'
    ):
        if container is section:
            continue
        if not container.xpath('.//aside[@role="doc-footnote"]') and not container.text_content().strip():
            parent = container.getparent()
            if parent is not None:
                parent.remove(container)

    body_nodes[0].append(section)
    merged_html.write_bytes(
        etree.tostring(root, encoding="utf-8", method="html", doctype="<!DOCTYPE html>")
    )
    return len(refs), previews


def find_unique_tex4ht_main(html_dir: Path, stem: str) -> Path:
    candidates = [path for path in html_dir.rglob(f"{stem}.html") if path.is_file()]
    if len(candidates) != 1:
        raise ConversionError(
            f"TeX4ht 主 HTML 应唯一，实际 {len(candidates)} 个: "
            + ", ".join(str(path) for path in candidates[:10])
        )
    return candidates[0]


def convert_svg_images_for_docx(
    merged_html: Path,
    search_dirs: Sequence[Path],
    *,
    verbose: bool,
) -> tuple[list[dict[str, str]], list[str]]:
    """Create PNG fallbacks for SVGs when Pandoc lacks an SVG converter."""
    try:
        from lxml import etree, html  # type: ignore
    except ModuleNotFoundError as exc:
        raise ConversionError("SVG fallback processing needs lxml") from exc

    root = html.parse(str(merged_html)).getroot()
    converted: list[dict[str, str]] = []
    warnings: list[str] = []
    rsvg = shutil.which("rsvg-convert")
    mutool = shutil.which("mutool")
    sips = shutil.which("sips")
    changed = False
    for image in root.xpath("//img[@src]"):
        raw_src = str(image.get("src") or "")
        if not raw_src.lower().split("?", 1)[0].endswith(".svg"):
            continue
        source_svg: Path | None = None
        for directory in search_dirs:
            candidate = (directory / raw_src).resolve()
            if candidate.is_file():
                source_svg = candidate
                break
        if source_svg is None:
            warnings.append(f"找不到 SVG 资源: {raw_src}")
            continue
        output_png = source_svg.with_suffix(source_svg.suffix + ".png")
        if rsvg:
            run_command(
                [rsvg, "--output", str(output_png), str(source_svg)],
                cwd=source_svg.parent,
                verbose=verbose,
            )
            converter = "rsvg-convert"
        elif mutool:
            run_command(
                [mutool, "draw", "-o", str(output_png), "-r", "150", str(source_svg)],
                cwd=source_svg.parent,
                verbose=verbose,
            )
            converter = "mutool"
        elif sips:
            run_command(
                [sips, "-s", "format", "png", str(source_svg), "--out", str(output_png)],
                cwd=source_svg.parent,
                verbose=verbose,
            )
            converter = "sips"
        else:
            warnings.append(
                f"没有 rsvg-convert/mutool/sips，DOCX 可能跳过 SVG: {source_svg.name}"
            )
            continue
        image.set("src", output_png.name)
        changed = True
        converted.append(
            {"source": str(source_svg), "output": str(output_png), "converter": converter}
        )
    if changed:
        merged_html.write_bytes(
            etree.tostring(root, encoding="utf-8", method="html", doctype="<!DOCTYPE html>")
        )
    return converted, warnings


def convert_latex_make4ht(
    source: Path,
    stage: Path,
    args: argparse.Namespace,
    pandoc: str,
) -> tuple[Path, dict[str, Any], int]:
    make4ht = command_path(args.make4ht, "make4ht")
    biber = shutil.which(args.biber)
    build_dir = stage / "tex4ht-build"
    html_dir = stage / "tex4ht-html"
    build_dir.mkdir()
    html_dir.mkdir()
    tex_env = {
        "TEXINPUTS": tex_search_path(source.parent),
        "BIBINPUTS": os.pathsep.join((str(source.parent), str(source.parent) + "//", "")),
    }

    make_args = [
        make4ht,
        "-f",
        "html5",
        "-B",
        str(build_dir),
        "-d",
        str(html_dir),
        source.name,
        "fn-in",
    ]
    build_warnings: list[str] = []
    first = run_command(make_args, cwd=source.parent, env=tex_env, verbose=args.verbose)
    if first.stderr.strip():
        build_warnings.append(first.stderr.strip())

    bcf = build_dir / f"{source.stem}.bcf"
    biber_warnings = ""
    if bcf.exists():
        if not biber:
            raise ConversionError(
                "LaTeX 生成了 .bcf，但找不到 biber；无法保留已格式化引文。"
            )
        biber_result = run_command(
            [biber, source.stem],
            cwd=build_dir,
            env=tex_env,
            verbose=args.verbose,
        )
        biber_warnings = biber_result.stderr.strip()

    previous_digest = ""
    passes = 0
    for _ in range(args.tex4ht_passes):
        completed = run_command(make_args, cwd=source.parent, env=tex_env, verbose=args.verbose)
        passes += 1
        if completed.stderr.strip():
            build_warnings.append(completed.stderr.strip())
        digest = build_file_digest(build_dir, source.stem)
        if digest and digest == previous_digest:
            break
        previous_digest = digest

    main_html = find_unique_tex4ht_main(html_dir, source.stem)
    merged_html = stage / "tex4ht-merged.html"
    html_note_count, note_previews = merge_tex4ht_footnotes(main_html, merged_html)
    svg_conversions, svg_warnings = convert_svg_images_for_docx(
        merged_html,
        (main_html.parent, build_dir, source.parent),
        verbose=args.verbose,
    )
    if html_note_count == 0:
        expanded_probe = fallback_expand_latex(source)
        if re.search(r"\\(?:footnote|lrfootnote|footnotemark|footnotetext)\b", expanded_probe):
            raise ConversionError("TeX4ht 没有生成脚注链接；转换已停止，以免静默丢注。")

    ast_path = stage / "source.ast.json"
    parse_args = [
        pandoc,
        str(merged_html),
        "--from=html",
        "--to=json",
        "--standalone",
        "--output",
        str(ast_path),
        "--resource-path",
        os.pathsep.join((str(main_html.parent), str(source.parent), str(build_dir))),
    ]
    parse_completed = run_command(parse_args, cwd=main_html.parent, verbose=args.verbose)
    ast = json.loads(ast_path.read_text(encoding="utf-8"))
    removed_metadata = {
        key: ast.get("meta", {}).pop(key)
        for key in ("title", "subtitle", "author", "date")
        if key in ast.get("meta", {})
    }
    if removed_metadata:
        # TeX4ht already emits a visible title block.  Pandoc metadata would
        # generate a second, oversized title above it in DOCX.
        ast_path.write_text(json.dumps(ast, ensure_ascii=False), encoding="utf-8")
    source_note_count = count_pandoc_notes(ast)
    if source_note_count != html_note_count:
        raise ConversionError(
            f"TeX4ht 有 {html_note_count} 个脚注链接，但 Pandoc AST 有 "
            f"{source_note_count} 个 Note"
        )

    staged_docx = stage / "converted.docx"
    output_warnings = convert_ast_to_docx(
        ast_path,
        staged_docx,
        pandoc,
        cwd=main_html.parent,
        reference_doc=args.reference_doc,
        resource_paths=(main_html.parent, source.parent, build_dir),
        verbose=args.verbose,
    )
    review = {
        "latex_backend": "make4ht",
        "make4ht": make4ht,
        "biber": biber,
        "tex4ht_followup_passes": passes,
        "html_main": str(main_html),
        "html_footnote_links": html_note_count,
        "pandoc_ast_notes": source_note_count,
        "pandoc_note_previews": note_previews[:20],
        "removed_duplicate_title_metadata": sorted(removed_metadata),
        "svg_conversions": svg_conversions,
        "svg_warnings": svg_warnings,
        "tex4ht_warnings": build_warnings,
        "biber_warnings": biber_warnings,
        "pandoc_parse_warnings": parse_completed.stderr.strip(),
        "pandoc_output_warnings": output_warnings,
    }
    return staged_docx, review, source_note_count


def latex_needs_compiled_backend(source: Path, args: argparse.Namespace) -> bool:
    try:
        probe = fallback_expand_latex(source)
    except ConversionError:
        probe = source.read_text(encoding="utf-8", errors="replace")
    commands = (*DEFAULT_FOOTNOTE_COMMANDS, *DEFAULT_CITATION_COMMANDS, *args.footnote_command, *args.citation_command)
    has_custom_macros = any(re.search(rf"\\{re.escape(command)}\b", probe) for command in commands)
    has_biblatex = bool(
        re.search(r"\\(?:addbibresource|printbibliography|footcite|autocite)\b", probe)
        or re.search(r"\\usepackage(?:\[[^]]*\])?\{biblatex\}", probe)
    )
    return has_custom_macros or has_biblatex


def convert_latex(
    source: Path,
    stage: Path,
    args: argparse.Namespace,
    pandoc: str,
) -> tuple[Path, dict[str, Any], int]:
    backend = args.latex_backend
    if backend == "auto":
        needs_compiled = latex_needs_compiled_backend(source, args)
        if needs_compiled and not shutil.which(args.make4ht):
            raise ConversionError(
                "该 LaTeX 使用 biblatex 或自定义引证/脚注宏，需要 make4ht 后端才能"
                "保留已排版引文。请安装 TeX Live/make4ht；只有在明确接受可能的"
                "引文格式变化时，才显式使用 --latex-backend pandoc。"
            )
        backend = "make4ht" if needs_compiled else "pandoc"
    if backend == "make4ht":
        # Fail closed: silently falling back to Pandoc can turn preformatted
        # legal citations into author-year text while still producing a valid DOCX.
        return convert_latex_make4ht(source, stage, args, pandoc)
    return convert_latex_pandoc(source, stage, args, pandoc)


def convert_pdf(
    source: Path,
    stage: Path,
    args: argparse.Namespace,
    pandoc: str,
) -> tuple[Path, dict[str, Any], int]:
    ast, review = pdf_to_pandoc_ast(
        source,
        pandoc,
        strict=not args.best_effort,
        min_confidence=args.pdf_min_confidence,
        verbose=args.verbose,
    )
    ast_path = stage / "recovered.ast.json"
    ast_path.write_text(json.dumps(ast, ensure_ascii=False, indent=2), encoding="utf-8")
    source_note_count = count_pandoc_notes(ast)
    staged_docx = stage / "converted.docx"
    output_warnings = convert_ast_to_docx(
        ast_path,
        staged_docx,
        pandoc,
        cwd=source.parent,
        reference_doc=args.reference_doc,
        resource_paths=(source.parent,),
        verbose=args.verbose,
    )
    review["pandoc_output_warnings"] = output_warnings
    return staged_docx, review, source_note_count


def copy_intermediates(stage: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for path in stage.iterdir():
        if path.name == "converted.docx":
            continue
        target = destination / path.name
        if path.is_dir():
            if target.exists():
                raise ConversionError(f"中间文件目标已存在: {target}")
            shutil.copytree(path, target)
        else:
            shutil.copy2(path, target)


def resolve_source_type(path: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    suffix = path.suffix.lower()
    if suffix in {".tex", ".ltx", ".latex"}:
        return "latex"
    if suffix == ".pdf":
        return "pdf"
    raise ConversionError("无法根据扩展名判断输入类型；请使用 --source-type latex 或 pdf")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "把带脚注的 LaTeX 或有文本层 PDF 转成含真实 Word 脚注的 DOCX。\n"
            "LaTeX 路径优先；PDF 路径使用版面启发式并默认严格校验。"
        ),
    )
    parser.add_argument("input", type=Path, help="输入 .tex/.latex/.pdf")
    parser.add_argument("-o", "--output", type=Path, help="输出 .docx；默认与输入同名")
    parser.add_argument("--source-type", choices=("auto", "latex", "pdf"), default="auto")
    parser.add_argument(
        "--latex-backend",
        choices=("auto", "pandoc", "make4ht"),
        default="auto",
        help="LaTeX 后端；auto 对 biblatex/自定义脚注宏优先使用 make4ht",
    )
    parser.add_argument("--reference-doc", type=Path, help="Pandoc reference.docx 样式模板")
    parser.add_argument("--bibliography", action="append", default=[], help="额外 .bib，可重复")
    parser.add_argument("--csl", type=Path, help="CSL 引文样式")
    parser.add_argument("--no-citeproc", action="store_true", help="不运行 Pandoc citeproc")
    parser.add_argument(
        "--footnote-command",
        action="append",
        default=[],
        metavar="NAME",
        help="把自定义 \\NAME{...} 视为 \\footnote{...}；可重复",
    )
    parser.add_argument(
        "--citation-command",
        action="append",
        default=[],
        metavar="NAME",
        help="把自定义 \\NAME[...]{} 视为 \\cite；可重复",
    )
    parser.add_argument("--best-effort", action="store_true", help="PDF 歧义时继续并附到页末；默认关闭")
    parser.add_argument(
        "--pdf-min-confidence",
        type=float,
        default=0.85,
        metavar="0..1",
        help="PDF 严格模式最低启发式证据分（兼容名 confidence；默认 0.85）",
    )
    parser.add_argument("--review-json", type=Path, help="审阅报告路径；默认 <output>.review.json")
    parser.add_argument("--no-review-json", action="store_true", help="不写 JSON 审阅报告")
    parser.add_argument("--keep-intermediate", type=Path, help="复制 Pandoc AST/展开后 TeX 等中间文件")
    parser.add_argument("--pandoc", default="pandoc", help="pandoc 可执行文件（默认从 PATH 查找）")
    parser.add_argument("--make4ht", default="make4ht", help="make4ht 可执行文件")
    parser.add_argument("--biber", default="biber", help="biber 可执行文件")
    parser.add_argument(
        "--tex4ht-passes",
        type=int,
        default=3,
        metavar="N",
        help="biber 后最多追加的 TeX4ht 编译轮数（默认 3）",
    )
    parser.add_argument("--latexpand", default="latexpand", help="latexpand 可执行文件")
    parser.add_argument("--no-latexpand", action="store_true", help="使用内置 include 展开器")
    parser.add_argument("--force", action="store_true", help="覆盖已有输出与报告")
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        source = args.input.expanduser().resolve()
        if not source.is_file():
            raise ConversionError(f"输入文件不存在: {source}")
        source_type = resolve_source_type(source, args.source_type)
        output = (args.output or source.with_suffix(".docx")).expanduser().resolve()
        if output.suffix.lower() != ".docx":
            raise ConversionError("输出文件必须使用 .docx 扩展名")
        if output == source:
            raise ConversionError("输出不能覆盖输入文件")
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists() and not args.force:
            raise ConversionError(f"输出已存在；使用 --force 才能覆盖: {output}")
        if not 0.0 <= args.pdf_min_confidence <= 1.0:
            raise ConversionError("--pdf-min-confidence 必须在 0 到 1 之间")
        if not 1 <= args.tex4ht_passes <= 8:
            raise ConversionError("--tex4ht-passes 必须在 1 到 8 之间")

        if args.reference_doc:
            args.reference_doc = args.reference_doc.expanduser().resolve()
            if not args.reference_doc.is_file():
                raise ConversionError(f"reference.docx 不存在: {args.reference_doc}")
        if args.csl:
            args.csl = args.csl.expanduser().resolve()
            if not args.csl.is_file():
                raise ConversionError(f"CSL 文件不存在: {args.csl}")

        pandoc = command_path(args.pandoc, "pandoc")
        review_path = (
            args.review_json.expanduser().resolve()
            if args.review_json
            else output.with_suffix(".review.json")
        )
        if not args.no_review_json:
            if review_path in {source, output}:
                raise ConversionError("审阅报告路径不能与输入或 DOCX 输出相同")
            review_path.parent.mkdir(parents=True, exist_ok=True)
            if review_path.exists() and not args.force:
                raise ConversionError(f"审阅报告已存在；使用 --force 才能覆盖: {review_path}")

        with tempfile.TemporaryDirectory(prefix=".footnote-to-docx-", dir=output.parent) as temp_name:
            stage = Path(temp_name)
            if source_type == "latex":
                staged_docx, details, source_note_count = convert_latex(source, stage, args, pandoc)
            else:
                staged_docx, details, source_note_count = convert_pdf(source, stage, args, pandoc)

            validation = validate_docx_footnotes(staged_docx, expected_count=source_note_count)
            if not validation["valid"]:
                raise ConversionError(
                    "DOCX 真脚注结构校验失败:\n- " + "\n- ".join(validation["errors"])
                )
            # The staged file is atomically moved to this path after every check passes.
            # Keep the durable destination in the user-facing review report.
            validation["path"] = str(output)

            review = {
                "schema_version": 1,
                "source": str(source),
                "source_type": source_type,
                "output": str(output),
                "pandoc": pandoc_version(pandoc, source.parent),
                "mode": "best-effort" if args.best_effort and source_type == "pdf" else "strict",
                "source_note_count": source_note_count,
                "details": details,
                "docx_validation": validation,
            }
            review_text = json.dumps(review, ensure_ascii=False, indent=2) + "\n"
            staged_review = stage / "review.json"
            staged_review.write_text(review_text, encoding="utf-8")

            if args.keep_intermediate:
                copy_intermediates(stage, args.keep_intermediate.expanduser().resolve())

            os.replace(staged_docx, output)
            if not args.no_review_json:
                report_temp: Path | None = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="w",
                        encoding="utf-8",
                        dir=review_path.parent,
                        prefix=f".{review_path.name}.tmp-",
                        delete=False,
                    ) as handle:
                        handle.write(review_text)
                        report_temp = Path(handle.name)
                    report_temp.chmod(0o644)
                    os.replace(report_temp, review_path)
                    report_temp = None
                finally:
                    if report_temp is not None:
                        report_temp.unlink(missing_ok=True)

        print(f"DOCX: {output}")
        if source_type == "pdf":
            print(f"恢复并写入的 Word 脚注（PDF 启发式）: {source_note_count}")
        else:
            print(f"真实脚注: {source_note_count}")
        if not args.no_review_json:
            print(f"审阅报告: {review_path}")
        return 0
    except ConversionError as exc:
        eprint(f"错误: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
