#!/usr/bin/env python3
"""Deterministic citation-integrity check over a research report's reference list.

WHY (2026-09-23): agy 1.2.9, running `/agy:research --intensity high`, produced a report that
assigned the SAME arXiv id (2410.02694) to two different papers (NoLiMa and HELMET) — a
duplicate-id/mismatched-title citation that the model's own anti-hallucination prompt rules did
not catch. Prompt-level instructions ("do not fabricate citations") are necessary but not
sufficient; this script is a cheap, zero-tokens, deterministic pass that runs AFTER agy writes the
report and catches the one class of citation error that is checkable without opening every URL:
the same URL/id cited under two materially different titles.

This does NOT verify that a URL resolves or that the cited fact actually appears on the page —
that needs a real HTTP fetch, which this stdlib-only script deliberately does not do (no network
calls from this plugin's own scripts). It only catches internal inconsistency in the report
itself. Report it to the user as "needs manual verification", never as "confirmed wrong".

Usage:
  python verify_citations.py REPORT.md

Exits 0 always (this is advisory, never a hard failure). Prints one line per warning found, or
nothing if none. Looks for a "## References" or "## Sources" section with lines shaped
"N. [Title](URL) — ...".
"""
import re
import sys

# Force UTF-8 stdout regardless of the platform's console codepage (Windows'
# default cp1252/cp932 mangles the em dash below into replacement chars when a
# UTF-8-expecting caller reads it). Python 3.7+.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


# Two reference shapes seen in practice:
#   1) markdown link, as instructed by this plugin's own templates: "N. [Title](URL) — ..."
#   2) citation style, as agy 1.2.9 actually produced on 2026-09-23: '* [N] Publisher, "Title", URL, date.'
REF_LINE_MD = re.compile(r'^\s*\d+\.\s*\[(?P<title>[^\]]+)\]\((?P<url>\S+?)\)')
REF_LINE_CITATION = re.compile(r'\[\d+\][^"]*"(?P<title>[^"]+)",\s*(?P<url>https?://\S+?),')
SECTION_HEADING = re.compile(r'^#{1,3}\s*(References|Sources|Referencias|Fuentes)\s*$', re.IGNORECASE)


def normalize_url(url):
    url = url.strip().rstrip('/')
    url = re.sub(r'^https?://(www\.)?', '', url, flags=re.IGNORECASE)
    return url.lower()


def extract_references(text):
    """Return [(title, url)] from the first References/Sources section found.
    Falls back to scanning the whole file for numbered [Title](URL) lines if no
    such heading exists (some templates may omit it or use a different label)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if SECTION_HEADING.match(line.strip()):
            start = i + 1
            break
    scope = lines[start:] if start is not None else lines
    refs = []
    for line in scope:
        if start is not None and line.strip().startswith('#'):
            break  # next section
        m = REF_LINE_MD.match(line) or REF_LINE_CITATION.search(line)
        if m:
            refs.append((m.group('title').strip(), m.group('url').strip()))
    return refs


def find_warnings(refs):
    by_url = {}
    for title, url in refs:
        key = normalize_url(url)
        by_url.setdefault(key, set()).add(title.strip().lower())
    warnings = []
    for key, titles in by_url.items():
        if len(titles) > 1:
            warnings.append(
                'Mismo URL/id citado para titulos distintos ({}): "{}" '
                '— una de las dos referencias esta mal asignada, confirmar antes de citar.'.format(
                    key, '" / "'.join(sorted(titles))))
    return warnings


def main():
    if len(sys.argv) != 2:
        print('Usage: python verify_citations.py REPORT.md', file=sys.stderr)
        return 0
    path = sys.argv[1]
    try:
        with open(path, encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f'verify_citations: could not read {path}: {e}', file=sys.stderr)
        return 0
    refs = extract_references(text)
    if not refs:
        return 0
    warnings = find_warnings(refs)
    for w in warnings:
        print(w)
    return 0


if __name__ == '__main__':
    sys.exit(main())
