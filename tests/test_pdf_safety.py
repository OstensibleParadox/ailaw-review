from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "footnote_to_docx.py"


def load_converter():
    spec = importlib.util.spec_from_file_location("footnote_to_docx_pdf_safety", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load converter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONVERTER = load_converter()

try:
    import pdfplumber  # noqa: F401
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas
except ModuleNotFoundError:
    PDF_FIXTURE_DEPS = False
else:
    PDF_FIXTURE_DEPS = True


@unittest.skipUnless(PDF_FIXTURE_DEPS, "reportlab and pdfplumber are required")
class PdfSafetyTests(unittest.TestCase):
    def test_strict_mode_rejects_unmatched_small_body_superscript_with_zero_notes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdf-safety-unmatched-marker-") as temp_name:
            source = Path(temp_name) / "unmatched-marker.pdf"
            page = canvas.Canvas(str(source), pagesize=(612, 792))
            body = "A body sentence with an unmatched superscript marker"
            page.setFont("Times-Roman", 12)
            page.drawString(72, 700, body)
            page.setFont("Times-Roman", 7)
            page.drawString(72 + stringWidth(body, "Times-Roman", 12), 704, "1")
            page.showPage()
            page.save()

            pages, _warnings = CONVERTER.extract_pdf_pages(source)
            markers, _marker_warnings = CONVERTER.collect_page_markers(pages[0])
            self.assertTrue(
                any(marker.label == "1" and marker.plausible for marker in markers),
                "fixture must contain a plausible unmatched body superscript",
            )

            pandoc = shutil.which("pandoc") or "__pandoc_should_not_be_called__"
            with self.assertRaises(CONVERTER.ConversionError) as caught:
                CONVERTER.pdf_to_pandoc_ast(
                    source,
                    pandoc,
                    strict=True,
                    min_confidence=0.85,
                    verbose=False,
                )
            message = str(caught.exception)
            self.assertIn("没有检测到任何脚注", message)
            self.assertIn("未配对疑似正文脚注号", message)

    def test_repeated_running_header_is_removed_from_body(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdf-safety-running-header-") as temp_name:
            source = Path(temp_name) / "running-header.pdf"
            header = "AI RESPONSIBILITY | WORKING PAPER"
            page = canvas.Canvas(str(source), pagesize=(612, 792))
            for number in range(1, 4):
                page.setFont("Times-Roman", 9)
                page.drawString(72, 765, header)
                page.setFont("Times-Roman", 12)
                page.drawString(72, 640, f"Unique body paragraph for page {number}.")
                page.setFont("Times-Roman", 9)
                page.drawCentredString(306, 30, str(number))
                page.showPage()
            page.save()

            pages, _warnings = CONVERTER.extract_pdf_pages(source)
            self.assertEqual(len(pages), 3)
            for number, parsed in enumerate(pages, start=1):
                removed = [line.text for line in parsed.removed_running_lines]
                body = " ".join(line.visible_text for line in parsed.body_lines)
                self.assertIn(header, removed)
                self.assertNotIn(header, body)
                self.assertIn(f"Unique body paragraph for page {number}.", body)

    def test_semantic_line_end_hyphen_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdf-safety-hyphen-") as temp_name:
            source = Path(temp_name) / "semantic-hyphen.pdf"
            page = canvas.Canvas(str(source), pagesize=(612, 792))
            page.setFont("Times-Roman", 12)
            page.drawString(72, 700, "The system uses a high-")
            page.drawString(72, 685, "impact safeguard for deployed models.")
            page.showPage()
            page.save()

            pages, _warnings = CONVERTER.extract_pdf_pages(source)
            preserved: list[dict[str, object]] = []
            paragraphs = CONVERTER.page_paragraphs(pages[0], preserved, [])
            text = " ".join(paragraph for paragraph, _heading in paragraphs)
            self.assertIn("high-impact safeguard", text)
            self.assertNotIn("highimpact safeguard", text)
            self.assertNotIn("high- impact safeguard", text)
            self.assertTrue(preserved, "preserved hyphen should be recorded for review")

    def test_cross_line_url_is_joined_without_space(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pdf-safety-url-") as temp_name:
            source = Path(temp_name) / "wrapped-url.pdf"
            page = canvas.Canvas(str(source), pagesize=(612, 792))
            page.setFont("Times-Roman", 12)
            page.drawString(72, 700, "Source: https://example.com/alpha/")
            page.drawString(72, 685, "beta?x=1&y=2 (visited Aug. 28, 2026).")
            page.showPage()
            page.save()

            pages, _warnings = CONVERTER.extract_pdf_pages(source)
            repairs: list[dict[str, object]] = []
            paragraphs = CONVERTER.page_paragraphs(pages[0], [], repairs)
            text = " ".join(paragraph for paragraph, _heading in paragraphs)
            expected = "https://example.com/alpha/beta?x=1&y=2"
            self.assertIn(expected, text)
            self.assertNotIn("https://example.com/alpha/ beta", text)
            self.assertTrue(
                any(repair.get("kind") == "url-line-wrap" for repair in repairs),
                "URL line-wrap repair should be recorded for review",
            )

    def test_cross_page_url_is_joined_and_rechecked(self) -> None:
        paragraphs = [
            (1, "Source: https://www", None),
            (
                2,
                ".example.com/path/alpha- 1234 (visited Aug. 28, 2026).",
                None,
            ),
        ]
        repairs: list[dict[str, object]] = []
        repaired = CONVERTER.repair_split_body_urls(paragraphs, repairs)
        self.assertEqual(len(repaired), 1)
        text = repaired[0][1]
        self.assertIn(
            "https://www.example.com/path/alpha-1234",
            text,
        )
        self.assertFalse(CONVERTER.find_residual_malformed_urls(repaired, []))
        self.assertTrue(
            any(repair.get("kind") == "url-page-wrap" for repair in repairs),
            "cross-page URL repair should be recorded for review",
        )


if __name__ == "__main__":
    unittest.main()
