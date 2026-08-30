#!/usr/bin/env python3
"""Apply a Harvard Journal of Law & Technology-inspired layout to DOCX files.

The manuscript DOCX files are semantic conversions whose content and footnotes
already exist.  This program intentionally works after conversion: it rewrites
only WordprocessingML layout, styles, fonts, headers, and page geometry while
preserving the body text, links, drawings, and real Word footnotes.

It is deliberately dependency-free so ``make docx`` can run on a normal Python
installation.  Every write is atomic and a structural footnote/ZIP check runs
before and after the rewrite.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)
ET.register_namespace("", REL_NS)

# WordprocessingML property elements have a schema-defined child order.  Word
# often repairs a mildly out-of-order property list, but LibreOffice rejects a
# package during import when a ``w:pPr`` or ``w:rPr`` is malformed.  Keep the
# subset used here in canonical order whenever layout code rewrites it.
PARAGRAPH_PROPERTY_ORDER = (
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
    "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
    "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct",
    "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
    "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
    "suppressOverlap", "jc", "textDirection", "textAlignment",
    "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr",
    "pPrChange",
)
RUN_PROPERTY_ORDER = (
    "rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps",
    "strike", "dstrike", "outline", "shadow", "emboss", "imprint", "noProof",
    "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern",
    "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd",
    "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout",
    "specVanish", "oMath", "rPrChange",
)
STYLE_CHILD_ORDER = (
    "name", "aliases", "basedOn", "next", "link", "autoRedefine", "hidden",
    "uiPriority", "semiHidden", "unhideWhenUsed", "qFormat", "locked",
    "personal", "personalCompose", "personalReply", "rsid", "pPr", "rPr",
    "tblPr", "trPr", "tcPr", "tblStylePr",
)


def qn(namespace: str, name: str) -> str:
    return f"{{{namespace}}}{name}"


def w(name: str) -> str:
    return qn(W_NS, name)


def r(name: str) -> str:
    return qn(R_NS, name)


def rel(name: str) -> str:
    return qn(REL_NS, name)


def ct(name: str) -> str:
    return qn(CT_NS, name)


def serialize(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def serialize_content_types(root: ET.Element) -> bytes:
    """Preserve the package content-types root as the default namespace.

    LibreOffice 26.8 rejects this particular part when ElementTree writes its
    namespace as an arbitrary ``ns0`` prefix, despite the XML being namespace
    equivalent.  Relationships still need their own default namespace, so
    restore it immediately after serializing this one package member.
    """
    ET.register_namespace("", CT_NS)
    try:
        return serialize(root)
    finally:
        ET.register_namespace("", REL_NS)


def reorder_children(parent: ET.Element, names: Iterable[str]) -> None:
    """Order known WordprocessingML children while retaining unknown content."""
    order = {w(name): index for index, name in enumerate(names)}
    children = list(parent)
    indexed = list(enumerate(children))
    indexed.sort(key=lambda item: (order.get(item[1].tag, len(order) + item[0]), item[0]))
    parent[:] = [child for _, child in indexed]


def reorder_paragraph_properties(properties: ET.Element) -> None:
    reorder_children(properties, PARAGRAPH_PROPERTY_ORDER)


def reorder_run_properties(properties: ET.Element) -> None:
    reorder_children(properties, RUN_PROPERTY_ORDER)


def reorder_style(style: ET.Element) -> None:
    reorder_children(style, STYLE_CHILD_ORDER)


def parse_xml(payload: bytes, member: str) -> ET.Element:
    try:
        return ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML in {member}: {exc}") from exc


def first_child(parent: ET.Element, tag: str) -> ET.Element | None:
    return parent.find(tag)


def ensure_child(parent: ET.Element, tag: str, *, index: int | None = None) -> ET.Element:
    child = first_child(parent, tag)
    if child is None:
        child = ET.Element(tag)
        if index is None:
            parent.append(child)
        else:
            parent.insert(index, child)
    return child


def remove_children(parent: ET.Element, tags: Iterable[str]) -> None:
    targets = set(tags)
    for child in list(parent):
        if child.tag in targets:
            parent.remove(child)


def set_val(element: ET.Element, value: str) -> None:
    element.set(w("val"), value)


def paragraph_properties(paragraph: ET.Element) -> ET.Element:
    return ensure_child(paragraph, w("pPr"), index=0)


def run_properties(run: ET.Element) -> ET.Element:
    return ensure_child(run, w("rPr"), index=0)


def style_properties(style: ET.Element, kind: str) -> ET.Element:
    return ensure_child(style, w(kind))


def style_id(paragraph: ET.Element) -> str | None:
    ppr = paragraph.find(w("pPr"))
    if ppr is None:
        return None
    style = ppr.find(w("pStyle"))
    return style.get(w("val")) if style is not None else None


def set_style_id(paragraph: ET.Element, value: str) -> None:
    ppr = paragraph_properties(paragraph)
    style = ensure_child(ppr, w("pStyle"), index=0)
    set_val(style, value)
    reorder_paragraph_properties(ppr)


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(w("t"))).strip()


def replace_paragraph_text(paragraph: ET.Element, value: str) -> None:
    """Replace visible paragraph text while retaining its run-level formatting."""
    nodes = list(paragraph.iter(w("t")))
    if not nodes:
        return
    nodes[0].text = value
    for node in nodes[1:]:
        node.text = ""


def set_fonts(
    rpr: ET.Element,
    *,
    latin: str,
    cjk: str,
    language: str = "en-US",
) -> None:
    fonts = ensure_child(rpr, w("rFonts"), index=0)
    for key in (
        "asciiTheme",
        "hAnsiTheme",
        "eastAsiaTheme",
        "cstheme",
    ):
        fonts.attrib.pop(w(key), None)
    fonts.set(w("ascii"), latin)
    fonts.set(w("hAnsi"), latin)
    fonts.set(w("cs"), latin)
    fonts.set(w("eastAsia"), cjk)

    lang = ensure_child(rpr, w("lang"))
    lang.set(w("val"), language)
    lang.set(w("eastAsia"), "zh-CN")


def set_size(rpr: ET.Element, half_points: int) -> None:
    size = ensure_child(rpr, w("sz"))
    set_val(size, str(half_points))
    size_cs = ensure_child(rpr, w("szCs"))
    set_val(size_cs, str(half_points))


def set_color(rpr: ET.Element, value: str) -> None:
    color = ensure_child(rpr, w("color"))
    for key in ("themeColor", "themeShade", "themeTint"):
        color.attrib.pop(w(key), None)
    set_val(color, value)


def set_toggle(rpr: ET.Element, name: str, enabled: bool | None) -> None:
    if enabled is None:
        return
    remove_children(rpr, (w(name),))
    if enabled:
        rpr.append(ET.Element(w(name)))


def set_underline(rpr: ET.Element, value: str | None) -> None:
    remove_children(rpr, (w("u"),))
    if value:
        underline = ET.Element(w("u"))
        set_val(underline, value)
        rpr.append(underline)


def apply_run_style(
    rpr: ET.Element,
    *,
    latin: str,
    cjk: str,
    size: int | None = None,
    color: str | None = None,
    bold: bool | None = None,
    italic: bool | None = None,
    small_caps: bool | None = None,
    underline: str | None = None,
) -> None:
    set_fonts(rpr, latin=latin, cjk=cjk)
    if size is not None:
        set_size(rpr, size)
    if color is not None:
        set_color(rpr, color)
    set_toggle(rpr, "b", bold)
    set_toggle(rpr, "bCs", bold)
    set_toggle(rpr, "i", italic)
    set_toggle(rpr, "iCs", italic)
    set_toggle(rpr, "smallCaps", small_caps)
    if underline is not None:
        set_underline(rpr, underline)
    reorder_run_properties(rpr)


def set_paragraph_layout(
    paragraph: ET.Element,
    *,
    before: int,
    after: int,
    line: int,
    first_line: int | None,
    left: int | None = None,
    right: int | None = None,
    alignment: str | None = None,
    keep_next: bool = False,
    keep_lines: bool = False,
    page_break_before: bool = False,
) -> None:
    ppr = paragraph_properties(paragraph)
    remove_children(
        ppr,
        (
            w("spacing"),
            w("ind"),
            w("jc"),
            w("keepNext"),
            w("keepLines"),
            w("pageBreakBefore"),
        ),
    )

    spacing = ET.Element(w("spacing"))
    spacing.set(w("before"), str(before))
    spacing.set(w("after"), str(after))
    spacing.set(w("line"), str(line))
    spacing.set(w("lineRule"), "exact")
    ppr.append(spacing)

    if any(value is not None for value in (first_line, left, right)):
        ind = ET.Element(w("ind"))
        if first_line is not None:
            ind.set(w("firstLine"), str(first_line))
        if left is not None:
            ind.set(w("left"), str(left))
        if right is not None:
            ind.set(w("right"), str(right))
        ppr.append(ind)
    if alignment:
        jc = ET.Element(w("jc"))
        set_val(jc, alignment)
        ppr.append(jc)
    if keep_next:
        ppr.append(ET.Element(w("keepNext")))
    if keep_lines:
        ppr.append(ET.Element(w("keepLines")))
    if page_break_before:
        ppr.append(ET.Element(w("pageBreakBefore")))
    reorder_paragraph_properties(ppr)


def ensure_style(
    styles: ET.Element,
    style_name: str,
    *,
    style_type: str = "paragraph",
    display_name: str | None = None,
    based_on: str | None = None,
    custom: bool = False,
) -> ET.Element:
    for style in styles.findall(w("style")):
        if style.get(w("styleId")) == style_name and style.get(w("type")) == style_type:
            result = style
            break
    else:
        result = ET.Element(w("style"))
        result.set(w("type"), style_type)
        result.set(w("styleId"), style_name)
        if custom:
            result.set(w("customStyle"), "1")
        styles.append(result)

    name = ensure_child(result, w("name"), index=0)
    set_val(name, display_name or style_name)
    if based_on:
        based = ensure_child(result, w("basedOn"))
        set_val(based, based_on)
    return result


def configure_style(
    style: ET.Element,
    *,
    latin: str,
    cjk: str,
    size: int,
    color: str = "000000",
    before: int = 0,
    after: int = 0,
    line: int = 320,
    first_line: int | None = 0,
    left: int | None = None,
    right: int | None = None,
    alignment: str | None = "both",
    bold: bool | None = False,
    italic: bool | None = False,
    small_caps: bool | None = False,
    keep_next: bool = False,
    keep_lines: bool = False,
) -> None:
    ppr = style_properties(style, "pPr")
    temporary = ET.Element(w("p"))
    temporary.append(ppr)
    set_paragraph_layout(
        temporary,
        before=before,
        after=after,
        line=line,
        first_line=first_line,
        left=left,
        right=right,
        alignment=alignment,
        keep_next=keep_next,
        keep_lines=keep_lines,
    )
    rpr = style_properties(style, "rPr")
    apply_run_style(
        rpr,
        latin=latin,
        cjk=cjk,
        size=size,
        color=color,
        bold=bold,
        italic=italic,
        small_caps=small_caps,
    )


def configure_styles(styles: ET.Element, *, latin: str, cjk: str) -> None:
    normal = ensure_style(styles, "Normal", display_name="Normal")
    normal_rpr = style_properties(normal, "rPr")
    apply_run_style(normal_rpr, latin=latin, cjk=cjk, size=24, color="000000")

    body = ensure_style(styles, "BodyText", display_name="Body Text", based_on="Normal")
    configure_style(
        body,
        latin=latin,
        cjk=cjk,
        size=24,
        line=320,
        first_line=360,
        alignment="both",
    )
    first = ensure_style(styles, "FirstParagraph", display_name="First Paragraph", based_on="BodyText")
    configure_style(
        first,
        latin=latin,
        cjk=cjk,
        size=24,
        line=320,
        first_line=360,
        alignment="both",
    )
    compact = ensure_style(styles, "Compact", display_name="Compact", based_on="BodyText")
    configure_style(
        compact,
        latin=latin,
        cjk=cjk,
        size=22,
        line=280,
        first_line=0,
        alignment="both",
    )
    block = ensure_style(styles, "BlockText", display_name="Block Text", based_on="BodyText")
    configure_style(
        block,
        latin=latin,
        cjk=cjk,
        size=24,
        before=80,
        after=80,
        line=320,
        first_line=0,
        left=360,
        right=360,
        alignment="both",
    )

    title = ensure_style(styles, "Title", display_name="Title", based_on="Normal")
    configure_style(
        title,
        latin=latin,
        cjk=cjk,
        size=28,
        before=0,
        after=180,
        line=340,
        first_line=0,
        alignment="center",
        bold=True,
        small_caps=True,
        keep_next=True,
        keep_lines=True,
    )
    author = ensure_style(styles, "Author", display_name="Author", based_on="Normal", custom=True)
    configure_style(
        author,
        latin=latin,
        cjk=cjk,
        size=24,
        after=60,
        line=280,
        first_line=0,
        alignment="center",
        italic=True,
        keep_next=True,
    )
    date = ensure_style(styles, "Date", display_name="Date", based_on="Normal")
    configure_style(
        date,
        latin=latin,
        cjk=cjk,
        size=20,
        after=180,
        line=240,
        first_line=0,
        alignment="center",
        keep_next=True,
    )
    abstract_title = ensure_style(
        styles,
        "AbstractTitle",
        display_name="Abstract Title",
        based_on="Normal",
        custom=True,
    )
    configure_style(
        abstract_title,
        latin=latin,
        cjk=cjk,
        size=24,
        before=160,
        after=40,
        line=280,
        first_line=0,
        alignment="center",
        bold=True,
        small_caps=True,
        keep_next=True,
    )
    abstract = ensure_style(styles, "Abstract", display_name="Abstract", based_on="Normal", custom=True)
    configure_style(
        abstract,
        latin=latin,
        cjk=cjk,
        size=24,
        before=0,
        after=0,
        line=272,
        first_line=0,
        alignment="both",
        italic=True,
        keep_lines=True,
    )

    for heading, size, before, after, italic in (
        ("Heading1", 24, 300, 100, False),
        ("Heading2", 24, 260, 100, False),
        ("Heading3", 24, 300, 100, False),
        ("Heading4", 22, 220, 70, False),
        ("Heading5", 21, 180, 50, True),
    ):
        heading_style = ensure_style(styles, heading, display_name=heading.replace("Heading", "heading "), based_on="Normal")
        configure_style(
            heading_style,
            latin=latin,
            cjk=cjk,
            size=size,
            before=before,
            after=after,
            line=280,
            first_line=0,
            alignment="left",
            bold=False,
            italic=italic,
            small_caps=not italic,
            keep_next=True,
            keep_lines=True,
        )

    toc_heading = ensure_style(styles, "TOCHeading", display_name="TOC Heading", based_on="Normal")
    configure_style(
        toc_heading,
        latin=latin,
        cjk=cjk,
        size=24,
        before=0,
        after=160,
        line=280,
        first_line=0,
        alignment="center",
        bold=True,
        small_caps=True,
        keep_next=True,
    )
    toc = ensure_style(styles, "TOC1", display_name="TOC 1", based_on="Normal", custom=True)
    configure_style(
        toc,
        latin=latin,
        cjk=cjk,
        size=20,
        line=240,
        first_line=0,
        alignment="left",
    )
    toc_link = ensure_style(
        styles,
        "TOCLink",
        style_type="character",
        display_name="TOC Link",
        based_on="DefaultParagraphFont",
        custom=True,
    )
    toc_link_rpr = style_properties(toc_link, "rPr")
    apply_run_style(
        toc_link_rpr,
        latin=latin,
        cjk=cjk,
        size=20,
        color="000000",
        underline="none",
    )
    hyperlink = ensure_style(styles, "Hyperlink", style_type="character", display_name="Hyperlink")
    hyperlink_rpr = style_properties(hyperlink, "rPr")
    apply_run_style(
        hyperlink_rpr,
        latin=latin,
        cjk=cjk,
        size=20,
        color="0000FF",
        underline="single",
    )

    footnote = ensure_style(styles, "FootnoteText", display_name="Footnote Text", based_on="Normal")
    configure_style(
        footnote,
        latin=latin,
        cjk=cjk,
        size=18,
        line=210,
        first_line=0,
        alignment="both",
    )
    footnote_block = ensure_style(styles, "FootnoteBlockText", display_name="Footnote Block Text", based_on="FootnoteText")
    configure_style(
        footnote_block,
        latin=latin,
        cjk=cjk,
        size=18,
        before=40,
        after=40,
        line=210,
        first_line=0,
        left=360,
        right=360,
        alignment="both",
    )
    footnote_ref = ensure_style(
        styles,
        "FootnoteReference",
        style_type="character",
        display_name="Footnote Reference",
    )
    footnote_ref_rpr = style_properties(footnote_ref, "rPr")
    apply_run_style(footnote_ref_rpr, latin=latin, cjk=cjk, size=18, color="000000")
    vert = ensure_child(footnote_ref_rpr, w("vertAlign"))
    set_val(vert, "superscript")
    reorder_run_properties(footnote_ref_rpr)

    definition_term = ensure_style(styles, "DefinitionTerm", display_name="Definition Term", based_on="Normal", custom=True)
    configure_style(
        definition_term,
        latin=latin,
        cjk=cjk,
        size=24,
        before=0,
        after=0,
        line=320,
        first_line=0,
        left=360,
        alignment="left",
    )
    definition = ensure_style(styles, "Definition", display_name="Definition", based_on="Normal", custom=True)
    configure_style(
        definition,
        latin=latin,
        cjk=cjk,
        size=24,
        before=0,
        after=0,
        line=320,
        first_line=0,
        left=720,
        alignment="both",
    )
    for caption_name in ("Caption", "TableCaption", "ImageCaption"):
        caption = ensure_style(styles, caption_name, display_name=caption_name.replace("Caption", " Caption").strip(), based_on="Normal")
        configure_style(
            caption,
            latin=latin,
            cjk=cjk,
            size=20,
            before=80,
            after=100,
            line=240,
            first_line=0,
            alignment="center",
            italic=True,
        )

    for style in styles.findall(w("style")):
        ppr = style.find(w("pPr"))
        if ppr is not None:
            reorder_paragraph_properties(ppr)
        rpr = style.find(w("rPr"))
        if rpr is not None:
            reorder_run_properties(rpr)
        reorder_style(style)


def normalize_run_fonts(root: ET.Element, *, latin: str, cjk: str) -> None:
    for run in root.iter(w("r")):
        properties = run_properties(run)
        set_fonts(properties, latin=latin, cjk=cjk)
        reorder_run_properties(properties)


def set_direct_runs(
    paragraph: ET.Element,
    *,
    latin: str,
    cjk: str,
    size: int,
    color: str = "000000",
    bold: bool | None = None,
    italic: bool | None = None,
    small_caps: bool | None = None,
) -> None:
    for run in paragraph.iter(w("r")):
        apply_run_style(
            run_properties(run),
            latin=latin,
            cjk=cjk,
            size=size,
            color=color,
            bold=bold,
            italic=italic,
            small_caps=small_caps,
        )


def retarget_toc_links(paragraph: ET.Element) -> None:
    for rpr in paragraph.iter(w("rPr")):
        rstyle = rpr.find(w("rStyle"))
        if rstyle is not None and rstyle.get(w("val")) == "Hyperlink":
            set_val(rstyle, "TOCLink")
            set_color(rpr, "000000")
            set_underline(rpr, "none")


def is_abstract_heading(text: str) -> bool:
    return text.casefold() == "abstract" or text == "摘要"


def is_contents_heading(text: str) -> bool:
    return text.casefold() in {"contents", "table of contents"} or text == "目录"


def is_intro_heading(text: str) -> bool:
    return text.casefold() == "introduction" or text == "引言"


def layout_document_body(root: ET.Element, *, latin: str, cjk: str) -> None:
    body = root.find(w("body"))
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    paragraphs = [child for child in body if child.tag == w("p")]
    if not paragraphs:
        raise ValueError("word/document.xml has no paragraphs")

    title = paragraphs[0]
    set_style_id(title, "Title")
    set_paragraph_layout(
        title,
        before=0,
        after=180,
        line=340,
        first_line=0,
        alignment="center",
        keep_next=True,
        keep_lines=True,
    )
    set_direct_runs(title, latin=latin, cjk=cjk, size=28, bold=True, small_caps=True)

    abstract_open = False
    contents_open = False
    contents_paragraph: ET.Element | None = None
    intro_pending = False

    for index, paragraph in enumerate(paragraphs):
        text = paragraph_text(paragraph)
        current_style = style_id(paragraph) or ""

        if index == 0:
            continue
        if index == 1:
            set_style_id(paragraph, "Author")
            set_paragraph_layout(
                paragraph,
                before=0,
                after=60,
                line=280,
                first_line=0,
                alignment="center",
                keep_next=True,
            )
            set_direct_runs(paragraph, latin=latin, cjk=cjk, size=24, italic=True)
            continue
        if index == 2 and text:
            replace_paragraph_text(paragraph, "(submission draft)")
            set_style_id(paragraph, "Date")
            set_paragraph_layout(
                paragraph,
                before=0,
                after=180,
                line=240,
                first_line=0,
                alignment="center",
                keep_next=True,
            )
            set_direct_runs(paragraph, latin=latin, cjk=cjk, size=20)
            continue

        if is_abstract_heading(text):
            abstract_open = True
            set_style_id(paragraph, "AbstractTitle")
            set_paragraph_layout(
                paragraph,
                before=160,
                after=40,
                line=280,
                first_line=0,
                alignment="center",
                keep_next=True,
            )
            set_direct_runs(paragraph, latin=latin, cjk=cjk, size=24, bold=True, small_caps=True)
            continue

        if abstract_open and current_style == "BlockText":
            set_style_id(paragraph, "Abstract")
            set_paragraph_layout(
                paragraph,
                before=0,
                after=0,
                line=272,
                first_line=0,
                alignment="both",
                keep_lines=True,
            )
            set_direct_runs(paragraph, latin=latin, cjk=cjk, size=24, italic=True)
            continue

        if abstract_open and current_style == "FootnoteText":
            abstract_open = False

        if is_contents_heading(text):
            contents_open = True
            intro_pending = True
            set_style_id(paragraph, "TOCHeading")
            set_paragraph_layout(
                paragraph,
                before=0,
                after=160,
                line=280,
                first_line=0,
                alignment="center",
                keep_next=True,
                page_break_before=True,
            )
            set_direct_runs(paragraph, latin=latin, cjk=cjk, size=24, bold=True, small_caps=True)
            continue

        if contents_open and contents_paragraph is None:
            contents_paragraph = paragraph
            set_style_id(paragraph, "TOC1")
            set_paragraph_layout(
                paragraph,
                before=0,
                after=0,
                line=240,
                first_line=0,
                alignment="left",
            )
            retarget_toc_links(paragraph)
            set_direct_runs(paragraph, latin=latin, cjk=cjk, size=20)
            continue

        if intro_pending and is_intro_heading(text):
            contents_open = False
            intro_pending = False
            set_style_id(paragraph, "Heading3")
            set_paragraph_layout(
                paragraph,
                before=0,
                after=100,
                line=280,
                first_line=0,
                alignment="left",
                keep_next=True,
                keep_lines=True,
                page_break_before=True,
            )
            set_direct_runs(paragraph, latin=latin, cjk=cjk, size=24, small_caps=True)
            continue

        current_style = style_id(paragraph) or ""
        if current_style in {"BodyText", "FirstParagraph"}:
            set_paragraph_layout(
                paragraph,
                before=0,
                after=0,
                line=320,
                first_line=360,
                alignment="both",
            )
        elif current_style == "Compact":
            set_paragraph_layout(
                paragraph,
                before=0,
                after=0,
                line=280,
                first_line=0,
                alignment="both",
            )
        elif current_style == "BlockText":
            set_paragraph_layout(
                paragraph,
                before=80,
                after=80,
                line=320,
                first_line=0,
                left=360,
                right=360,
                alignment="both",
            )
        elif current_style in {"Heading1", "Heading2", "Heading3", "Heading4", "Heading5"}:
            size = {"Heading1": 24, "Heading2": 24, "Heading3": 24, "Heading4": 22, "Heading5": 21}[current_style]
            before = {"Heading1": 300, "Heading2": 260, "Heading3": 300, "Heading4": 220, "Heading5": 180}[current_style]
            after = {"Heading1": 100, "Heading2": 100, "Heading3": 100, "Heading4": 70, "Heading5": 50}[current_style]
            set_paragraph_layout(
                paragraph,
                before=before,
                after=after,
                line=280,
                first_line=0,
                alignment="left",
                keep_next=True,
                keep_lines=True,
            )
            set_direct_runs(
                paragraph,
                latin=latin,
                cjk=cjk,
                size=size,
                italic=current_style == "Heading5",
                small_caps=current_style != "Heading5",
            )
        elif current_style == "DefinitionTerm":
            set_paragraph_layout(
                paragraph,
                before=0,
                after=0,
                line=320,
                first_line=0,
                left=360,
                alignment="left",
            )
        elif current_style == "Definition":
            set_paragraph_layout(
                paragraph,
                before=0,
                after=0,
                line=320,
                first_line=0,
                left=720,
                alignment="both",
            )
        elif current_style in {"Caption", "TableCaption", "ImageCaption"}:
            set_paragraph_layout(
                paragraph,
                before=80,
                after=100,
                line=240,
                first_line=0,
                alignment="center",
            )
            set_direct_runs(paragraph, latin=latin, cjk=cjk, size=20, italic=True)
        elif current_style == "FootnoteText":
            # The author note produced by the TeX-to-DOCX converter is a visible
            # footnote block in the body.  Keep its short separator rule at 2".
            if not text:
                set_paragraph_layout(
                    paragraph,
                    before=40,
                    after=0,
                    line=180,
                    first_line=0,
                    right=3600,
                    alignment="left",
                )
            else:
                set_paragraph_layout(
                    paragraph,
                    before=0,
                    after=80,
                    line=210,
                    first_line=0,
                    alignment="both",
                )
                set_direct_runs(paragraph, latin=latin, cjk=cjk, size=18)


def configure_section(document: ET.Element) -> None:
    body = document.find(w("body"))
    if body is None:
        raise ValueError("word/document.xml has no w:body")
    section = body.find(w("sectPr"))
    if section is None:
        section = ET.Element(w("sectPr"))
        body.append(section)

    # ECMA-376 prescribes the order of a section property element.  Header
    # references come first, while titlePg follows pgMar.  LibreOffice is
    # stricter than Word about that ordering, so rebuild both elements rather
    # than inserting titlePg next to the header references.
    remove_children(section, (w("headerReference"), w("titlePg")))
    for offset, (kind, rel_id) in enumerate(
        (("first", "rIdHarvardJoltFirst"), ("default", "rIdHarvardJoltOdd"), ("even", "rIdHarvardJoltEven"))
    ):
        reference = ET.Element(w("headerReference"))
        reference.set(w("type"), kind)
        reference.set(r("id"), rel_id)
        section.insert(offset, reference)

    page_size = ensure_child(section, w("pgSz"))
    page_size.set(w("w"), "12240")
    page_size.set(w("h"), "15840")
    margin = ensure_child(section, w("pgMar"))
    margin.set(w("top"), "2160")
    margin.set(w("right"), "2880")
    margin.set(w("bottom"), "1440")
    margin.set(w("left"), "2880")
    margin.set(w("header"), "720")
    margin.set(w("footer"), "720")
    margin.set(w("gutter"), "0")
    title_page = ET.Element(w("titlePg"))
    section.insert(list(section).index(margin) + 1, title_page)


def field_run(field: str, *, font: str, size: int, italic: bool = False) -> ET.Element:
    run = ET.Element(w("r"))
    apply_run_style(run_properties(run), latin=font, cjk="Songti SC", size=size, italic=italic)
    begin = ET.Element(w("fldChar"))
    begin.set(w("fldCharType"), "begin")
    run.append(begin)
    return run


def page_field_runs(*, font: str, size: int) -> list[ET.Element]:
    begin = ET.Element(w("r"))
    apply_run_style(run_properties(begin), latin=font, cjk="Songti SC", size=size)
    fld_begin = ET.Element(w("fldChar"))
    fld_begin.set(w("fldCharType"), "begin")
    begin.append(fld_begin)

    instruction = ET.Element(w("r"))
    apply_run_style(run_properties(instruction), latin=font, cjk="Songti SC", size=size)
    instr_text = ET.Element(w("instrText"))
    instr_text.set(qn("http://www.w3.org/XML/1998/namespace", "space"), "preserve")
    instr_text.text = " PAGE "
    instruction.append(instr_text)

    separate = ET.Element(w("r"))
    apply_run_style(run_properties(separate), latin=font, cjk="Songti SC", size=size)
    fld_separate = ET.Element(w("fldChar"))
    fld_separate.set(w("fldCharType"), "separate")
    separate.append(fld_separate)

    result = ET.Element(w("r"))
    apply_run_style(run_properties(result), latin=font, cjk="Songti SC", size=size)
    result_text = ET.Element(w("t"))
    result_text.text = "1"
    result.append(result_text)

    end = ET.Element(w("r"))
    apply_run_style(run_properties(end), latin=font, cjk="Songti SC", size=size)
    fld_end = ET.Element(w("fldChar"))
    fld_end.set(w("fldCharType"), "end")
    end.append(fld_end)
    return [begin, instruction, separate, result, end]


def text_run(
    text: str,
    *,
    font: str,
    size: int,
    italic: bool = False,
) -> ET.Element:
    run = ET.Element(w("r"))
    apply_run_style(run_properties(run), latin=font, cjk="Songti SC", size=size, italic=italic)
    value = ET.Element(w("t"))
    if text.startswith(" ") or text.endswith(" "):
        value.set(qn("http://www.w3.org/XML/1998/namespace", "space"), "preserve")
    value.text = text
    run.append(value)
    return run


def tab_run(*, font: str, size: int) -> ET.Element:
    run = ET.Element(w("r"))
    apply_run_style(run_properties(run), latin=font, cjk="Songti SC", size=size)
    run.append(ET.Element(w("tab")))
    return run


def header_paragraph(
    *,
    alignment: str | None,
    tabs: tuple[tuple[str, int], ...] = (),
) -> ET.Element:
    paragraph = ET.Element(w("p"))
    ppr = paragraph_properties(paragraph)
    spacing = ET.Element(w("spacing"))
    spacing.set(w("before"), "0")
    spacing.set(w("after"), "0")
    spacing.set(w("line"), "220")
    spacing.set(w("lineRule"), "exact")
    ppr.append(spacing)
    if alignment:
        jc = ET.Element(w("jc"))
        set_val(jc, alignment)
        ppr.append(jc)
    if tabs:
        tab_stops = ET.Element(w("tabs"))
        for kind, position in tabs:
            tab = ET.Element(w("tab"))
            tab.set(w("val"), kind)
            tab.set(w("pos"), str(position))
            tab_stops.append(tab)
        ppr.append(tab_stops)
    reorder_paragraph_properties(ppr)
    return paragraph


def make_headers(*, year: str) -> dict[str, bytes]:
    root_attributes = {qn("http://www.w3.org/2000/xmlns/", "w"): W_NS, qn("http://www.w3.org/2000/xmlns/", "r"): R_NS}
    # ElementTree emits the namespace declarations from register_namespace; the
    # explicit dictionary is intentionally avoided because it creates duplicate
    # xmlns bindings on some Python versions.
    del root_attributes

    first = ET.Element(w("hdr"))
    first_line = header_paragraph(alignment="center")
    first_line.append(text_run("Harvard Journal of Law & Technology", font="Garamond", size=24, italic=True))
    first.append(first_line)
    second_line = header_paragraph(alignment="center")
    second_line.append(text_run("(submission draft)", font="Garamond", size=24, italic=True))
    first.append(second_line)

    odd = ET.Element(w("hdr"))
    odd_line = header_paragraph(alignment=None, tabs=(("right", 6480),))
    odd_line.append(text_run("Before the Merits", font="Garamond", size=21, italic=True))
    odd_line.append(tab_run(font="Garamond", size=21))
    odd_line.extend(page_field_runs(font="Garamond", size=21))
    odd.append(odd_line)

    even = ET.Element(w("hdr"))
    even_line = header_paragraph(alignment=None, tabs=(("center", 3240), ("right", 6480)))
    even_line.extend(page_field_runs(font="Garamond", size=21))
    even_line.append(tab_run(font="Garamond", size=21))
    even_line.append(text_run("Harvard Journal of Law & Technology", font="Garamond", size=21))
    even_line.append(tab_run(font="Garamond", size=21))
    even_line.append(text_run(f"[{year}]", font="Garamond", size=21))
    even.append(even_line)

    return {
        "word/header1.xml": serialize(first),
        "word/header2.xml": serialize(odd),
        "word/header3.xml": serialize(even),
    }


def configure_settings(settings: ET.Element) -> None:
    if settings.find(w("evenAndOddHeaders")) is None:
        settings.insert(0, ET.Element(w("evenAndOddHeaders")))
    update = ensure_child(settings, w("updateFields"))
    set_val(update, "true")
    theme_language = ensure_child(settings, w("themeFontLang"))
    theme_language.set(w("val"), "en-US")
    theme_language.set(w("eastAsia"), "zh-CN")
    remove_children(settings, (w("embedSystemFonts"),))


def configure_relationships(relationships: ET.Element) -> None:
    replacement = {
        "rIdHarvardJoltFirst": "header1.xml",
        "rIdHarvardJoltOdd": "header2.xml",
        "rIdHarvardJoltEven": "header3.xml",
    }
    for item in list(relationships):
        if item.get("Id") in replacement:
            relationships.remove(item)
    for rel_id, target in replacement.items():
        item = ET.Element(rel("Relationship"))
        item.set("Id", rel_id)
        item.set(
            "Type",
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header",
        )
        item.set("Target", target)
        relationships.append(item)


def configure_content_types(content_types: ET.Element) -> None:
    parts = {"/word/header1.xml", "/word/header2.xml", "/word/header3.xml"}
    content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"
    existing = {item.get("PartName"): item for item in content_types.findall(ct("Override"))}
    for part in parts:
        item = existing.get(part)
        if item is None:
            item = ET.Element(ct("Override"))
            content_types.append(item)
        item.set("PartName", part)
        item.set("ContentType", content_type)


def configure_font_table(font_table: ET.Element, *, latin: str, cjk: str) -> None:
    existing = {item.get(w("name")) for item in font_table.findall(w("font"))}
    for name, family, charset in ((latin, "roman", "00"), (cjk, "roman", "86")):
        if name in existing:
            continue
        font = ET.Element(w("font"))
        font.set(w("name"), name)
        family_element = ET.Element(w("family"))
        set_val(family_element, family)
        font.append(family_element)
        charset_element = ET.Element(w("charset"))
        set_val(charset_element, charset)
        font.append(charset_element)
        font_table.append(font)


def configure_footnotes(footnotes: ET.Element, *, latin: str, cjk: str) -> None:
    for note in footnotes.findall(w("footnote")):
        note_id = note.get(w("id"))
        if note_id == "-1":
            separator = note.find(w("p"))
            if separator is not None:
                set_paragraph_layout(
                    separator,
                    before=0,
                    after=0,
                    line=180,
                    first_line=0,
                    right=3600,
                    alignment="left",
                )
        elif note_id == "0":
            continue
        for paragraph in note.findall(w("p")):
            set_style_id(paragraph, "FootnoteText")
            set_paragraph_layout(
                paragraph,
                before=0,
                after=0,
                line=210,
                first_line=0,
                alignment="both",
            )
        for run in note.iter(w("r")):
            rpr = run_properties(run)
            apply_run_style(rpr, latin=latin, cjk=cjk, size=18, color="000000")
            if run.find(w("footnoteRef")) is not None:
                vert = ensure_child(rpr, w("vertAlign"))
                set_val(vert, "superscript")
                reorder_run_properties(rpr)


def resize_inline_drawings(document: ET.Element) -> None:
    """Fit existing images inside the 4.5 inch body column without distorting them."""

    maximum = 4114800  # 4.5 inches in EMU.
    for inline in document.iter(qn("http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing", "inline")):
        extent = inline.find(qn("http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing", "extent"))
        if extent is None:
            continue
        try:
            width = int(extent.get("cx", "0"))
            height = int(extent.get("cy", "0"))
        except ValueError:
            continue
        if not width or width <= maximum:
            continue
        resized_height = max(1, round(height * maximum / width))
        extent.set("cx", str(maximum))
        extent.set("cy", str(resized_height))
        for drawing_extent in inline.iter(qn("http://schemas.openxmlformats.org/drawingml/2006/main", "ext")):
            drawing_extent.set("cx", str(maximum))
            drawing_extent.set("cy", str(resized_height))


def footnote_counts(document: ET.Element, footnotes: ET.Element) -> tuple[int, int]:
    references = sum(1 for _ in document.iter(w("footnoteReference")))
    notes = sum(
        1
        for note in footnotes.findall(w("footnote"))
        if (note.get(w("id")) or "").lstrip("-").isdigit() and int(note.get(w("id"), "-1")) > 0
    )
    return references, notes


def validate_members(members: dict[str, bytes], path: Path) -> tuple[int, int]:
    required = {
        "word/document.xml",
        "word/styles.xml",
        "word/footnotes.xml",
        "word/settings.xml",
        "word/_rels/document.xml.rels",
        "[Content_Types].xml",
        "word/header1.xml",
        "word/header2.xml",
        "word/header3.xml",
    }
    missing = sorted(required - members.keys())
    if missing:
        raise ValueError(f"{path}: missing OOXML members: {', '.join(missing)}")
    document = parse_xml(members["word/document.xml"], "word/document.xml")
    footnotes = parse_xml(members["word/footnotes.xml"], "word/footnotes.xml")
    content_types = parse_xml(members["[Content_Types].xml"], "[Content_Types].xml")
    if content_types.tag != ct("Types") or b"<Types xmlns=\"" not in members["[Content_Types].xml"]:
        raise ValueError(f"{path}: [Content_Types].xml must retain its default namespace")
    body = document.find(w("body"))
    section = body.find(w("sectPr")) if body is not None else None
    margin = section.find(w("pgMar")) if section is not None else None
    if margin is None or margin.get(w("left")) != "2880" or margin.get(w("right")) != "2880":
        raise ValueError(f"{path}: expected 2 inch left/right margins")
    references, notes = footnote_counts(document, footnotes)
    if references != notes:
        raise ValueError(f"{path}: {references} footnote references but {notes} footnotes")
    return references, notes


def read_docx(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise ValueError(f"{path}: corrupt ZIP member {corrupt}")
        return {name: archive.read(name) for name in archive.namelist()}


def write_docx(path: Path, members: dict[str, bytes]) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, payload in members.items():
                archive.writestr(name, payload)
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def apply_layout(path: Path, *, latin: str, cjk: str, year: str, check_only: bool) -> tuple[int, int]:
    if not path.is_file():
        raise ValueError(f"DOCX not found: {path}")
    members = read_docx(path)
    pre_document = parse_xml(members["word/document.xml"], "word/document.xml")
    pre_footnotes = parse_xml(members["word/footnotes.xml"], "word/footnotes.xml")
    before_references, before_notes = footnote_counts(pre_document, pre_footnotes)
    if before_references != before_notes:
        raise ValueError(
            f"{path}: source has {before_references} footnote references but {before_notes} footnotes"
        )
    if check_only:
        return validate_members(members, path)

    document = pre_document
    styles = parse_xml(members["word/styles.xml"], "word/styles.xml")
    footnotes = pre_footnotes
    settings = parse_xml(members["word/settings.xml"], "word/settings.xml")
    relationships = parse_xml(members["word/_rels/document.xml.rels"], "word/_rels/document.xml.rels")
    content_types = parse_xml(members["[Content_Types].xml"], "[Content_Types].xml")

    configure_styles(styles, latin=latin, cjk=cjk)
    normalize_run_fonts(document, latin=latin, cjk=cjk)
    layout_document_body(document, latin=latin, cjk=cjk)
    configure_section(document)
    resize_inline_drawings(document)
    configure_footnotes(footnotes, latin=latin, cjk=cjk)
    configure_settings(settings)
    configure_relationships(relationships)
    configure_content_types(content_types)

    font_table_member = "word/fontTable.xml"
    if font_table_member in members:
        font_table = parse_xml(members[font_table_member], font_table_member)
        configure_font_table(font_table, latin=latin, cjk=cjk)
        members[font_table_member] = serialize(font_table)

    members["word/document.xml"] = serialize(document)
    members["word/styles.xml"] = serialize(styles)
    members["word/footnotes.xml"] = serialize(footnotes)
    members["word/settings.xml"] = serialize(settings)
    members["word/_rels/document.xml.rels"] = serialize(relationships)
    members["[Content_Types].xml"] = serialize_content_types(content_types)
    members.update(make_headers(year=year))

    after_references, after_notes = validate_members(members, path)
    if (before_references, before_notes) != (after_references, after_notes):
        raise ValueError(
            f"{path}: footnote count changed from {before_references}/{before_notes} "
            f"to {after_references}/{after_notes}"
        )
    write_docx(path, members)

    # Verify the actual ZIP, not only the in-memory replacement map.
    validated = read_docx(path)
    return validate_members(validated, path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply Harvard JOLT-style Word layout without altering manuscript text."
    )
    parser.add_argument(
        "documents",
        metavar="DOCX",
        nargs="*",
        type=Path,
        default=[
            Path("output/docx/before-the-merits.docx"),
            Path("output/docx/实体审理前.docx"),
        ],
        help="DOCX files to format (defaults to the two published outputs).",
    )
    parser.add_argument("--latin-font", default="Garamond")
    parser.add_argument("--cjk-font", default="Songti SC")
    parser.add_argument("--year", default="2026")
    parser.add_argument("--check", action="store_true", help="Validate a previously formatted DOCX without rewriting it.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        for document in args.documents:
            references, notes = apply_layout(
                document.resolve(),
                latin=args.latin_font,
                cjk=args.cjk_font,
                year=args.year,
                check_only=args.check,
            )
            action = "validated" if args.check else "formatted"
            print(f"{action}: {document} (footnotes: {references}/{notes})")
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
