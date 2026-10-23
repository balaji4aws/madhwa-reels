#!/usr/bin/env python3
"""Automated post-build checks for a venkatachala-ep06 reel.

Same checks as venkatachala-ep01/check_reel.py (that's the canonical
pattern -- this is a per-slug copy, not a reimplementation of its shared
logic):
  1. SPECS   — 1080x1920, duration (warn if > 60s for a Short).
  2. SPELL   — every subtitle word is in the system dictionary OR the
               known-names allowlist; otherwise flagged for review.
  3. CUTS    — caption-boundary based odd-cut check (NOT loudness -- these
               sources carry a constant background drone that defeats any
               volume threshold as a final verifier).

Usage:
  python3 check_reel.py <reel.mp4> --subs-json <subs.json> \\
      --vtt <source.en.vtt> --src-start <s> --src-end <e>
Exit code 0 = all pass, 1 = at least one FAIL (warnings don't fail).
"""
import argparse
import json
import os
import re
import subprocess
import sys

# clip_cutter.py and sanskrit_terms.py live in the shared tools/ folder,
# two levels up from this per-slug script -- imported, not reimplemented.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from clip_cutter import load_cues, inside_cue  # noqa: E402
from sanskrit_terms import correct_variants, all_correct_lower  # noqa: E402

DICT_PATH = "/usr/share/dict/words"

# Shared reference list (tools/sanskrit_terms.py) plus terms specific to
# THIS slug's source material that aren't general/recurring enough yet for
# the shared list -- same split venkatachala-ep01/check_reel.py already
# uses. Add new recurring Madhwa/channel proper nouns to the shared file
# instead of here.
ALLOWLIST = all_correct_lower() | {
    # general devotional / already-used-elsewhere terms
    "venkata", "tirupati", "yuga", "yugas",
    "srinivasa", "madhwa", "dvaita", "uttaradi", "math", "purana",
    "madhwa16", "shri",
    # this slug's own story material (Padmavati/Srinivasa narrative)
    "dharani", "aditya", "sudarshana", "chakra", "venkateshwara",
    # the quoted Sanskrit verse (transcribed as heard, not a channel proper
    # noun to standardize -- see build_reel01.py's subs comment)
    "nachamatrasamam", "mitram", "putrinam", "nandini", "asthi",
}

KNOWN_WRONG = correct_variants()

EXTRA_OK = {"its", "it's", "lord's", "wasn't", "don't", "doesn't",
            "god", "yugas",
            # real English words missing from web2's morphology coverage
            # (web2 has "dispel" but not the doubled-consonant gerund
            # "dispelling" -- not a typo, see docs/CHANGELOG.md's
            # "Brahminhood"/"committed" precedent on venkatachala-ep01).
            "dispelling",
            # same category, found while building reels 05/06: "couldn't"
            # (contraction, web2 lacks the apostrophe form), "replied" and
            # "proud" (plain English words not in web2) -- not typos.
            "couldn't", "replied", "proud"}


def ffprobe_dims(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True).stdout.split()
    w, h, dur = int(out[0]), int(out[1]), float(out[2])
    return w, h, dur


def load_dict():
    words = set()
    if os.path.exists(DICT_PATH):
        with open(DICT_PATH, errors="ignore") as f:
            for ln in f:
                words.add(ln.strip().lower())
    return words


def _known(w, vocab):
    if w in vocab:
        return True
    if w.endswith("'s") and w[:-2] in vocab:
        return True
    if w.endswith("s") and w[:-1] in vocab:
        return True
    if w.endswith("es") and w[:-2] in vocab:
        return True
    if w.endswith("ies") and (w[:-3] + "y") in vocab:
        return True
    for suf, repl in (("ed", ""), ("ed", "e"), ("ing", ""), ("ing", "e"),
                      ("d", ""), ("ly", ""), ("er", ""), ("est", "")):
        if w.endswith(suf):
            base = w[:-len(suf)] + repl
            if base in vocab:
                return True
    return False


def spell_check(subs, dictionary):
    vocab = dictionary | ALLOWLIST | EXTRA_OK
    bad = []
    wrong_hits = []
    for s in subs:
        for raw in re.findall(r"[A-Za-z']+", s):
            w = raw.lower().strip("'")
            if not w:
                continue
            if w in KNOWN_WRONG:
                wrong_hits.append((raw, KNOWN_WRONG[w]))
                continue
            if not _known(w, vocab):
                bad.append(raw)
    return bad, wrong_hits


def boundary_cut_check(path, dur, src_start=None, src_end=None, vtt=None):
    """Caption-boundary odd-cut check -- loudness is unreliable on these
    sources (constant background drone). See clip_cutter.py / STYLE.md."""
    if not (vtt and src_start is not None and src_end is not None
            and os.path.exists(vtt)):
        return ("start: cut not verified (no caption timing supplied)",
                "end: cut not verified (no caption timing supplied)",
                None, None)

    cues = load_cues(vtt)
    s_mid = inside_cue(src_start, cues)
    e_mid = inside_cue(src_end, cues)
    sm = ("start: lands at a caption boundary — clean"
          if not s_mid else "start: INSIDE a caption cue — may cut a word")
    em = ("end: lands at a caption boundary — clean"
          if not e_mid else "end: INSIDE a caption cue — may cut a word")
    return sm, em, (not s_mid), (not e_mid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--subs-json", required=True)
    ap.add_argument("--vtt", help="source .en.vtt for caption-boundary cut check")
    ap.add_argument("--src-start", type=float, help="clip start in source seconds")
    ap.add_argument("--src-end", type=float, help="clip end in source seconds")
    args = ap.parse_args()

    with open(args.subs_json) as f:
        subs = json.load(f)

    name = os.path.basename(args.video)
    print(f"\n=== CHECK: {name} ===")
    failed = False

    w, h, dur = ffprobe_dims(args.video)
    ok_dims = (w == 1080 and h == 1920)
    print(f"[{'PASS' if ok_dims else 'FAIL'}] dimensions {w}x{h} (want 1080x1920)")
    failed |= not ok_dims
    short_ok = dur <= 60.5
    print(f"[{'PASS' if short_ok else 'WARN'}] duration {dur:.1f}s "
          f"({'ok for Short' if short_ok else '>60s, not a Short'})")

    dictionary = load_dict()
    bad, wrong_hits = spell_check(subs, dictionary)
    if wrong_hits:
        for wrong, correct in sorted(set(wrong_hits)):
            print(f"[FAIL] known wrong transliteration: {wrong!r} "
                  f"should be {correct!r} (see tools/sanskrit_terms.py)")
        failed = True
    if bad:
        print(f"[WARN] possible spelling issues (review): {sorted(set(bad))}")
    if not bad and not wrong_hits:
        print("[PASS] spelling: all subtitle words recognised")

    sm, em, s_ok, e_ok = boundary_cut_check(
        args.video, dur, args.src_start, args.src_end, args.vtt)
    for msg, ok in ((sm, s_ok), (em, e_ok)):
        tag = "PASS" if ok else ("WARN" if ok is False else "INFO")
        print(f"[{tag}] {msg}")

    print("=== RESULT:", "FAIL" if failed else "OK (review any WARN)", "===")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
