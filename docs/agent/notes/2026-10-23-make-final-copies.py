#!/usr/bin/env python3
"""Make clean hand-in copies of the research statement and poster outline.

Usage: python3 make_final_copies.py [OUTDIR]
Reads the v3 drafts next to this file, removes the author-only parts, the
trace tags and the drafting parentheses, and writes research-statement-final.md
and poster-outline-final.md to OUTDIR (default: the deliver-1028 directory).
Deterministic; stdlib only; prints what it removed. [STUDENT: ...] slots stay.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/home/brianm/projects/physics/chaos/lpcstudy-wt/deliver-1028")
TAG = re.compile(r"[ \t]*\{[A-Z]\d+[a-z]?(?:\s*(?:,|to)\s*[A-Z]\d+[a-z]?)*\}")
DRAFTY = re.compile(r"[ \t]*\((?:F\d resolved[^)]*|R\d)\)")


def cut(text, start, end):
    i = text.index(start)
    j = text.index(end, i) if end else len(text)
    return text[i:j], text[:i] + text[j:]


def clean(body, label, log):
    n_tags = len(TAG.findall(body))
    body = TAG.sub("", body)
    n_dr = len(DRAFTY.findall(body))
    body = DRAFTY.sub("", body)
    body = re.sub(r"\s*\((?:v3 )?§[^)]*\)(?=[.]? \|$)", "", body, flags=re.M)
    body = body.replace("Header for this section and every copy of it: ", "")
    log.append(f"{label}: removed {n_tags} trace tags, {n_dr} drafting parentheses")
    return body.rstrip() + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = []
    s = (HERE / "2026-10-23-research-statement-v3.md").read_text()
    body, rest = cut(s, "## 1. The research question", None)
    body = body[: body.index("---\n\n## For the author")]
    log.append("statement: removed title paragraph, number rule, tags note, "
               "'What changed', 'For the author' (trace, checklist, open items)")
    out = ("# Research statement: when should a forecaster trust the past, "
           "and when the physics?\n\n" + clean(body, "statement", log))
    (OUT / "research-statement-final.md").write_text(out)

    p = (HERE / "2026-10-23-poster-outline-v3.md").read_text()
    body = p[p.index("## 0. Status"):p.index("## 4. Honesty checklist")]
    log.append("poster: removed header, 'What changed', sections 4 to 7 "
               "(checklist, must-not-say, trace, open items)")
    out = "# Poster outline: when should a forecaster trust the past, and when the physics?\n\n" + clean(body, "poster", log)
    (OUT / "poster-outline-final.md").write_text(out)
    print("\n".join(log))
    print("wrote", OUT / "research-statement-final.md", OUT / "poster-outline-final.md")


main()
