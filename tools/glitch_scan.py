#!/usr/bin/env python3
"""Scan a whole video for non-content frames: editor placeholders like
"Missing File"/"Media Offline", black or solid-colour flashes, frozen title
cards. Added 2026-10-23 after the source of venkatachala-ep06 reel 10 turned
out to contain a 1.6s "Missing File" card that our spot-check frames missed.

How it works: sample frames at --fps, measure per-frame luma average,
saturation average and frame-to-frame difference (ffmpeg signalstats), and
flag any run >= --min-dur seconds where the picture is (a) frozen -- almost no
change frame to frame, which never happens with a live speaker on camera, or
(b) far from the video's typical colour/brightness. Prints the flagged
ranges in source seconds. Exit code 1 if anything is flagged.

    python3 tools/glitch_scan.py <video> [--start S --end E] [--fps 5]
"""
import argparse, re, statistics, subprocess, sys

def stats(path, start, end, fps):
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-nostats"]
    if start: cmd += ["-ss", str(start)]
    cmd += ["-i", path]
    if end: cmd += ["-t", str(end - (start or 0))]
    cmd += ["-vf", f"fps={fps},scale=96:54,signalstats,metadata=print:file=-", "-an", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    rows, cur = [], {}
    for line in out.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            if cur: rows.append(cur)
            cur = {"t": float(m[1]) + (start or 0)}
        for k in ("YAVG", "SATAVG", "YDIF"):
            m = re.search(rf"lavfi\.signalstats\.{k}=([\d.]+)", line)
            if m: cur[k] = float(m[1])
    if cur: rows.append(cur)
    return [r for r in rows if {"YAVG", "SATAVG", "YDIF"} <= r.keys()]

def scan(path, start=None, end=None, fps=5, min_dur=0.4):
    rows = stats(path, start, end, fps)
    if not rows: return [], 0
    my, ms = statistics.median(r["YAVG"] for r in rows), statistics.median(r["SATAVG"] for r in rows)
    sy = statistics.pstdev(r["YAVG"] for r in rows) or 1
    ss = statistics.pstdev(r["SATAVG"] for r in rows) or 1
    # A "card" is a FROZEN frame that also looks unlike the speaker shot
    # (editor placeholder, solid colour, title card): flag from min_dur.
    # A frozen frame that still looks like the speaker is usually just him
    # sitting still or a jump cut -- only flag it if it lasts >= 1.5s.
    def kind(r):
        frozen = r["YDIF"] < 0.15
        off = abs(r["YAVG"] - my) > 4 * sy or abs(r["SATAVG"] - ms) > 4 * ss
        if frozen and off: return "card"
        if frozen: return "freeze"
        return None
    ranges, run = [], None
    for r in rows:
        k = kind(r)
        if k:
            if run: run[1] = r["t"]; run[2] = run[2] or (k == "card")
            else: run = [r["t"], r["t"], k == "card"]
        else:
            if run: ranges.append(tuple(run))
            run = None
    if run: ranges.append(tuple(run))
    step = 1 / fps
    ranges = [(a, b) for a, b, card in ranges
              if (b - a + step) >= (min_dur if card else max(min_dur, 1.5))]
    return [(a, b + 1 / fps) for a, b in ranges], len(rows)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--start", type=float); ap.add_argument("--end", type=float)
    ap.add_argument("--fps", type=float, default=5); ap.add_argument("--min-dur", type=float, default=0.4)
    a = ap.parse_args()
    found, n = scan(a.video, a.start, a.end, a.fps, a.min_dur)
    print(f"scanned {n} frames of {a.video}")
    for s, e in found: print(f"  FLAG {s:9.2f}s - {e:9.2f}s  ({e - s:.1f}s)")
    if not found: print("  clean")
    sys.exit(1 if found else 0)
