from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "footnote_to_docx.py"


def load_converter():
    spec = importlib.util.spec_from_file_location("footnote_to_docx_safety", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load converter")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CONVERTER = load_converter()


class ConverterSafetyTests(unittest.TestCase):
    def run_converter(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_auto_compiled_backend_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="footnote-fail-closed-") as temp_name:
            temp = Path(temp_name)
            source = temp / "sample.tex"
            source.write_text(
                r"""\documentclass{article}
\newcommand{\lrfootnote}[1]{\footnote{#1}}
\begin{document}Body\lrfootnote{Note.}\end{document}
""",
                encoding="utf-8",
            )
            args = SimpleNamespace(
                latex_backend="auto",
                make4ht=sys.executable,
                footnote_command=[],
                citation_command=[],
            )
            with (
                mock.patch.object(
                    CONVERTER,
                    "convert_latex_make4ht",
                    side_effect=CONVERTER.ConversionError("compiled backend failed"),
                ),
                mock.patch.object(CONVERTER, "convert_latex_pandoc") as fallback,
                self.assertRaises(CONVERTER.ConversionError),
            ):
                CONVERTER.convert_latex(source, temp, args, "pandoc")
            fallback.assert_not_called()

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_review_path_cannot_overwrite_output_or_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="footnote-path-safety-") as temp_name:
            temp = Path(temp_name)
            source = temp / "sample.tex"
            original = r"\documentclass{article}\begin{document}Body\end{document}"
            source.write_text(original, encoding="utf-8")

            output = temp / "sample.docx"
            completed = self.run_converter(
                str(source),
                "-o",
                str(output),
                "--review-json",
                str(output),
            )
            self.assertEqual(completed.returncode, 2)
            self.assertFalse(output.exists())

            completed = self.run_converter(
                str(source),
                "-o",
                str(output),
                "--review-json",
                str(source),
                "--force",
            )
            self.assertEqual(completed.returncode, 2)
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertFalse(output.exists())

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
    def test_custom_review_parent_is_created(self) -> None:
        with tempfile.TemporaryDirectory(prefix="footnote-review-parent-") as temp_name:
            temp = Path(temp_name)
            source = temp / "sample.tex"
            output = temp / "sample.docx"
            review = temp / "nested" / "reports" / "sample.json"
            source.write_text(
                r"\documentclass{article}\begin{document}Body\footnote{Note.}\end{document}",
                encoding="utf-8",
            )
            completed = self.run_converter(
                str(source),
                "-o",
                str(output),
                "--review-json",
                str(review),
                "--latex-backend",
                "pandoc",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(review.is_file())


if __name__ == "__main__":
    unittest.main()
