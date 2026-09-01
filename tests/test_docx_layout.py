from __future__ import annotations

import runpy
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


MODULE = runpy.run_path(
    str(Path(__file__).parents[1] / "scripts" / "apply_harvardjolt_docx_layout.py"),
    run_name="docx_layout_test",
)
w = MODULE["w"]
paragraph_text = MODULE["paragraph_text"]
style_id = MODULE["style_id"]
text_paragraph = MODULE["text_paragraph"]


def document_with_body(*paragraphs: ET.Element) -> ET.Element:
    document = ET.Element(w("document"))
    body = ET.SubElement(document, w("body"))
    body.extend(paragraphs)
    body.append(ET.Element(w("sectPr")))
    return document


class FrontMatterLayoutTests(unittest.TestCase):
    def test_fresh_tex4ht_front_matter_is_normalized(self) -> None:
        marker = text_paragraph("* ", "BodyText")
        note = text_paragraph(
            "*Google Gemini was used for LaTeX formatting. "
            "The authors remain responsible for all claims and citations.",
            "BodyText",
        )
        document = document_with_body(
            text_paragraph(
                "Harvard Journal of Law & Technology (submission draft)",
                "FirstParagraph",
            ),
            text_paragraph(
                "Who Controls, Who Answers A Deployment Front Door for High-Impact AI Litigation",
                "Heading1",
            ),
            text_paragraph("Lucia Yizi Zhang, Peng Zhao", "FirstParagraph"),
            marker,
            text_paragraph("Abstract", "BodyText"),
            text_paragraph("The abstract text.", "BodyText"),
            text_paragraph("Keywords: AI litigation", "BodyText"),
            text_paragraph("Table of Contents", "Heading3"),
            text_paragraph("I Introduction", "FirstParagraph"),
            text_paragraph("I.  Introduction", "Heading3"),
            text_paragraph("Opening paragraph.", "FirstParagraph"),
            text_paragraph("VII.  Conclusion", "Heading3"),
            text_paragraph("Conclusion text.", "FirstParagraph"),
            note,
        )

        expected_title = (
            "Who Controls, Who Answers? A Deployment Front Door for High-Impact AI Litigation"
        )
        title = MODULE["normalize_front_matter"](
            document,
            expected_title=expected_title,
        )
        self.assertEqual(
            title,
            expected_title,
        )
        MODULE["layout_document_body"](document, latin="Garamond", cjk="Songti SC")

        body = document.find(w("body"))
        assert body is not None
        paragraphs = [child for child in body if child.tag == w("p")]
        self.assertEqual(
            [paragraph_text(paragraph) for paragraph in paragraphs[:10]],
            [
                title,
                "Lucia Yizi Zhang, Peng Zhao*",
                "(submission draft)",
                "Abstract",
                "The abstract text.",
                "Keywords: AI litigation",
                "",
                "* Google Gemini was used for LaTeX formatting. "
                "The authors remain responsible for all claims and citations.",
                "Table of Contents",
                "I Introduction",
            ],
        )
        self.assertEqual(
            [style_id(paragraph) for paragraph in paragraphs[:9]],
            [
                "Title",
                "Author",
                "Date",
                "AbstractTitle",
                "Abstract",
                "Abstract",
                "FootnoteText",
                "FootnoteText",
                "TOCHeading",
            ],
        )
        introduction = next(
            paragraph
            for paragraph in paragraphs
            if paragraph_text(paragraph).endswith("Introduction")
            and style_id(paragraph) == "Heading3"
        )
        self.assertIsNotNone(introduction.find(f"{w('pPr')}/{w('pageBreakBefore')}"))

    def test_formatted_chinese_front_matter_is_untouched(self) -> None:
        document = document_with_body(
            text_paragraph(
                "Before the Merits: A Deployment Front Door for High-Impact AI Litigation",
                "Title",
            ),
            text_paragraph("匿名∗", "Author"),
            text_paragraph("(submission draft)", "Date"),
            text_paragraph("摘要", "AbstractTitle"),
        )
        before = ET.tostring(document)
        title = MODULE["normalize_front_matter"](document)
        self.assertEqual(
            title,
            "Before the Merits: A Deployment Front Door for High-Impact AI Litigation",
        )
        self.assertEqual(ET.tostring(document), before)

    def test_running_head_is_derived_from_hybrid_title(self) -> None:
        title = "Who Controls, Who Answers? A Deployment Front Door for High-Impact AI Litigation"
        self.assertEqual(MODULE["derive_short_title"](title), "Who Controls, Who Answers?")
        headers = MODULE["make_headers"](year="2026", short_title="Who Controls, Who Answers?")
        odd = ET.fromstring(headers["word/header2.xml"])
        visible = "".join(node.text or "" for node in odd.iter(w("t")))
        self.assertEqual(visible, "Who Controls, Who Answers?1")


