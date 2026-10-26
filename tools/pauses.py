#!/usr/bin/env python3
"""List speech pauses in a window (finer than cut_inspect.py).
Usage:  python3 tools/pauses.py <slug> <start_s> <end_s> [min_pause_s=0.15]
Use it to check the exact tail right where you plan to end a reel."""
import os, re, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); thr = float(sys.argv[4]) if len(sys.argv) > 4 else 0.15
o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", str(a), "-t", str(b - a), "-i", f"{ROOT}/sources/{src}/source.mp4",
                    "-af", f"silencedetect=noise=-30dB:d={thr}", "-f", "null", "-"], capture_output=True, text=True).stderr
ss = [float(x) + a for x in re.findall(r"silence_start: ([\d.-]+)", o)]
se = [float(x) + a for x in re.findall(r"silence_end: ([\d.]+)", o)]
print("  ".join(f"{s:.2f}-{e:.2f}" for s, e in zip(ss, se)))
