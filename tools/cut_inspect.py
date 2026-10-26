#!/usr/bin/env python3
"""Show the Kannada caption lines AND the real speech pauses for a time window,
so you can choose cut points that sit in a genuine pause.
Usage:  python3 tools/cut_inspect.py <slug> <start_s> <end_s>
Output: each Kannada cue (start-end text), then PAUSES>=0.4 (silencedetect,
-30dB, min 0.2s). Pick a START at the END of a pause and an END inside a pause
(end = pause_start + ~0.5s so there is 0.4-0.7s of quiet after the last word).
Cue times are speech starts but can lag/lead the audio by up to ~1s: the pauses
are the truth, the cues tell you WHICH words sit between pauses."""
import os, re, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
kn = open(f"{ROOT}/sources/{src}/source.kn.vtt", encoding="utf-8").read()
prev = None
for blk in kn.split("\n\n"):
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
    prev = ls[-1]
    print(f"  {s:7.2f}-{e:7.2f} {ls[-1]}")
out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(a), "-t", str(b - a), "-i", f"{ROOT}/sources/{src}/source.mp4",
                      "-af", "silencedetect=noise=-30dB:d=0.2", "-f", "null", "-"], capture_output=True, text=True).stderr
ss = [float(x) + a for x in re.findall(r"silence_start: ([\d.]+)", out)]
se = [float(x) + a for x in re.findall(r"silence_end: ([\d.]+)", out)]
print("  PAUSES>=0.4:", "  ".join(f"{s:.2f}-{e:.2f}" for s, e in zip(ss, se) if e - s >= 0.4))