class ConverterArtifactTests(unittest.TestCase):
    def test_empty_cell_figure_table_is_unwrapped(self) -> None:
        table = ET.Element(w("tbl"))
        properties = ET.SubElement(table, w("tblPr"))
        style = ET.SubElement(properties, w("tblStyle"))
        style.set(w("val"), "FigureTable")
        row = ET.SubElement(table, w("tr"))

        empty_cell = ET.SubElement(row, w("tc"))
        empty_paragraph = ET.SubElement(empty_cell, w("p"))
        bookmark_start = ET.SubElement(empty_paragraph, w("bookmarkStart"))
        bookmark_start.set(w("id"), "9")
        bookmark_start.set(w("name"), "figure-anchor")
        bookmark_end = ET.SubElement(empty_paragraph, w("bookmarkEnd"))
        bookmark_end.set(w("id"), "9")

        drawing_cell = ET.SubElement(row, w("tc"))
        drawing_paragraph = ET.SubElement(drawing_cell, w("p"))
        paragraph_properties = ET.SubElement(drawing_paragraph, w("pPr"))
        alignment = ET.SubElement(paragraph_properties, w("jc"))
        alignment.set(w("val"), "center")
        run = ET.SubElement(drawing_paragraph, w("r"))
        ET.SubElement(run, w("drawing"))

        document = document_with_body(table)
        self.assertEqual(MODULE["unwrap_converter_figure_tables"](document), 1)
        body = document.find(w("body"))
        assert body is not None
        self.assertIsNone(body.find(w("tbl")))
        direct_paragraph = body.find(w("p"))
        assert direct_paragraph is not None
        self.assertIsNotNone(direct_paragraph.find(f".//{w('drawing')}"))
        self.assertEqual(
            direct_paragraph.find(w("bookmarkStart")).get(w("name")),
            "figure-anchor",
        )

    def test_table_heading_repeats_and_rows_do_not_split(self) -> None:
        table = ET.Element(w("tbl"))
        properties = ET.SubElement(table, w("tblPr"))
        style = ET.SubElement(properties, w("tblStyle"))
        style.set(w("val"), "Table")
        blank_row = ET.SubElement(table, w("tr"))
        ET.SubElement(ET.SubElement(blank_row, w("tc")), w("p"))
        heading_row = ET.SubElement(table, w("tr"))
        heading_cell = ET.SubElement(heading_row, w("tc"))
        heading_cell.append(
            text_paragraph(
                "Component Required allocation Front-door function",
                "Compact",
            )
        )
        data_row = ET.SubElement(table, w("tr"))
        data_cell = ET.SubElement(data_row, w("tc"))
        data_cell.append(text_paragraph("Data", "Compact"))
        document = document_with_body(table)

        MODULE["configure_data_table_rows"](document)

        rows = table.findall(w("tr"))
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row.find(f"{w('trPr')}/{w('cantSplit')}") is not None for row in rows))
        self.assertIsNotNone(rows[0].find(f"{w('trPr')}/{w('tblHeader')}"))
        self.assertIsNone(rows[1].find(f"{w('trPr')}/{w('tblHeader')}"))

    def test_toc_anchor_suffix_is_repaired(self) -> None:
        paragraph = ET.Element(w("p"))
        hyperlink = ET.SubElement(paragraph, w("hyperlink"))
        hyperlink.set(w("anchor"), "introduction1")
        run = ET.SubElement(hyperlink, w("r"))
        run_properties = ET.SubElement(run, w("rPr"))
        run_style = ET.SubElement(run_properties, w("rStyle"))
        run_style.set(w("val"), "Hyperlink")

        MODULE["retarget_toc_links"](paragraph, {"introduction"})

        self.assertEqual(hyperlink.get(w("anchor")), "introduction")
        self.assertEqual(run_style.get(w("val")), "TOCLink")


if __name__ == "__main__":
    unittest.main()
