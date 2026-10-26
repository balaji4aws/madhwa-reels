#!/usr/bin/env python3
"""Make one side-by-side image of frames from reels, for a quick visual check.
Usage:  python3 tools/frame_sheet.py out.png reel1.mp4@12 reel2.mp4@30 ...
(file@seconds). Then look at out.png: title, subtitle, watermark, face centred."""
import subprocess, sys, tempfile, os
out = sys.argv[1]; ims = []; tmp = tempfile.mkdtemp()
for i, s in enumerate(sys.argv[2:]):
    f, t = s.rsplit("@", 1); p = os.path.join(tmp, f"s{i}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", f, "-frames:v", "1", p], check=True); ims.append(p)
cmd = ["ffmpeg", "-v", "error", "-y"]
for p in ims: cmd += ["-i", p]
if len(ims) == 1:
    cmd += ["-vf", "scale=720:-1", out]
else:
    cmd += ["-filter_complex", f"hstack=inputs={len(ims)},scale=1440:-1", out]
subprocess.run(cmd, check=True)
