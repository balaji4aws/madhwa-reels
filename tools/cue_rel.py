#!/usr/bin/env python3
"""Kannada (KN) and English (EN) caption lines for a cut, with times RELATIVE to
the clip start. Use the KN times to time your subtitle lines in reels.json.
Usage:  python3 tools/cue_rel.py <slug> <start_s> <end_s>"""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
def cues(lang):
    t = open(f"{ROOT}/sources/{src}/source.{lang}.vtt", encoding="utf-8").read(); out = []; prev = None
    for blk in t.split("\n\n"):
        m = re.search(r"(\d\d):(\d\d):(\d\d)\.(\d+)\s*-->\s*(\d\d):(\d\d):(\d\d)\.(\d+)", blk)
        if not m:
            continue
        s = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000
        e = int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7]) + int(m[8]) / 1000
        if e < a or s > b or e - s < 0.05:
            continue
        ls = [re.sub(r"<[^>]+>", "", l).strip() for l in blk.split("\n")[1:]]
        ls = [l for l in ls if l and "-->" not in l]
        if not ls or ls[-1] == prev:
            continue
        prev = ls[-1]; out.append((s - a, e - a, ls[-1]))
    return out
print("KN:", " | ".join(f"{s:.1f} {t}" for s, e, t in cues("kn")))
print("EN:", " | ".join(f"{s:.1f} {t}" for s, e, t in cues("en")))
