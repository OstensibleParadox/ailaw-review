from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "footnote_to_docx.py"


def load_converter():
    spec = importlib.util.spec_from_file_location("footnote_to_docx", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load converter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONVERTER = load_converter()


class FootnoteConverterTests(unittest.TestCase):
    def run_converter(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def rewrite_docx_xml(
        self,
        source: Path,
        destination: Path,
        member: str,
        mutate,
    ) -> None:
        with zipfile.ZipFile(source) as archive:
            members = {name: archive.read(name) for name in archive.namelist()}
        root = ET.fromstring(members[member])
        mutate(root)
        members[member] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, payload in members.items():
                archive.writestr(name, payload)

    def reportlab_canvas(self, path: Path):
        try:
            from reportlab.pdfgen import canvas
        except ModuleNotFoundError:
            self.skipTest("reportlab is required")
        return canvas.Canvas(str(path), pagesize=(612, 792))

    def draw_numbered_note(self, page, label: str, body: str, note: str) -> None:
        from reportlab.pdfbase.pdfmetrics import stringWidth

        page.setFont("Times-Roman", 12)
        page.drawString(72, 700, body)
        page.setFont("Times-Roman", 7)
        page.drawString(72 + stringWidth(body, "Times-Roman", 12), 704, label)
        page.setLineWidth(0.5)
        page.line(72, 125, 259, 125)
        page.setFont("Times-Roman", 7)
        page.drawString(81, 105, label)
        page.setFont("Times-Roman", 10)
        page.drawString(89, 105, note)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_latex_produces_true_word_footnotes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="footnote-latex-test-") as temp_name:
            temp = Path(temp_name)
            source = temp / "sample.tex"
            output = temp / "sample.docx"
            source.write_text(
                r"""\documentclass{article}
\newcommand{\lrfootnote}[1]{\footnote{#1}}
\begin{document}
First sentence\footnote{First note with \emph{emphasis} and A\&B}.
中文正文\lrfootnote{第二条中文脚注。}
A split note\footnotemark{} remains linked.\footnotetext{Third note from mark and text.}
\end{document}
""",
                encoding="utf-8",
            )
            completed = self.run_converter(
                str(source),
                "-o",
                str(output),
                "--latex-backend",
                "pandoc",
                "--no-review-json",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = CONVERTER.validate_docx_footnotes(output, expected_count=3)
            self.assertTrue(report["valid"], report["errors"])
            self.assertEqual(len(report["reference_ids"]), 3)
            self.assertIn("第二条中文脚注", " ".join(report["note_texts"]))

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_synthetic_pdf_recovers_one_note_in_strict_mode(self) -> None:
        try:
            from reportlab.pdfbase.pdfmetrics import stringWidth
            from reportlab.pdfgen import canvas
        except ModuleNotFoundError:
            self.skipTest("reportlab is required")
        try:
            import pdfplumber  # noqa: F401
        except ModuleNotFoundError:
            self.skipTest("pdfplumber is required")

        with tempfile.TemporaryDirectory(prefix="footnote-pdf-test-") as temp_name:
            temp = Path(temp_name)
            source = temp / "sample.pdf"
            output = temp / "sample.docx"
            page = canvas.Canvas(str(source), pagesize=(612, 792))
            body = "Synthetic PDF sentence with a real footnote."
            page.setFont("Times-Roman", 12)
            page.drawString(72, 700, body)
            page.setFont("Times-Roman", 7)
            page.drawString(72 + stringWidth(body, "Times-Roman", 12), 704, "1")
            page.setLineWidth(0.5)
            page.line(72, 125, 259, 125)
            page.setFont("Times-Roman", 7)
            page.drawString(81, 105, "1")
            page.setFont("Times-Roman", 10)
            page.drawString(85, 105, "Recovered from page-bottom text.")
            page.showPage()
            page.save()

            completed = self.run_converter(
                str(source),
                "-o",
                str(output),
                "--no-review-json",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = CONVERTER.validate_docx_footnotes(output, expected_count=1)
            self.assertTrue(report["valid"], report["errors"])
            self.assertIn("Recovered from page-bottom text", report["note_texts"][0])

    def test_decimal_continuation_is_not_a_new_footnote(self) -> None:
        chars = [
            {"text": char, "size": 10.0, "x0": index * 5.0, "x1": index * 5.0 + 4.0}
            for index, char in enumerate("5.71–5.97")
        ]
        line = CONVERTER.PdfLine(
            page=1,
            text="5.71–5.97",
            x0=72.0,
            x1=120.0,
            top=650.0,
            bottom=660.0,
            median_size=10.0,
            max_size=10.0,
            chars=chars,
        )
        self.assertIsNone(CONVERTER.note_label_from_line(line, 12.0))

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_validator_rejects_malformed_footnote_plumbing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="footnote-validator-test-") as temp_name:
            temp = Path(temp_name)
            source = temp / "sample.tex"
            valid = temp / "valid.docx"
            source.write_text(
                r"""\documentclass{article}
\begin{document}
Body\footnote{A nonempty note.}
\end{document}
""",
                encoding="utf-8",
            )
            completed = self.run_converter(
                str(source),
                "-o",
                str(valid),
                "--latex-backend",
                "pandoc",
                "--no-review-json",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

            external = temp / "external.docx"

            def make_external(root: ET.Element) -> None:
                relationship = next(
                    item
                    for item in root
                    if item.attrib.get("Type") == CONVERTER.FOOTNOTE_REL
                )
                relationship.set("TargetMode", "External")

            self.rewrite_docx_xml(
                valid,
                external,
                "word/_rels/document.xml.rels",
                make_external,
            )
            report = CONVERTER.validate_docx_footnotes(external, expected_count=1)
            self.assertFalse(report["valid"])
            self.assertTrue(any("TargetMode" in error for error in report["errors"]))

            malformed_note = temp / "malformed-note.docx"

            def remove_marker_and_text(root: ET.Element) -> None:
                for note in root.findall(f"{{{CONVERTER.W_NS}}}footnote"):
                    if int(note.attrib.get(f"{{{CONVERTER.W_NS}}}id", "-1")) <= 0:
                        continue
                    for parent in note.iter():
                        for child in list(parent):
                            if child.tag == f"{{{CONVERTER.W_NS}}}footnoteRef":
                                parent.remove(child)
                            elif child.tag == f"{{{CONVERTER.W_NS}}}t":
                                child.text = ""

            self.rewrite_docx_xml(
                valid,
                malformed_note,
                "word/footnotes.xml",
                remove_marker_and_text,
            )
            report = CONVERTER.validate_docx_footnotes(malformed_note, expected_count=1)
            self.assertFalse(report["valid"])
            self.assertTrue(any("w:footnoteRef" in error for error in report["errors"]))
            self.assertTrue(any("没有文本内容" in error for error in report["errors"]))

            wrong_root = temp / "wrong-root.docx"

            def replace_root(root: ET.Element) -> None:
                root.tag = f"{{{CONVERTER.W_NS}}}endnotes"

            self.rewrite_docx_xml(
                valid,
                wrong_root,
                "word/footnotes.xml",
                replace_root,
            )
            report = CONVERTER.validate_docx_footnotes(wrong_root, expected_count=1)
            self.assertFalse(report["valid"])
            self.assertTrue(any("根元素" in error for error in report["errors"]))

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_pdf_strict_mode_rejects_zero_detected_notes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="footnote-zero-test-") as temp_name:
            temp = Path(temp_name)
            source = temp / "zero.pdf"
            output = temp / "zero.docx"
            page = self.reportlab_canvas(source)
            page.setFont("Times-Roman", 12)
            page.drawString(72, 700, "Text-only PDF whose lack of footnotes cannot be verified.")
            page.showPage()
            page.save()
            completed = self.run_converter(str(source), "-o", str(output), "--no-review-json")
            self.assertEqual(completed.returncode, 2)
            self.assertIn("没有检测到任何脚注", completed.stderr)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_duplicate_superscript_cannot_steal_note_silently(self) -> None:
        try:
            from reportlab.pdfbase.pdfmetrics import stringWidth
        except ModuleNotFoundError:
            self.skipTest("reportlab is required")
        with tempfile.TemporaryDirectory(prefix="footnote-marker-test-") as temp_name:
            temp = Path(temp_name)
            source = temp / "duplicate-marker.pdf"
            output = temp / "duplicate-marker.docx"
            page = self.reportlab_canvas(source)
            first = "Formula x"
            page.setFont("Times-Roman", 12)
            page.drawString(72, 700, first)
            first_x = 72 + stringWidth(first, "Times-Roman", 12)
            page.setFont("Times-Roman", 7)
            page.drawString(first_x, 704, "1")
            second = " followed by the actual reference"
            page.setFont("Times-Roman", 12)
            page.drawString(first_x + 6, 700, second)
            page.setFont("Times-Roman", 7)
            page.drawString(first_x + 6 + stringWidth(second, "Times-Roman", 12), 704, "1")
            page.setLineWidth(0.5)
            page.line(72, 125, 259, 125)
            page.setFont("Times-Roman", 7)
            page.drawString(81, 105, "1")
            page.setFont("Times-Roman", 10)
            page.drawString(89, 105, "Only one source note exists.")
            page.showPage()
            page.save()
            completed = self.run_converter(str(source), "-o", str(output), "--no-review-json")
            self.assertEqual(completed.returncode, 2)
            self.assertIn("未配对疑似正文脚注号", completed.stderr)

    def test_running_headers_are_removed_by_cross_page_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory(prefix="footnote-header-test-") as temp_name:
            source = Path(temp_name) / "headers.pdf"
            page = self.reportlab_canvas(source)
            for number in range(1, 4):
                page.setFont("Times-Roman", 10)
                page.drawString(72, 760, f"Example Law Review {number}")
                page.setFont("Times-Roman", 12)
                page.drawString(72, 700, f"Distinct body content on page {number}.")
                page.showPage()
            page.save()
            pages, _warnings = CONVERTER.extract_pdf_pages(source)
            self.assertEqual(
                [line.text for item in pages for line in item.removed_running_lines],
                ["Example Law Review 1", "Example Law Review 2", "Example Law Review 3"],
            )
            self.assertFalse(
                any("Example Law Review" in line.text for item in pages for line in item.body_lines)
            )

    def test_line_end_hyphens_are_preserved_and_urls_are_repaired(self) -> None:
        repairs: list[dict[str, str]] = []
        self.assertEqual(CONVERTER.join_wrapped_lines(["high-", "impact"]), "high-impact")
        recovered = CONVERTER.join_wrapped_lines(
            ["url: https://psas.sc", "ripts.mit.edu/file.pdf (visited on 01/01/2026)."],
            repairs,
        )
        self.assertIn("https://psas.scripts.mit.edu/file.pdf", recovered)
        self.assertTrue(repairs)
        same_line_repairs: list[dict[str, str]] = []
        recovered = CONVERTER.join_wrapped_lines(
            ["url: https://example.com/a b.pdf (visited on 01/01/2026)."],
            same_line_repairs,
        )
        self.assertIn("https://example.com/ab.pdf", recovered)
        self.assertTrue(same_line_repairs)

    def test_nonadjacent_page_text_is_not_appended_to_old_note(self) -> None:
        previous = CONVERTER.PdfNote(
            key="p1n1",
            page=1,
            label="1",
            lines=["Original note."],
            bbox=(72.0, 650.0, 300.0, 660.0),
            boundary_kind="separator-rule",
            last_content_page=1,
        )
        chars = [
            {"text": char, "size": 10.0, "x0": 72.0 + index * 5, "x1": 76.0 + index * 5}
            for index, char in enumerate("publisher footer")
        ]
        line = CONVERTER.PdfLine(
            page=3,
            text="publisher footer",
            x0=72.0,
            x1=150.0,
            top=650.0,
            bottom=660.0,
            median_size=10.0,
            max_size=10.0,
            chars=chars,
        )
        notes, _previous, warnings = CONVERTER.parse_page_notes(
            3, [line], 12.0, "separator-rule", previous
        )
        self.assertEqual(notes, [])
        self.assertEqual(previous.lines, ["Original note."])
        self.assertTrue(any("非相邻续行" in warning for warning in warnings))

    def test_multicolumn_detector_flags_sustained_two_column_prose(self) -> None:
        lines: list[object] = []
        for index in range(8):
            for x0, x1, text in (
                (72.0, 275.0, "Left column contains sustained scholarly prose."),
                (330.0, 540.0, "Right column contains sustained scholarly prose."),
            ):
                lines.append(
                    CONVERTER.PdfLine(
                        page=1,
                        text=text,
                        x0=x0,
                        x1=x1,
                        top=100.0 + index * 28.0,
                        bottom=112.0 + index * 28.0,
                        median_size=10.0,
                        max_size=10.0,
                        chars=[],
                    )
                )
        self.assertTrue(CONVERTER.detect_multi_column(lines, 612.0, 792.0))

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_pdf_strict_mode_rejects_number_reset_and_supra(self) -> None:
        with tempfile.TemporaryDirectory(prefix="footnote-numbering-test-") as temp_name:
            temp = Path(temp_name)
            source = temp / "reset.pdf"
            output = temp / "reset.docx"
            page = self.reportlab_canvas(source)
            self.draw_numbered_note(page, "1", "First page claim.", "First note.")
            page.showPage()
            self.draw_numbered_note(
                page,
                "1",
                "Second page claim.",
                "See authority, supra note 1.",
            )
            page.showPage()
            page.save()
            completed = self.run_converter(str(source), "-o", str(output), "--no-review-json")
            self.assertEqual(completed.returncode, 2)
            self.assertIn("编号不是从 1 连续递增", completed.stderr)
            self.assertIn("supra/infra", completed.stderr)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_repository_pdf_best_effort_golden_signals(self) -> None:
        source = ROOT / "output" / "pdf" / "what-is-ai-for-courts.pdf"
        if not source.exists():
            self.skipTest("repository PDF fixture is unavailable")
        ast, review = CONVERTER.pdf_to_pandoc_ast(
            source,
            shutil.which("pandoc") or "pandoc",
            strict=False,
            min_confidence=0.85,
            verbose=False,
        )
        self.assertEqual(review["detected_notes"], 120)
        self.assertEqual(review["matched_notes"], 120)
        self.assertEqual(review["unmatched_markers"], [])
        self.assertGreaterEqual(len(review["removed_running_matter"]), 92)
        self.assertEqual(review["dehyphenations"], [])

        def plain(value) -> str:
            if isinstance(value, dict):
                if value.get("t") == "Str":
                    return str(value.get("c", ""))
                if value.get("t") in {"Space", "SoftBreak", "LineBreak"}:
                    return " "
                return "".join(plain(item) for item in value.values())
            if isinstance(value, list):
                return "".join(plain(item) for item in value)
            return ""

        text = plain(ast["blocks"])
        self.assertNotIn("Generic Law Review", text)
        for compound in ("high-impact", "deployment-control", "self-harm"):
            self.assertIn(compound, text)
        for repaired_url in (
            "https://psas.scripts.mit.edu/home/get_file.php?name=STPA_handbook.pdf",
            "https://ipc.court.gov.cn/zh-cn/news/view-5447.html",
        ):
            self.assertIn(repaired_url, text)
        for broken_fragment in ("https://psas.sc ripts", "ipc.court.gov.cn/zh -cn"):
            self.assertNotIn(broken_fragment, text)


if __name__ == "__main__":
    unittest.main()
