#!/usr/bin/env python3
"""
termlint - terminology canon enforcement for the Who Controls, Who Answers? manuscript.

The canon lives in TERMINOLOGY.yaml. This script is the only thing that decides whether
the source conforms to it. Prose is never the authority; the canon is.

Usage
-----
    python3 scripts/termlint.py                    # lint the source, human output
    python3 scripts/termlint.py --json             # machine output for agents / CI
    python3 scripts/termlint.py --list             # print the canon as a table
    python3 scripts/termlint.py --term visible_operator
    python3 scripts/termlint.py --warnings         # include warn-severity findings
    python3 scripts/termlint.py --actions          # print the non-lintable action items

Exit codes
----------
    0  no error-severity findings
    1  at least one error-severity finding
    2  configuration or usage problem

Suppressing a deliberate exception
----------------------------------
Put a pragma on the offending line or the line before it:

    Some sentence using a front end deliberately.  % termlint: allow front_door
    % termlint: allow-line
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("termlint: PyYAML is required.  pip install pyyaml\n")
    sys.exit(2)


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE) if os.path.basename(HERE) == "scripts" else HERE
CANON = os.path.join(REPO, "TERMINOLOGY.yaml")

PRAGMA_TERM = re.compile(r"%\s*termlint:\s*allow\s+([A-Za-z0-9_]+)")
PRAGMA_LINE = re.compile(r"%\s*termlint:\s*allow-line\b")

# Fields on a term that carry a non-lintable instruction plus a severity.
ACTION_FIELDS = (
    "anchor", "collision", "consolidation", "consistency", "double_definition",
    "assignment_conflict", "list_consistency", "heading_consistency", "ordering",
    "role_discipline",
)


def phrase_pattern(phrase: str, case_sensitive: bool = False) -> re.Pattern:
    """Whole-phrase match, tolerant of line-wrapped whitespace, not matching inside words."""
    parts = [re.escape(p) for p in phrase.split()]
    body = r"\s+".join(parts)
    pat = r"(?<![\w-])" + body + r"(?![\w-])"
    return re.compile(pat, 0 if case_sensitive else re.IGNORECASE)


def load_canon(path: str) -> dict:
    if not os.path.exists(path):
        sys.stderr.write(f"termlint: canon not found at {path}\n")
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def collect_allow_phrases(canon: dict) -> list[re.Pattern]:
    """Canonical and permitted forms are masked before banned forms are scanned, so that a
    banned substring never fires inside a phrase the canon explicitly allows."""
    out = []
    for term in canon.get("terms", []):
        forms = [term.get("canonical", "")]
        forms += term.get("short_forms", []) or []
        exc = term.get("permitted_exception")
        if isinstance(exc, dict) and exc.get("form"):
            forms.append(exc["form"])
        for f in forms:
            if not f or "/" in f:
                continue
            out.append(phrase_pattern(f))
    # longest first so the most specific allowance masks first
    return sorted(out, key=lambda p: -len(p.pattern))


def mask_allowed(line: str, allows: list[re.Pattern]) -> str:
    masked = line
    for pat in allows:
        masked = pat.sub(lambda m: "\x00" * len(m.group(0)), masked)
    return masked


def iter_source_files(canon: dict, roots: list[str] | None) -> list[str]:
    files: list[str] = []
    globs = roots or canon.get("document", {}).get("source_globs", [])
    for g in globs:
        pattern = g if os.path.isabs(g) else os.path.join(REPO, g)
        files.extend(sorted(glob.glob(pattern, recursive=True)))
    return files


def banned_rules(canon: dict):
    """Yield (owner_id, rule) for every banned form in terms and style_rules."""
    for term in canon.get("terms", []):
        for rule in term.get("banned", []) or []:
            if rule.get("replace") is None and rule.get("severity") != "error":
                # advisory-only entries (e.g. "black box") still reported, but as warn
                pass
            yield term["id"], rule
    for sr in canon.get("style_rules", []):
        for rule in sr.get("banned", []) or []:
            yield sr["id"], rule


def lint(canon: dict, files: list[str], include_warnings: bool) -> list[dict]:
    allows = collect_allow_phrases(canon)
    rules = [(oid, r, phrase_pattern(r["form"], r.get("case_sensitive", False)))
             for oid, r in banned_rules(canon)]
    findings: list[dict] = []

    for path in files:
        rel = os.path.relpath(path, REPO)
        with open(path, "r", encoding="utf-8") as fh:
            lines = fh.readlines()

        for n, raw in enumerate(lines, start=1):
            prev = lines[n - 2] if n >= 2 else ""
            if PRAGMA_LINE.search(raw) or PRAGMA_LINE.search(prev):
                continue
            allowed_here = set(PRAGMA_TERM.findall(raw)) | set(PRAGMA_TERM.findall(prev))

            stripped = raw.lstrip()
            if stripped.startswith("%"):
                continue

            masked = mask_allowed(raw, allows)

            for owner_id, rule, pat in rules:
                if owner_id in allowed_here:
                    continue
                sev = rule.get("severity", "error")
                if sev != "error" and not include_warnings:
                    continue
                for m in pat.finditer(masked):
                    findings.append({
                        "file": rel,
                        "line": n,
                        "col": m.start() + 1,
                        "severity": sev,
                        "term": owner_id,
                        "found": raw[m.start():m.end()],
                        "replace": rule.get("replace"),
                        "why": (rule.get("why") or "").strip(),
                        "context": raw.strip()[:160],
                    })

    # A more specific banned form masks a shorter one that overlaps it: "closed manifest"
    # should report once, not also as a bare "manifest".
    def span(f):
        return (f["file"], f["line"], f["col"], f["col"] + len(f["found"]))

    kept = []
    for f in findings:
        _, ln, s, e = span(f)
        covered = any(
            g is not f
            and g["file"] == f["file"] and g["line"] == ln
            and g["col"] <= s and (g["col"] + len(g["found"])) >= e
            and (g["col"], g["col"] + len(g["found"])) != (s, e)
            for g in findings
        )
        if not covered:
            kept.append(f)

    kept.sort(key=lambda f: (f["file"], f["line"], f["col"]))
    return kept


def check_definitions(canon: dict, files: list[str]) -> list[dict]:
    """A term whose define_at names \\term must carry exactly one \\term mark.

    A term whose define_at says MISSING is expected to have none yet; the canon is
    asking for one to be added, so it is reported until it exists. Terms defined by
    Model Act enumeration, a heading, or the title are not \\term-marked and are skipped.
    """
    blob = {}
    for path in files:
        with open(path, "r", encoding="utf-8") as fh:
            blob[os.path.relpath(path, REPO)] = fh.read()

    out = []
    for term in canon.get("terms", []):
        if term.get("status") not in ("coined", "borrowed"):
            continue
        canonical = term.get("canonical", "")
        define_at = term.get("define_at", "") or ""
        if "/" in canonical:
            continue

        wants_term = "\\term" in define_at
        wants_added = "MISSING" in define_at
        if not (wants_term or wants_added):
            continue

        pat = re.compile(r"\\term\{" + re.escape(canonical) + r"\}", re.IGNORECASE)
        hits = [(f, len(pat.findall(t))) for f, t in blob.items()]
        total = sum(c for _, c in hits)

        if total == 0:
            out.append({
                "term": term["id"],
                "kind": "needs-definition" if wants_added else "undefined",
                "count": 0,
                "detail": f'no \\term{{{canonical}}} anywhere; canon says: {define_at}',
            })
        elif total > 1:
            where = ", ".join(f"{f} x{c}" for f, c in hits if c)
            out.append({
                "term": term["id"], "kind": "multiply-defined", "count": total,
                "detail": f"\\term{{{canonical}}} appears {total} times ({where}); "
                          f"canon says: {define_at}",
            })
    return out


def collect_actions(canon: dict) -> list[dict]:
    out = []
    for term in canon.get("terms", []):
        for field in ACTION_FIELDS:
            node = term.get(field)
            if not isinstance(node, dict):
                continue
            action = node.get("action") or node.get("resolution") or node.get("note")
            if not action:
                continue
            out.append({
                "term": term["id"],
                "kind": field,
                "severity": node.get("severity", "warn"),
                "action": " ".join(str(action).split()),
                "cite": " ".join(str(node.get("cite", "")).split()) or None,
            })
    for sr in canon.get("style_rules", []):
        if sr.get("why") and not sr.get("banned"):
            out.append({
                "term": sr["id"], "kind": "style_rule",
                "severity": sr.get("severity", "warn"),
                "action": " ".join(str(sr["why"]).split()), "cite": None,
            })
    order = {"error": 0, "warn": 1}
    out.sort(key=lambda a: (order.get(a["severity"], 2), a["term"]))
    return out


C = {"red": "\033[31m", "yel": "\033[33m", "dim": "\033[2m",
     "bold": "\033[1m", "off": "\033[0m"}


def paint(s: str, key: str, on: bool) -> str:
    return f"{C[key]}{s}{C['off']}" if on else s


def main() -> int:
    ap = argparse.ArgumentParser(description="Enforce the terminology canon.")
    ap.add_argument("paths", nargs="*", help="Override the canon's source globs.")
    ap.add_argument("--canon", default=CANON)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list", action="store_true", help="Print the canon as a table.")
    ap.add_argument("--term", help="Print one term's full entry.")
    ap.add_argument("--actions", action="store_true", help="Print non-lintable action items.")
    ap.add_argument("--warnings", "-w", action="store_true", help="Include warn severity.")
    ap.add_argument("--no-color", action="store_true")
    args = ap.parse_args()

    canon = load_canon(args.canon)
    color = sys.stdout.isatty() and not args.no_color

    if args.term:
        for t in canon.get("terms", []):
            if t["id"] == args.term:
                print(yaml.safe_dump(t, allow_unicode=True, sort_keys=False))
                return 0
        sys.stderr.write(f"termlint: no term with id {args.term!r}\n")
        return 2

    if args.list:
        rows = [(t["id"], t.get("status", ""), t.get("canonical", "")) for t in canon["terms"]]
        w0 = max(len(r[0]) for r in rows)
        w1 = max(len(r[1]) for r in rows)
        print(paint(f"{'ID'.ljust(w0)}  {'STATUS'.ljust(w1)}  CANONICAL FORM", "bold", color))
        for r in rows:
            print(f"{r[0].ljust(w0)}  {r[1].ljust(w1)}  {r[2]}")
        print(f"\n{len(rows)} terms.")
        return 0

    if args.actions:
        actions = collect_actions(canon)
        if args.json:
            print(json.dumps(actions, indent=2, ensure_ascii=False))
            return 0
        for a in actions:
            tag = paint("MUST", "red", color) if a["severity"] == "error" else paint("should", "yel", color)
            print(f"{tag}  {paint(a['term'], 'bold', color)} [{a['kind']}]")
            print(f"      {a['action']}")
            if a["cite"]:
                print(f"      {paint('cite: ' + a['cite'], 'dim', color)}")
            print()
        errs = sum(1 for a in actions if a["severity"] == "error")
        print(f"{len(actions)} action items, {errs} required.")
        return 0

    files = iter_source_files(canon, args.paths or None)
    if not files:
        sys.stderr.write("termlint: no source files matched\n")
        return 2

    findings = lint(canon, files, include_warnings=args.warnings)
    defects = check_definitions(canon, files)

    if args.json:
        print(json.dumps({"findings": findings, "definitions": defects,
                          "files": len(files)}, indent=2, ensure_ascii=False))
        return 1 if any(f["severity"] == "error" for f in findings) or defects else 0

    for f in findings:
        tag = paint("error", "red", color) if f["severity"] == "error" else paint("warn ", "yel", color)
        loc = paint(f"{f['file']}:{f['line']}:{f['col']}", "bold", color)
        print(f"{loc}: {tag}: {f['found']!r} [{f['term']}]")
        if f["replace"]:
            print(f"    -> {f['replace']}")
        if f["why"]:
            print(f"    {paint(' '.join(f['why'].split()), 'dim', color)}")

    if defects:
        print()
        for d in defects:
            print(f"{paint('definition', 'bold', color)}: {paint('error', 'red', color)}: "
                  f"[{d['term']}] {d['detail']}")

    n_err = sum(1 for f in findings if f["severity"] == "error")
    n_warn = sum(1 for f in findings if f["severity"] == "warn")
    print(f"\n{len(files)} files, {n_err} errors, {n_warn} warnings, "
          f"{len(defects)} definition defects.")
    if not args.warnings and not n_warn:
        print("(run with -w to include warn-severity findings)")
    print("Non-lintable action items: python3 scripts/termlint.py --actions")

    return 1 if (n_err or defects) else 0


if __name__ == "__main__":
    sys.exit(main())
