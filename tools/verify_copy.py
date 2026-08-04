#!/usr/bin/env python3
"""Release gate: this device is an alternative route to the same
measurement, not a replacement for the instrument it was validated against.

The Millipore EZ-Fit served as the reference instrument in validation — the
thing 3DPLAM's counts were checked against, not a product this project
claims to supersede. Copy that frames it as a replacement or a rated
equivalent overstates what the validation (n=8 sites, one field season)
supports. This gate fails the build if that framing creeps back in,
anywhere the copy ships: the markdown docs and the built site.

Usage:  python3 tools/verify_copy.py                    (scans the defaults)
   or:  python3 tools/verify_copy.py "README.md" "docs/**/*.md"
   or:  python3 -m tools.verify_copy "site/dist/**/*.html"
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BANNED_PHRASES = [
    "replaces the millipore",
    "drop-in replacement",
    "as good as",
    "equivalent to the millipore",
]

# Scanned when no paths are given on the command line: every markdown page
# plus the Astro site *source* (components, layouts, and the copy-holding
# site.json). This catches banned phrasing at the point someone would
# actually type it. It is deliberately not sufficient on its own — see
# tools/README.md and .github/workflows/verify.yml, where a second
# invocation scans the *built* site/dist/**/*.html, because the built HTML
# is what actually ships and could in principle differ from any single
# source file (e.g. text assembled across a template and a data file).
DEFAULT_PATTERNS = [
    "README.md",
    "docs/**/*.md",
    "site/src/**/*.astro",
    "site/src/**/*.md",
    "site/src/**/*.json",
]

TEXT_SUFFIXES = (".md", ".astro", ".json", ".html", ".mdx", ".txt", ".css", ".js")


def find_files(patterns):
    files = set()
    for pattern in patterns:
        for match in glob.glob(pattern, recursive=True):
            if os.path.isfile(match) and match.lower().endswith(TEXT_SUFFIXES):
                files.add(match)
    return sorted(files)


def scan_file(path):
    """Return a list of (line_no, phrase, line_text) hits in `path`."""
    hits = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line_no, line in enumerate(f, start=1):
            lowered = line.lower()
            for phrase in BANNED_PHRASES:
                if phrase in lowered:
                    hits.append((line_no, phrase, line.strip()))
    return hits


def main(patterns=None):
    patterns = patterns if patterns else DEFAULT_PATTERNS
    files = find_files(patterns)
    if not files:
        print("verify_copy: no files matched", file=sys.stderr)
        return 1

    total_hits = 0
    for path in files:
        for line_no, phrase, line_text in scan_file(path):
            total_hits += 1
            print(f"  FAIL  {path}:{line_no}  {phrase!r}\n        {line_text}")

    if total_hits:
        print(
            f"\n{total_hits} banned phrase occurrence(s) in {len(files)} "
            f"file(s) scanned. The Millipore EZ-Fit is the reference "
            f"instrument this device is validated against, not a product "
            f"it replaces — reword to describe an alternative route to the "
            f"same measurement."
        )
        return 1

    print(f"verify_copy: {len(files)} file(s) scanned, 0 banned phrases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
