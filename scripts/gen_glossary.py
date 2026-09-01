#!/usr/bin/env python3
"""Render TERMINOLOGY.yaml as a standalone HTML reference page.

The page is derived from the canon, never hand-edited, so the two cannot drift.
Regenerate after any canon change:

    python3 scripts/gen_glossary.py -o output/terminology.html
"""
from __future__ import annotations

import argparse
import html
import os
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("gen_glossary: PyYAML required.  pip install pyyaml\n")
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE) if os.path.basename(HERE) == "scripts" else HERE

ACTION_FIELDS = ("anchor", "collision", "consolidation", "consistency",
                 "double_definition", "assignment_conflict", "list_consistency",
                 "heading_consistency", "ordering", "role_discipline")

KIND_LABEL = {
    "anchor": "Anchor to the standard term",
    "collision": "Collides with an established term",
    "consolidation": "Three names, one object",
    "consistency": "Internal inconsistency",
    "double_definition": "Defined twice",
    "assignment_conflict": "Assigned to two different actors",
    "list_consistency": "Enumeration differs across the draft",
    "heading_consistency": "Heading does not match the term",
    "ordering": "Used before it is defined",
    "role_discipline": "Role distinction to preserve",
    "style_rule": "Manuscript hygiene",
}

E = html.escape


def sq(v) -> str:
    """Squash whitespace in a YAML block scalar."""
    return " ".join(str(v).split()) if v else ""


