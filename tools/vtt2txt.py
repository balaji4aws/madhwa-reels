#!/usr/bin/env python3
"""Turn a YouTube .vtt caption file into plain text chunks with start seconds.
Use it to READ a whole talk quickly when picking moments.
Usage:  python3 tools/vtt2txt.py sources/<slug>/source.en.vtt [chunk_seconds=20]
Prints lines like  [1361] text ...  (the number is the chunk's start second).
Read source.en.vtt (English, 30s chunks) to find topics; read source.kn.vtt
(Kannada, 20s chunks) to place the actual cuts."""
import re, sys
txt = open(sys.argv[1], encoding="utf-8").read()
cues = []
for b in txt.split("\n\n"):
    m = re.search(r"(\d\d):(\d\d):(\d\d)\.(\d+)\s*-->\s*(\d\d):(\d\d):(\d\d)\.(\d+)", b)
    if not m:
        continue
    s = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000
    e = int(m[5]) * 3600 + int(m[6]) * 60 + int(m[7]) + int(m[8]) / 1000
    lines = [re.sub(r"<[^>]+>", "", l).strip() for l in b.split("\n")[1:]]
    lines = [l for l in lines if l and "-->" not in l]
    if not lines or e - s < 0.05:
        continue
    cues.append((s, lines[-1]))
ded, prev = [], None
for s, t in cues:
    if t != prev:
        ded.append((s, t))
    prev = t
chunk_len = float(sys.argv[2]) if len(sys.argv) > 2 else 20
out, cur, cs = [], [], None
for s, t in ded:
    if cs is None:
        cs = s
    if s - cs >= chunk_len and cur:
        out.append(f"[{cs:.0f}] " + " ".join(cur)); cur, cs = [], s
    cur.append(t)
if cur:
    out.append(f"[{cs:.0f}] " + " ".join(cur))
print("\n".join(out))
