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


ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def existing_reel_numbers(slug):
    """Return a sorted list of reel numbers (ints) ever used for slug.

    Finished reels are deleted locally after upload (post-upload cleanup), so
    reels/<slug>/ alone is NOT a reliable record -- scanning only that folder
    would restart numbering at 01 and collide with reels already live. So this
    takes the union of three records:
      1. reels/<slug>/<slug>_NN_*.mp4           (built, not yet uploaded)
      2. docs/SOURCES.md rows "| [<slug>](...) | NN · Title |" (every reel)
      3. work/<slug>/ files: build_reelNN.py, clipNN_*.mp4, reels.json "num"
    """
    nums = set()
    d = reel_dir(slug)
    for fname in os.listdir(d):
        m = _NUM_RE.match(fname)
        if fname.endswith(".mp4") and m and m.group("slug") == slug:
            nums.add(int(m.group("num")))
    sources_md = os.path.join(ROOT, "docs", "SOURCES.md")
    if os.path.exists(sources_md):
        row = re.compile(r"^\|\s*\[?" + re.escape(slug) + r"\]?(?:\([^)]*\))?\s*\|\s*(\d{2,})\b")
        with open(sources_md, encoding="utf-8") as f:
            for line in f:
                m = row.match(line)
                if m:
                    nums.add(int(m.group(1)))
    work = os.path.join(ROOT, "work", slug)
    if os.path.isdir(work):
        for fname in os.listdir(work):
            m = re.match(r"^(?:build_reel|clip)(\d{2,})", fname)
            if m:
                nums.add(int(m.group(1)))
        spec = os.path.join(work, "reels.json")
        if os.path.exists(spec):
            import json
            with open(spec, encoding="utf-8") as f:
                for r in json.load(f).get("reels", []):
                    if "num" in r:
                        nums.add(int(r["num"]))
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