CSS = """
:root{
  --ground:#F6F8F7; --panel:#EBEFEE; --card:#FFFFFF;
  --ink:#141817; --ink-2:#4A5654; --ink-3:#77837F;
  --rule:#D5DCDA; --rule-soft:#E4EAE8;
  --accent:#1B5A4B; --accent-soft:#E2EDE8;
  --amber:#7A5F17; --amber-soft:#F1ECDB;
  --serif:"Newsreader",Georgia,serif;
  --sans:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono",Menlo,Consolas,monospace;
  --s1:.4rem; --s2:.75rem; --s3:1.15rem; --s4:1.8rem; --s5:2.75rem; --s6:4.25rem;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#0F1312; --panel:#181D1C; --card:#141918;
  --ink:#E6EAE8; --ink-2:#A2AFAB; --ink-3:#7B8783;
  --rule:#293130; --rule-soft:#1F2625;
  --accent:#6FB69E; --accent-soft:#16302A;
  --amber:#C5A452; --amber-soft:#272113;
}}
:root[data-theme="dark"]{
  --ground:#0F1312; --panel:#181D1C; --card:#141918;
  --ink:#E6EAE8; --ink-2:#A2AFAB; --ink-3:#7B8783;
  --rule:#293130; --rule-soft:#1F2625;
  --accent:#6FB69E; --accent-soft:#16302A;
  --amber:#C5A452; --amber-soft:#272113;
}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font-family:var(--sans);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1060px;margin:0 auto;padding:var(--s5) 1.5rem var(--s6);
  display:flex;flex-direction:column;gap:var(--s5)}
p{margin:0}
code{font-family:var(--mono);font-size:.875em}
cite{font-style:italic}

.eyebrow{font-family:var(--mono);font-size:.688rem;font-weight:500;
  letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3)}

header.mast{display:flex;flex-direction:column;gap:var(--s3)}
.mast h1{font-family:var(--serif);font-weight:500;
  font-size:clamp(2.2rem,5.6vw,3.5rem);line-height:1.05;letter-spacing:-.018em;
  margin:0;text-wrap:balance}
.standfirst{font-family:var(--serif);font-size:clamp(1.05rem,2.2vw,1.28rem);
  line-height:1.5;color:var(--ink-2);max-width:62ch;text-wrap:pretty}
.stats{display:flex;flex-wrap:wrap;gap:.4rem 1.4rem;padding-top:var(--s3);
  border-top:1px solid var(--rule);font-family:var(--mono);font-size:.75rem;
  color:var(--ink-3);font-variant-numeric:tabular-nums}
.stats b{color:var(--accent);font-weight:500}

section{display:flex;flex-direction:column;gap:var(--s4)}
.sec-head{display:flex;flex-direction:column;gap:var(--s2)}
.sec-head h2{font-family:var(--serif);font-weight:500;
  font-size:clamp(1.5rem,3.2vw,2rem);line-height:1.2;margin:0;
  max-width:28ch;text-wrap:balance}
.sec-head p{color:var(--ink-2);max-width:66ch}

.legend{display:grid;gap:var(--s3);grid-template-columns:1fr}
@media(min-width:720px){.legend{grid-template-columns:repeat(3,1fr);gap:var(--s3)}}
.leg{border-top:2px solid var(--rule);padding-top:var(--s2);
  display:flex;flex-direction:column;gap:.35rem}
.leg-anchored{border-top-color:var(--ink-3)}
.leg-coined{border-top-color:var(--accent)}
.leg-borrowed{border-top-color:var(--amber)}
.leg h3{font-family:var(--mono);font-size:.75rem;font-weight:500;
  letter-spacing:.1em;text-transform:uppercase;margin:0}
.leg p{font-size:.875rem;color:var(--ink-2);line-height:1.55}

.act{display:flex;flex-direction:column;gap:var(--s2);
  border-left:2px solid var(--amber);padding:var(--s1) 0 var(--s1) var(--s3)}
.act.req{border-left-color:var(--accent)}
.act-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:.5rem}
.act-term{font-family:var(--mono);font-size:.875rem;font-weight:500;color:var(--ink)}
.act-kind{font-family:var(--mono);font-size:.688rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-3)}
.act p{font-size:.938rem;color:var(--ink-2);line-height:1.58;max-width:72ch}
.act .cite{font-size:.813rem;color:var(--ink-3);font-style:italic;max-width:72ch}
.acts{display:flex;flex-direction:column;gap:var(--s3)}

.controls{display:flex;flex-wrap:wrap;gap:var(--s2);align-items:center;
  position:sticky;top:0;z-index:5;background:var(--ground);
  padding:var(--s2) 0;border-bottom:1px solid var(--rule)}
input[type=search]{font-family:var(--sans);font-size:.938rem;color:var(--ink);
  background:var(--card);border:1px solid var(--rule);border-radius:2px;
  padding:.5rem .7rem;min-width:min(320px,100%);flex:1 1 240px}
input[type=search]::placeholder{color:var(--ink-3)}
.chips{display:flex;gap:.4rem;flex-wrap:wrap}
.chip{font-family:var(--mono);font-size:.75rem;letter-spacing:.04em;
  padding:.4rem .65rem;border:1px solid var(--rule);border-radius:2px;
  background:transparent;color:var(--ink-2);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--ground)}
.count{font-family:var(--mono);font-size:.75rem;color:var(--ink-3);
  font-variant-numeric:tabular-nums;margin-left:auto}

.terms{display:flex;flex-direction:column;gap:0}
.term{display:grid;gap:var(--s2);grid-template-columns:1fr;
  padding:var(--s3) 0;border-bottom:1px solid var(--rule-soft)}
@media(min-width:860px){.term{grid-template-columns:15rem 1fr;gap:var(--s4)}}
.tkey{display:flex;flex-direction:column;gap:.3rem;align-self:start}
.tcanon{font-family:var(--serif);font-size:1.1rem;font-weight:500;
  line-height:1.3;color:var(--ink)}
.tid{font-family:var(--mono);font-size:.75rem;color:var(--ink-3)}
.pill{align-self:flex-start;font-family:var(--mono);font-size:.625rem;
  letter-spacing:.1em;text-transform:uppercase;padding:.15rem .45rem;
  border-radius:2px;margin-top:.15rem}
.p-anchored{background:var(--panel);color:var(--ink-2)}
.p-coined{background:var(--accent-soft);color:var(--accent)}
.p-borrowed{background:var(--amber-soft);color:var(--amber)}
.tbody{display:flex;flex-direction:column;gap:var(--s2)}
.gloss{font-size:.938rem;color:var(--ink-2);line-height:1.58;max-width:70ch}
.meta{font-size:.813rem;color:var(--ink-3);line-height:1.5}
.meta b{font-family:var(--mono);font-weight:500;font-size:.75rem;
  letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)}
.bans{display:flex;flex-direction:column;gap:.35rem;margin:0;padding:0;list-style:none}
.ban{font-size:.875rem;line-height:1.5;color:var(--ink-2)}
.ban .x{font-family:var(--mono);color:var(--ink);text-decoration:line-through;
  text-decoration-color:var(--amber);text-decoration-thickness:1px}
.ban .arrow{color:var(--ink-3);padding:0 .3rem}
.ban .to{font-family:var(--mono);color:var(--accent)}
.ban .sev{font-family:var(--mono);font-size:.625rem;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-3);padding-left:.4rem}
.ban .why{display:block;color:var(--ink-3);font-size:.813rem;
  line-height:1.5;max-width:70ch;padding-top:.1rem}
.empty{padding:var(--s4) 0;color:var(--ink-3);font-size:.938rem}

pre{background:var(--panel);padding:var(--s3);border-radius:2px;overflow-x:auto;
  font-family:var(--mono);font-size:.813rem;line-height:1.7;color:var(--ink-2);margin:0}
footer{border-top:1px solid var(--rule);padding-top:var(--s3);
  font-family:var(--mono);font-size:.75rem;line-height:1.7;color:var(--ink-3);max-width:70ch}
*:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
(function(){
  var q=document.getElementById('q'),
      chips=[].slice.call(document.querySelectorAll('.chip')),
      terms=[].slice.call(document.querySelectorAll('.term')),
      count=document.getElementById('count'),
      empty=document.getElementById('empty'),
      active='all';
  function apply(){
    var s=(q.value||'').trim().toLowerCase(), n=0;
    terms.forEach(function(t){
      var okS = active==='all' || t.dataset.status===active;
      var okQ = !s || t.dataset.text.indexOf(s)>-1;
      var show = okS && okQ;
      t.hidden = !show;
      if(show) n++;
    });
    count.textContent = n + ' of ' + terms.length;
    empty.hidden = n>0;
  }
  q.addEventListener('input',apply);
  chips.forEach(function(c){
    c.addEventListener('click',function(){
      active=c.dataset.status;
      chips.forEach(function(o){o.setAttribute('aria-pressed', String(o===c));});
      apply();
    });
  });
  apply();
})();
"""


