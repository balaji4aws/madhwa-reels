#!/usr/bin/env python3
"""Per-source reel numbering helper.

Reels live at reels/<slug>/<slug>_NN_<topic>.mp4 (one subfolder per source
video, NOT a flat dump into reels/). This module answers: "what's the next
free NN for this slug?" by scanning what's already there, so numbering
auto-increments correctly even across separate sessions/runs and never
collides or restarts at 01 when more reels are added to an existing source
later.

Usage:
    from reel_numbering import next_reel_number, reel_dir

    n = next_reel_number("venkatachala-ep07")   # -> e.g. 5, if 01-04 exist
    out_dir = reel_dir("venkatachala-ep07")      # -> reels/venkatachala-ep07/
"""
import os
import re

REELS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reels")

_NUM_RE = re.compile(r"^(?P<slug>.+)_(?P<num>\d{2,})_.*\.mp4$")


def reel_dir(slug):
    """Return the (created-if-missing) per-source reels folder for slug."""
    path = os.path.join(REELS_ROOT, slug)
    os.makedirs(path, exist_ok=True)
    return path


def existing_reel_numbers(slug):
    """Return a sorted list of reel numbers (ints) already present for slug,
    by scanning reels/<slug>/ for files matching <slug>_NN_<topic>.mp4."""
    d = reel_dir(slug)
    nums = []
    for fname in os.listdir(d):
        if not fname.endswith(".mp4"):
            continue
        m = _NUM_RE.match(fname)
        if m and m.group("slug") == slug:
            nums.append(int(m.group("num")))
    return sorted(nums)


def next_reel_number(slug):
    """Return the next free reel number for slug (max existing + 1, or 1
    if none exist yet). NEVER hardcode a starting number in a build script
    -- always call this so numbering is correct even if reels were added
    in a separate session."""
    existing = existing_reel_numbers(slug)
    return (existing[-1] + 1) if existing else 1


def format_reel_number(n):
    """Zero-padded to 2 digits, matching the existing <slug>_01_... style.
    (If a source ever needs reel 100+, this naturally widens to 3 digits --
    the _NUM_RE regex above already accepts 2+ digit numbers.)"""
    return f"{n:02d}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 reel_numbering.py <slug>")
        sys.exit(1)
    slug = sys.argv[1]
    existing = existing_reel_numbers(slug)
    nxt = next_reel_number(slug)
    print(f"Slug: {slug}")
    print(f"Existing reel numbers: {existing}")
    print(f"Next free number: {nxt} (-> {format_reel_number(nxt)})")
