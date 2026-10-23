#!/usr/bin/env python3
"""Rebuild reels 02-05 for venkatachala-ep01, SHORTER (15-30s Gen-Z target).

These replace the old 02-05 builds (which ran 44-59s). Each clip below is a
NEW tighter cut (clipNN_..._v2.mp4) chosen by reading source.en.vtt and
cross-checking with tools/clip_cutter.py + direct ffmpeg silencedetect -- see
docs/CHANGELOG.md's 2026-10-23 entry for the full boundary reasoning per
reel.
Subtitle text/timing is written fresh for each new shorter clip, not reused
from the old longer subtitle sets.

Each reel: id, clip file, (title_lead, title_main),
subs = list of (text, start, end) in clip-seconds.
"""
import os
import subprocess
from overlays_lib import render_title, render_sub, crop_reframe_filter

WM = "../../assets/watermark.png"
OUT = "../../reels"

REELS = [
    {
        # Source 295.44-328.00s (32.56s). Starts clean at the word "we" in
        # "we should cut off our heads like Vrishabhasura" (prior sentence
        # ends right before); ends right after "...service of God." finishes,
        # before the next sentence "We should see the idols..." begins.
        "name": "venkatachala-ep01_02_offer-your-senses",
        "clip": "clip02_senses_v2.mp4",
        "title": ("Offer your head to God?", "What it really means"),
        "subs": [
            ("\u201cWe should cut off our heads", 0.2, 2.8),
            ("like Vrishabhasura\u201d \u2014 not literally.", 2.8, 6.5),
            ("The message from this Purana:", 23.5, 25.2),
            ("cutting off the head to God", 25.2, 28.0),
            ("means dedicating all our senses", 28.0, 30.0),
            ("to His service.", 30.0, 32.5),
        ],
    },
    {
        # Source 776.27-805.84s (29.57s). Starts clean at "Lord" in "Lord
        # Hanuman incarnated there" (word-level VTT boundary); ends right
        # after "...after her name." finishes, before "Therefore," (next
        # sentence) begins.
        "name": "venkatachala-ep01_03_why-anjanachala",
        "clip": "clip03_anjana_v2.mp4",
        "title": ("Why is it called", "Anjanachala?"),
        "subs": [
            ("Lord Hanuman incarnated here \u2014", 0.2, 3.3),
            ("that's why it's specially called", 3.3, 6.8),
            ("Anjanachala.", 6.8, 8.0),
            ("By devotion to Hanuman here,", 8.5, 11.5),
            ("his mother Anjana Devi's name", 20.5, 23.5),
            ("made this mountain famous forever.", 23.5, 29.5),
        ],
    },
    {
        # Source 1101.44-1128.26s (26.82s). Start is the VTT's own displayed
        # cue start for "message is that a person should not be arrogant..."
        # (flagged review-manually by clip_cutter because the snap lands on
        # the TAIL pause of this same whole-phrase cue, not a wrong-sentence
        # snap -- see CHANGELOG.md). End confirmed clean: "...through this
        # story." finishes right before the next (reel06) story begins.
        "name": "venkatachala-ep01_04_shesha-no-arrogance",
        "clip": "clip04_shesha_v2.mp4",
        "title": ("Seshachala's lesson:", "Never be arrogant"),
        "subs": [
            ("The message: never be arrogant", 0.2, 3.5),
            ("about your strength, knowledge,", 3.5, 5.8),
            ("or any other virtue.", 5.8, 7.2),
            ("'Shesha' means a remnant \u2014", 11.5, 14.5),
            ("we are all His servants,", 14.5, 18.5),
            ("He alone is supreme.", 18.5, 21.5),
            ("This is the lesson of Seshachala.", 21.5, 26.8),
        ],
    },
    {
        # Source 1227.20-1250.03s (22.83s). Start is the word-level VTT
        # boundary for "making the pilgrimage, we should touch..."; end
        # confirmed clean by clip_cutter (snapped to a real pause right
        # after "...Venkatachala." and before "We should make such a
        # special approach..." begins).
        "name": "venkatachala-ep01_05_venkata-burns-sins",
        "clip": "clip05_venkata_v2.mp4",
        "title": ("Why Venkatachala", "burns away sins"),
        "subs": [
            ("While on pilgrimage,", 0.2, 1.5),
            ("touch the mountain with devotion \u2014", 1.5, 4.5),
            ("Shesha, Vayu, Mahalakshmi", 4.5, 8.0),
            ("dwell in every particle.", 8.0, 10.5),
            ("Performing the yatra with devotion", 14.5, 17.5),
            ("will cure all sins.", 17.5, 20.0),
            ("That's why it's called Venkatachala.", 20.0, 22.83),
        ],
    },
]


def clip_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def build(reel):
    outdir = "."
    tp = render_title(outdir, reel["title"][0], reel["title"][1])

    dur = clip_duration(reel["clip"])
    last_end = max(e for _, _, e in reel["subs"])
    scale = (dur - 0.3) / last_end if last_end > dur - 0.3 else 1.0

    sub_paths = []
    for i, (txt, s, e) in enumerate(reel["subs"], 1):
        s2, e2 = round(s * scale, 2), round(e * scale, 2)
        sub_paths.append((render_sub(outdir, i, txt), s2, e2))

    inputs = ["-i", reel["clip"], "-i", tp]
    for p, _, _ in sub_paths:
        inputs += ["-i", p]
    inputs += ["-i", WM]

    fc = (
        crop_reframe_filter() +
        "[reframed][1:v]overlay=0:0[v0];"
    )
    prev = "v0"
    for i, (_, s, e) in enumerate(sub_paths):
        inp = i + 2
        out = f"vs{i}"
        fc += f"[{prev}][{inp}:v]overlay=0:0:enable='between(t,{s},{e})'[{out}];"
        prev = out
    wm_idx = 2 + len(sub_paths)
    fc += f"[{prev}][{wm_idx}:v]overlay=0:0[vout]"

    outpath = os.path.join(OUT, reel["name"] + ".mp4")

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", "[vout]",
        "-map", "0:a",
    ]
    cmd += [
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", "30", "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", outpath,
    ]
    print("Building", reel["name"], "...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", reel["name"])
        print(r.stderr[-2000:])
        return False
    print("  ->", outpath)
    return True


if __name__ == "__main__":
    ok = all(build(r) for r in REELS)
    print("ALL OK" if ok else "SOME FAILED")