def render(canon: dict) -> str:
    terms = canon.get("terms", [])
    styles = canon.get("style_rules", [])

    n_banned = sum(len(t.get("banned") or []) for t in terms) + \
        sum(len(s.get("banned") or []) for s in styles)

    actions = []
    for t in terms:
        for f in ACTION_FIELDS:
            node = t.get(f)
            if isinstance(node, dict):
                txt = node.get("action") or node.get("resolution") or node.get("note")
                if txt:
                    actions.append({
                        "term": t["id"], "kind": f,
                        "sev": node.get("severity", "warn"),
                        "text": sq(txt), "cite": sq(node.get("cite", "")),
                        "why": sq(node.get("why", "") or node.get("problem", "")),
                    })
    for s in styles:
        if s.get("why") and not s.get("banned"):
            actions.append({"term": s["id"], "kind": "style_rule",
                            "sev": s.get("severity", "warn"), "text": sq(s["why"]),
                            "cite": "", "why": ""})
    actions.sort(key=lambda a: (0 if a["sev"] == "error" else 1, a["term"]))
    n_req = sum(1 for a in actions if a["sev"] == "error")

    by_status = {}
    for t in terms:
        by_status[t.get("status", "?")] = by_status.get(t.get("status", "?"), 0) + 1

    out = []
    w = out.append

    w("<title>Front-Door Terminology Canon</title>")
    w('<link rel="preconnect" href="https://fonts.googleapis.com">')
    w('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    w('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
      'family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400'
      '&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600'
      '&display=swap">')
    w(f"<style>{CSS}</style>")
    w('<div class="wrap">')

    # masthead
    w('<header class="mast">')
    w('<div class="eyebrow">Canonical vocabulary · generated from TERMINOLOGY.yaml</div>')
    w("<h1>Front-Door Terminology Canon</h1>")
    w('<p class="standfirst">Every term in <cite>' + E(canon["document"]["title"]) +
      '</cite>, anchored to its standard scholarly or statutory name where one exists, '
      'and marked as the Article\'s own coinage where none does.</p>')
    w('<div class="stats">')
    w(f'<span><b>{len(terms)}</b> terms</span>')
    w("<span>" + " · ".join(f"<b>{v}</b> {E(k)}" for k, v in sorted(by_status.items())) + "</span>")
    w(f'<span><b>{n_banned}</b> banned forms</span>')
    w(f'<span><b>{n_req}</b> required actions</span>')
    w("</div></header>")

    # how it works
    w("<section><div class='sec-head'>")
    w('<div class="eyebrow">01 · How the canon binds</div>')
    w("<h2>The file is the authority, not the prose.</h2>")
    w("<p>Coining a term is legitimate, and this Article does a great deal of it. The failure "
      "mode is not coining. It is coining where a standard term already exists, or coining and "
      "then drifting. Every entry below is classified on that axis.</p>")
    w("<p>A terminology question is settled by editing <code>TERMINOLOGY.yaml</code> and running "
      "the linter, never by editing a sentence. That is what keeps an agent, a co-author and a "
      "cite-checker working from the same vocabulary six months from now.</p>")
    w("</div>")
    w('<div class="legend">')
    for key, body in (
        ("anchored", "A standard scholarly or statutory term already exists and is adopted. "
                     "Use it exactly; do not invent a synonym."),
        ("coined", "The Article's own term for a concept with no standard name. Keep it, define "
                   "it once, and never vary the wording."),
        ("borrowed", "Imported from an adjacent literature. Cite the source at first use and do "
                     "not silently rename what that literature already named."),
    ):
        w(f'<div class="leg leg-{key}"><h3>{key} · {by_status.get(key,0)}</h3><p>{body}</p></div>')
    w("</div></section>")

    # actions
    w("<section><div class='sec-head'>")
    w('<div class="eyebrow">02 · Work no linter can do</div>')
    w(f"<h2>{n_req} required actions, {len(actions)-n_req} advisory.</h2>")
    w("<p>String substitution is the easy half. These are the items where a term is lexically "
      "fine but sits on top of an established meaning in a neighbouring field, or where the "
      "draft assigns one object two owners. Each needs a sentence or a footnote, not a "
      "find-and-replace.</p>")
    w("</div><div class='acts'>")
    for a in actions:
        cls = "act req" if a["sev"] == "error" else "act"
        w(f'<div class="{cls}"><div class="act-head">'
          f'<span class="act-term">{E(a["term"])}</span>'
          f'<span class="act-kind">{E(KIND_LABEL.get(a["kind"], a["kind"]))}</span></div>')
        if a["why"]:
            w(f'<p>{E(a["why"])}</p>')
        w(f'<p>{E(a["text"])}</p>')
        if a["cite"]:
            w(f'<p class="cite">{E(a["cite"])}</p>')
        w("</div>")
    w("</div></section>")

    # the canon
    w("<section><div class='sec-head'>")
    w('<div class="eyebrow">03 · The canon</div>')
    w("<h2>Every term, its permitted forms, and what it replaces.</h2>")
    w("</div>")
    w('<div class="controls">')
    w('<input type="search" id="q" placeholder="Filter by term, gloss, or banned form">')
    w('<div class="chips">')
    w('<button class="chip" data-status="all" aria-pressed="true">all</button>')
    for k in ("anchored", "coined", "borrowed"):
        w(f'<button class="chip" data-status="{k}" aria-pressed="false">{k}</button>')
    w("</div>")
    w('<span class="count" id="count"></span>')
    w("</div>")

    w('<div class="terms">')
    for t in terms:
        status = t.get("status", "coined")
        bans = t.get("banned") or []
        shorts = t.get("short_forms") or []
        haystack = " ".join([
            t["id"], t.get("canonical", ""), sq(t.get("gloss", "")),
            " ".join(shorts), " ".join(b.get("form", "") for b in bans),
        ]).lower()
        w(f'<article class="term" data-status="{E(status)}" data-text="{E(haystack)}">')
        w('<div class="tkey">')
        w(f'<div class="tcanon">{E(t.get("canonical",""))}</div>')
        w(f'<div class="tid">{E(t["id"])}</div>')
        w(f'<span class="pill p-{E(status)}">{E(status)}</span>')
        w("</div><div class='tbody'>")
        if t.get("gloss"):
            w(f'<p class="gloss">{E(sq(t["gloss"]))}</p>')
        if shorts:
            w('<p class="meta"><b>permitted</b> ' +
              " · ".join(f"<code>{E(s)}</code>" for s in shorts) + "</p>")
        if t.get("define_at"):
            w(f'<p class="meta"><b>define at</b> {E(t["define_at"])}</p>')
        if t.get("style"):
            w(f'<p class="meta"><b>style</b> {E(sq(t["style"]))}</p>')
        anch = t.get("anchor")
        if isinstance(anch, dict) and anch.get("family"):
            w(f'<p class="meta"><b>anchor</b> {E(anch["family"])}</p>')
        if bans:
            w('<ul class="bans">')
            for b in bans:
                to = b.get("replace")
                sev = b.get("severity", "error")
                line = f'<span class="x">{E(b.get("form",""))}</span>'
                if to:
                    line += f'<span class="arrow">&rarr;</span><span class="to">{E(to)}</span>'
                line += f'<span class="sev">{E(sev)}</span>'
                why = sq(b.get("why", ""))
                if why:
                    line += f'<span class="why">{E(why)}</span>'
                w(f'<li class="ban">{line}</li>')
            w("</ul>")
        w("</div></article>")
    w("</div>")
    w('<p class="empty" id="empty" hidden>No term matches that filter.</p>')
    w("</section>")

    # linter
    w("<section><div class='sec-head'>")
    w('<div class="eyebrow">04 · Enforcement</div>')
    w("<h2>Run it before every commit.</h2>")
    w("<p>Nonzero exit means the source has drifted from this page. "
      "<code>--actions</code> prints the section 02 items ranked; <code>--json</code> is the "
      "form to hand an agent.</p></div>")
    w("<pre>" + E(
        "python3 scripts/termlint.py            # errors only\n"
        "python3 scripts/termlint.py -w         # include warnings\n"
        "python3 scripts/termlint.py --actions  # the non-lintable work\n"
        "python3 scripts/termlint.py --json     # for agents and CI\n"
        "python3 scripts/termlint.py --list     # the canon as a table\n"
        "python3 scripts/termlint.py --term visible_operator\n\n"
        "# deliberate exception, in the .tex source:\n"
        "some sentence  % termlint: allow front_door"
    ) + "</pre></section>")

    w("<footer>Generated from TERMINOLOGY.yaml by scripts/gen_glossary.py. "
      "Do not edit this page directly &mdash; edit the canon and regenerate, or the two "
      "will drift, which is the failure this whole apparatus exists to prevent.</footer>")
    w("</div>")
    w(f"<script>{JS}</script>")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--canon", default=os.path.join(REPO, "TERMINOLOGY.yaml"))
    ap.add_argument("-o", "--out", default=os.path.join(REPO, "output", "terminology.html"))
    a = ap.parse_args()
    with open(a.canon, "r", encoding="utf-8") as fh:
        canon = yaml.safe_load(fh)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(render(canon))
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
