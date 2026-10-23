#!/usr/bin/env python3
"""Automated post-build checks for a Madhwa reel.

Checks, per reel:
  1. SPECS   — 1080x1920, duration (warn if > 60s for a Short).
  2. SPELL   — every subtitle word is in the system dictionary OR the
               known-names allowlist; otherwise flagged for review.
  3. CUTS    — audio loudness in the first/last ~0.4s; if speech is loud at a
               boundary (not a quiet pause) it likely cuts a word -> flag.

Usage:
  python3 check_reel.py <reel.mp4> --subs-json <subs.json>
where subs.json is a JSON list of the subtitle strings used in that reel.
Exit code 0 = all pass, 1 = at least one FAIL (warnings don't fail).
"""
import argparse
import json
import os
import re
import subprocess
import sys

# clip_cutter.py and sanskrit_terms.py live in the shared tools/ folder
# (sibling of sources/, work/, reels/, etc.), two levels up from this
# per-slug script.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from clip_cutter import load_cues, inside_cue  # noqa: E402
from sanskrit_terms import correct_variants, all_correct_lower  # noqa: E402

DICT_PATH = "/usr/share/dict/words"

# Known-correct Sanskrit / Madhwa / proper nouns used across these reels.
# The authoritative, growing reference list now lives in
# tools/sanskrit_terms.py (shared across all source videos, not per-slug) --
# add new terms THERE, not here. This set adds a few terms specific to this
# slug's source material that aren't general enough for the shared list yet.
ALLOWLIST = all_correct_lower() | {
    "venkata", "tirupati", "balaji",
    "anjaneya",
    "yuga", "yugas", "krita", "treta", "dwapara", "kali",
    "hanuman", "vayu",
    "narasimha", "srinivasa",
    "mahalakshmi", "lakshmi", "madhwa", "dvaita", "uttaradi", "math",
    "bhakti", "vairagya", "sanatana", "dharma", "pravachana", "shraddha",
    "sudarshana", "chakra",
    "kapila", "tirtha", "sattvik", "matanga", "kesari",
    "aitareya", "upanishad", "bhagavatam", "srimad", "purana",
    "madhwa16",
    "yatra", "shri", "madhava",
}

# Known WRONG transliterations -> correct spelling. If a subtitle contains
# one of these, it's not just "not a dictionary word" -- it's a KNOWN,
# nameable error that should be actively flagged, not silently allowed.
KNOWN_WRONG = correct_variants()

# words we treat as fine regardless of dictionary (contractions, common)
EXTRA_OK = {"its", "it's", "lord's", "hanuman's", "god", "yugas",
            "commit", "commits", "committed", "committing"}


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
    """True if w (or a reasonable base form of it) is in vocab.
    web2 lacks many plurals/verb forms, so try common morphology."""
    if w in vocab:
        return True
    # possessive
    if w.endswith("'s") and w[:-2] in vocab:
        return True
    # plural / 3rd person: cats->cat, buses->bus, flies->fly
    if w.endswith("s") and w[:-1] in vocab:
        return True
    if w.endswith("es") and w[:-2] in vocab:
        return True
    if w.endswith("ies") and (w[:-3] + "y") in vocab:
        return True
    # past / -ing: offered->offer, called->call, humbled->humble
    for suf, repl in (("ed", ""), ("ed", "e"), ("ing", ""), ("ing", "e"),
                      ("d", ""), ("ly", ""), ("er", ""), ("est", "")):
        if w.endswith(suf):
            base = w[:-len(suf)] + repl
            if base in vocab:
                return True
    return False


def spell_check(subs, dictionary):
    """Returns (unknown_words, known_wrong_hits).

    unknown_words: words not in the dictionary/allowlist -- might be a typo,
        might just be a term missing from the allowlist. Needs a human look.
    known_wrong_hits: [(wrong, correct)] -- words that MATCH A KNOWN WRONG
        TRANSLITERATION from tools/sanskrit_terms.py. This is a stronger
        signal than "unknown": it's a specific, nameable fix, not just
        "unrecognised word."
    """
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
    """Decide whether the clip starts/ends mid-sentence.

    NOTE: a plain loudness threshold does NOT work for these sources — many
    devotional recordings carry a constant background drone (tanpura/shruti),
    so even a real pause reads 'loud'. The reliable signal is the source
    captions: if the clip's source start/end falls INSIDE a caption cue (rather
    than at a cue boundary / gap), speech is mid-flow there => likely odd cut.

    Returns (start_msg, end_msg, start_ok, end_ok). If vtt/src times are not
    provided, returns an explicit 'not checked' so we never claim a false PASS.
    """
    if not (vtt and src_start is not None and src_end is not None
            and os.path.exists(vtt)):
        return ("start: cut not verified (no caption timing supplied)",
                "end: cut not verified (no caption timing supplied)",
                None, None)

    # parse cue intervals (seconds) from the VTT — shared implementation,
    # see tools/clip_cutter.py (load_cues / inside_cue) so this check and the
    # cutting tool can never drift apart on what counts as a cue boundary.
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

    # 1. specs
    w, h, dur = ffprobe_dims(args.video)
    ok_dims = (w == 1080 and h == 1920)
    print(f"[{'PASS' if ok_dims else 'FAIL'}] dimensions {w}x{h} (want 1080x1920)")
    failed |= not ok_dims
    short_ok = dur <= 60.5
    print(f"[{'PASS' if short_ok else 'WARN'}] duration {dur:.1f}s "
          f"({'ok for Short' if short_ok else '>60s, not a Short'})")

    # 2. spelling
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

    # 3. odd-cut detection (caption-boundary based; loudness is unreliable here)
    sm, em, s_ok, e_ok = boundary_cut_check(
        args.video, dur, args.src_start, args.src_end, args.vtt)
    for msg, ok in ((sm, s_ok), (em, e_ok)):
        tag = "PASS" if ok else ("WARN" if ok is False else "INFO")
        print(f"[{tag}] {msg}")

    print("=== RESULT:", "FAIL" if failed else "OK (review any WARN)", "===")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
