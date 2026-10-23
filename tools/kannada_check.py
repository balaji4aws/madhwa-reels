#!/usr/bin/env python3
"""Kannada subtitle check (added 2026-10-23 with bilingual subtitles).

There is no trustworthy Kannada spell-checker installed (no hunspell, and
public Kannada dictionaries are thin), so this does two things it CAN do
reliably, and says plainly what it can't:

1. ORTHOGRAPHY (hard FAIL) -- every word is well-formed Kannada script:
   - only Kannada letters, spaces, ZWJ/ZWNJ, digits and normal punctuation
     (no stray Latin letters mixed into a Kannada line),
   - no word starting with a dependent sign (vowel sign, virama ್, ಂ, ಃ),
   - no two vowel signs in a row, no double virama, no virama followed by a
     vowel sign.
   These are the errors that render as broken/dotted-circle glyphs on screen.

2. VOCABULARY (WARN, for review) -- every word must appear in the speaker's
   own Kannada captions (sources/<slug>/source.kn.vtt). Words that don't are
   ones we typed or changed while cleaning up the auto-captions; each one is
   listed so a human checks it. YouTube's Kannada auto-captions themselves can
   be wrong, so "found in source" is not proof of correct spelling either --
   the channel owner's read of a sample reel is the final check.

    python3 tools/kannada_check.py <source.kn.vtt> "line one" "line two" ...
"""
import re
import sys
import unicodedata

KN_LO, KN_HI = 0x0C80, 0x0CFF
VOWEL_SIGNS = set(range(0x0CBE, 0x0CC5)) | set(range(0x0CC6, 0x0CC9)) | \
              set(range(0x0CCA, 0x0CCD)) | {0x0CD5, 0x0CD6, 0x0CE2, 0x0CE3}
VIRAMA = 0x0CCD
NUKTA = 0x0CBC
LEADING_BAD = VOWEL_SIGNS | {VIRAMA, NUKTA, 0x0C81, 0x0C82, 0x0C83}
ZW = {0x200C, 0x200D}
PUNCT = set(" ,.?!;:'\"\u2018\u2019\u201c\u201d\u2014\u2013-()…")


def _is_kn(cp):
    return KN_LO <= cp <= KN_HI


def words(text):
    return [w for w in re.split(r"[\s,.?!;:'\"\u2018\u2019\u201c\u201d\u2014\u2013()…-]+", text) if w]


def orthography_errors(text):
    errs = []
    text = unicodedata.normalize("NFC", text)
    for ch in text:
        cp = ord(ch)
        if not (_is_kn(cp) or cp in ZW or ch in PUNCT or ch.isdigit()):
            errs.append(f"non-Kannada character {ch!r} in {text!r}")
    for w in words(text):
        cps = [ord(c) for c in w]
        if cps and cps[0] in LEADING_BAD:
            errs.append(f"word starts with a dependent sign: {w!r}")
        for a, b in zip(cps, cps[1:]):
            if a in VOWEL_SIGNS and b in VOWEL_SIGNS:
                errs.append(f"two vowel signs in a row: {w!r}")
            if a == VIRAMA and (b == VIRAMA or b in VOWEL_SIGNS):
                errs.append(f"virama followed by a sign: {w!r}")
    return errs


def source_vocab(vtt_path):
    txt = open(vtt_path, encoding="utf-8").read()
    txt = re.sub(r"<[^>]+>", " ", txt)
    vocab = set()
    for line in txt.splitlines():
        if "-->" in line or not any(_is_kn(ord(c)) for c in line):
            continue
        vocab.update(unicodedata.normalize("NFC", w) for w in words(line))
    return vocab


def check(lines, vtt_path):
    """Return (errors, review_words). errors -> hard FAIL."""
    vocab = source_vocab(vtt_path)
    errors, review = [], []
    for ln in lines:
        if not ln:
            continue
        errors += orthography_errors(ln)
        for w in words(unicodedata.normalize("NFC", ln)):
            if w not in vocab and w not in review:
                review.append(w)
    return errors, review


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    errs, rev = check(sys.argv[2:], sys.argv[1])
    for e in errs:
        print("[FAIL]", e)
    print("[WARN] not in source captions (review):", rev) if rev else print("[PASS] all words found in source captions")
    sys.exit(1 if errs else 0)
