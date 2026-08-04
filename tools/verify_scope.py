#!/usr/bin/env python3
"""Release gate: this repository must contain only work the author has the
right to redistribute.

Two things must never be tracked here:

  * UNICEF's 2GLAM drawings, and Ondrej Sraitr's Petamentor2 filament-machine
    files. The author built a Petamentor2 from Sraitr's published design; he
    did not design it, so he cannot relicense it into this repository.
  * Grading material, raw video, planning documents, and proprietary CAD
    formats (.f3d/.f3z Fusion 360 archives, .pptx/.xlsx office files) that
    have no place in a hardware release.

Redistributing third-party design files here would also block the project's
pending OSHWA certification, which requires the applicant to hold rights to
everything certified.

This check only looks at paths Git actually tracks (`git ls-files`), so
work-in-progress files sitting in an ignored directory such as `incoming/`
never trip it — but anything `git add -f`'d against .gitignore will.

Usage:  python3 tools/verify_scope.py
   or:  python3 -m tools.verify_scope
"""
import fnmatch
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Case-insensitive substrings: a hit anywhere in the path is disqualifying.
# These name the two third-party design projects that must never appear here.
BANNED_SUBSTRINGS = [
    "petamentor2",
    "2glam",
]

# Path-component / prefix rules, checked case-insensitively against the
# posix-normalised path. A rule matches if the tracked path is that
# component, starts with "<rule>/", or contains "/<rule>/".
BANNED_PATH_PREFIXES = [
    "grading",
    "docs/superpowers",
    # The top-level SDD planning directory for this very release project.
    # It documents how the repo was built, not the hardware itself, and
    # must not ship alongside it.
    ".superpowers",
]

# Case-insensitive filename extensions that are categorically out of scope:
# proprietary CAD archives, office documents, and raw video/photo formats
# that belong in an editing pipeline, not a hardware release.
BANNED_EXTENSIONS = [
    ".f3d",
    ".f3z",
    ".pptx",
    ".xlsx",
    ".mov",
    ".mp4",
    ".heic",
]

# A single, previously reviewed exception to the extension ban above.
#
# The rule against .mov/.mp4/.heic exists to keep *raw*, unprocessed
# camera/phone dumps out of the tree (see incoming/videos/, which is
# git-ignored and never reaches this check). It is not a ban on video as a
# medium: the human partner explicitly requested this specific timelapse be
# hosted in-repo (progress.md, "Out-of-band changes (human partner,
# 2026-07-31)"), it is a size-reduced, purpose-encoded deliverable — not raw
# footage — documented in site/public/ASSETS.md ("1168x720, H.264, 8.6s,
# 3.0MB", down from the 2.9 MB incoming/videos/base_printing.mp4 raw
# source), and it is deliberately embedded via a plain <video> element in
# site/src/components/Print.astro (commit b60691e). Any *other* tracked
# .mp4/.mov/.heic file — including a second video anywhere else in the
# tree — still fails this gate.
ALLOWED_EXTENSION_EXCEPTIONS = {
    "site/public/video/base-printing-timelapse.mp4",
}


def _matches_path_prefix(posix_path, rule):
    lowered = posix_path.lower()
    rule = rule.lower().rstrip("/")
    return (
        lowered == rule
        or lowered.startswith(rule + "/")
        or ("/" + rule + "/") in lowered
    )


def offending_reason(path):
    """Return a human-readable reason `path` is out of scope, or None."""
    posix_path = path.replace(os.sep, "/")
    lowered = posix_path.lower()

    for needle in BANNED_SUBSTRINGS:
        if needle in lowered:
            return f"contains {needle!r} — third-party design files are out of scope"

    for rule in BANNED_PATH_PREFIXES:
        if _matches_path_prefix(posix_path, rule):
            return f"is under {rule!r} — excluded from the release"

    if posix_path in ALLOWED_EXTENSION_EXCEPTIONS:
        return None

    _, ext = os.path.splitext(posix_path)
    for banned in BANNED_EXTENSIONS:
        if fnmatch.fnmatch(ext.lower(), banned):
            return f"has extension {ext!r} — excluded file type"

    return None


def tracked_files():
    """Return the list of paths Git currently tracks, repo-relative."""
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True,
        check=True,
    ).stdout
    return [p for p in out.decode("utf-8", "surrogateescape").split("\0") if p]


def main(paths=None):
    files = paths if paths is not None else tracked_files()
    offenders = []
    for path in sorted(files):
        reason = offending_reason(path)
        if reason:
            offenders.append((path, reason))

    if not offenders:
        print(f"verify_scope: {len(files)} tracked files, 0 out of scope")
        return 0

    print(f"verify_scope: {len(offenders)} out-of-scope file(s) found:\n")
    for path, reason in offenders:
        print(f"  FAIL  {path}\n        {reason}")
    print(
        f"\n{len(offenders)} offending file(s) must be removed from the "
        f"index (git rm --cached) before this repository can ship."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
