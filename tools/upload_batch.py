#!/usr/bin/env python3
"""Upload finished reels of one source to YouTube, one after another, each
scheduled into the next free 6 AM / 6 PM IST slot. Stops at the first failure
(for example the daily quota). Logs every success to upload/upload_log.tsv
(slug, reel number, video id, goes-live time) - use it to fill docs/SOURCES.md.
Usage:  python3 tools/upload_batch.py <slug> <NN> [NN ...]
Run from anywhere; uses upload/.venv for the YouTube client."""
import glob, os, re, subprocess, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
slug = sys.argv[1]; nums = [int(x) for x in sys.argv[2:]]
for n in nums:
    f = glob.glob(f"{ROOT}/reels/{slug}/{slug}_{n:02d}_*.mp4")[0]
    r = subprocess.run([f"{ROOT}/upload/.venv/bin/python", f"{ROOT}/upload/youtube_upload.py", f, "--schedule-daily"], capture_output=True, text=True)
    out = r.stdout + r.stderr
    m = re.search(r"Video ID: (\S+)", out); w = re.search(r"scheduled for ([\d-]+ [\d:]+)", out)
    if not m:
        print("FAILED", f, out[-600:]); break
    line = f"{slug}\t{n:02d}\t{m.group(1)}\t{w.group(1) if w else ''}"
    print(line); open(f"{ROOT}/upload/upload_log.tsv", "a").write(line + "\n")
