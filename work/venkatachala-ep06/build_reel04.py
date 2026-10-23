#!/usr/bin/env python3
"""Build Reel (slug: venkatachala-ep06) -- "Don't take credit for God's work"

Source: "Glory of Venkatachala | Ep - 06 | ವೇಂಕಟಾಚಲ ಮಹಿಮೆ | By Sri
Satyatmateertha Shripadangalavaru" (Sri Uttaradi Math Adhyatmavani), full
discourse 2887.4s (~48.1 min) -- NOT trimmed at download time, per house
rule.

Moment: a humility teaching late in the discourse. The Lord tells Bakuladevi
that she did all the work of arranging His marriage; she insists she did
nothing -- "You did the work yourself" -- then admits that when she tried to
act on her own earlier (without His grace), her own effort came to nothing.
Self-contained hook ("who really did this work?") + payoff (true humility:
crediting God, not yourself, for what gets accomplished). This is a NEW
moment, well after reels 03/04 (no-friend-like-mother ~300-345s, chakra-
conch ~616-671s) and after the dharmadevi-name-meaning reel in this same
batch (~111-157s) -- no overlap with any of them.

Cut boundaries -- picked and placed with EXTRA care per the channel owner's
explicit "cuts feel abrupt" feedback on reels 03/04 (see docs/CHANGELOG.md's
2026-10-23 (later) entry for the full writeup of what changed this session):
  start = 2674.8 (source). The original rough window (2662.5-2733.0, the
          full "What is your leela?...God will teach me how to do business"
          arc) ran 69s -- OVER STYLE.md's 60s hard limit -- so the window was
          deliberately tightened to the tightest self-contained hook+payoff
          core rather than cut at an arbitrary mid-sentence point: dropping
          the narrative scaffolding ("Meanwhile Bakula Devi is slowly
          coming... welcomed her...") and starting directly at the hook
          line, "That Dharmadevi is none other than God...". clip_cutter.py
          (cut_report_04.json) flagged this boundary REVIEW-MANUALLY
          (2674.8 -> snapped 2674.829s, "inside_cue" per the coarse VTT
          grouping spanning the prior cue "...I had to do."). Manually
          verified with a direct silencedetect pass: a genuine ~0.81s pause
          sits at 2674.42-2675.22s (between "...I had to do." ending 2675.11
          and "That Dharmadevi..." beginning 2675.383 per its own karaoke
          word-tag), confirming this is a real inter-sentence pause, not a
          mid-clause snap. Chosen start (2674.8s) sits inside that pause,
          0.58s before the first word -- an audible breath before the hook
          line starts.
  end   = 2730.0 (source). clip_cutter.py flagged REVIEW-MANUALLY (2730.0 ->
          snapped 2729.367s, "inside_cue" per the coarse grouping of the cue
          spanning "God will teach...they have", 2728.64-2730.95s).
          Manually verified: the payoff sentence's last word ("business.")
          has its own karaoke word-tag at 2729.160s (i.e. already being
          spoken, confirming the sentence is nearly complete there, not that
          2730.95 is needed to finish it), and a direct silencedetect pass
          found a genuine ~0.4s pause at 2729.15-2729.56s right after it --
          then the cue immediately moves on to a new clause ("Mataram
          Pratinandya congratulated her well...", a new story beat, not part
          of this teaching's payoff). Chosen end (2730.0s) sits just past
          that pause, giving the complete payoff line plus a trailing
          breath before the cut, rather than snapping tight to 2729.56s or
          trusting the coarse cue's own claimed end (2730.95s, which runs
          into the next, unrelated clause -- the same cue-display-lag
          pattern already documented for this source).
Clip duration: 55.2s -- over the 20-45s default band and the 15-30s Gen-Z
range, but within STYLE.md's 15-60s acceptable range: the hook ("Dharmadevi
is none other than God") and the payoff (her own admission that her
unaided effort came to nothing) both need to land whole for the humility
lesson to read as complete, the same trade-off already made for reel04
(chakra-conch, 54.8s).

This source is 4K (3840x2160) -- scaled down to 1920x1080 BEFORE calling the
shared crop_reframe_filter() (which assumes a 1920-wide input), so crop_x
stays directly comparable to previous sources' derivations.

Title card uses the per-slug override (title_compact.py), NOT the shared
overlays_lib.render_title() -- see build_reel01.py's docstring for the full
reasoning (this speaker has near-zero headroom above his hairline/tilak
mark). REUSED as-is, not rebuilt -- re-verified visually against this
clip's own probe frames (framing confirmed consistent with reel03/04/the
dharmadevi-name reel, see docs/CHANGELOG.md) before use.

crop_x=573 REUSED from reel03/04 (same speaker/source), NOT re-derived --
re-verified visually against this clip's own probe frames at 10%/50%/90%
before use.

REBUILD (per user feedback that reels 05/06 STILL cut abruptly even with
the silence-margin boundary placement): this version adds a 0.2s video
fade-to/from-black + matching audio afade. IMPORTANT, learned the hard way
during this session's reel05 rebuild (see work/build-notes.md): the fade
must be applied to the FINAL COMPOSITED frame ([vout], after every
overlay), NOT to the raw background clip before compositing -- a first
attempt faded only the raw clip and fed it into the same overlay chain as
before, and the title card / watermark PNGs (composited at full opacity
for the clip's entire duration, no enable= gating on them) stayed fully
visible while the video underneath dimmed to black, an overlay-desync
artifact caught by directly inspecting extracted start/end frames. Fixed
here by applying `fade` to the tail of the filter_complex (on [vout],
after all overlays) and `afade` on the audio stream the same way, so
title/subtitle/watermark fade together with the background as one unit.
The cut boundaries themselves (2674.8s/2730.0s source, confirmed correct
placement in the prior session) are UNCHANGED -- this rebuild only adds
the fade transition on top of them. See docs/CHANGELOG.md's "abrupt cuts,
part 2" entry and work/build-notes.md for the full reasoning and this
reel's individual perceptual check.

Uses the shared crop_reframe_filter() from venkatachala-ep01's overlays_lib.py
(imported via sys.path) and tools/reel_numbering.py to assign the reel number.
"""
import os
import sys
import subprocess

sys.path.insert(0, os.path.join("..", "..", "tools"))
from overlays_lib import render_sub, crop_reframe_filter  # noqa: E402

sys.path.insert(0, os.path.join("..", "..", "tools"))
from reel_numbering import reel_dir, format_reel_number  # noqa: E402

from title_compact import render_title_compact  # noqa: E402

SLUG = "venkatachala-ep06"
CLIP = "clip04_bakuladevi-humility.mp4"
WM = "../../assets/watermark.png"
TOPIC = "bakuladevi-humility"
# This is a REBUILD/FIX of an already-assigned reel number, not a new reel
# -- do NOT call next_reel_number(SLUG) here. By the time this rebuild
# runs, reels 05/06 already exist on disk, so next_reel_number would
# return 07/08, which is wrong: this script must overwrite the existing
# reel 06 in place (same number, fixed content), per this task's explicit
# instruction. The number is fixed at the value originally assigned.
REEL_NUM = 6
# Cut-transition fade -- applied to the FINAL composited frame, not the
# raw background clip (see docstring above for why). 0.2s, chosen and
# verified in tools/fade_clip.py's module docstring; same duration used
# consistently across all 6 clips in this task.
FADE_DURATION = 0.2

# crop_x=573 derived + verified for THIS source/speaker on reel03/04 (see
# docs/CHANGELOG.md) -- REUSED here (same speaker/source), re-verified
# visually against THIS clip's own probe frames before use, per STYLE.md's
# "verify by rendering against a real frame" rule.
CROP_X = 573

# Subtitles: spell-checked, PARAPHRASED (not a verbatim VTT quote -- see
# STYLE.md's transcript-source honesty rule), clip-relative seconds (clip
# starts at source 2674.8s). "Bakuladevi"/"Dharmadevi" are already-confirmed
# spellings (tools/sanskrit_terms.py); no new or uncertain proper nouns in
# this reel's subtitles.
subs = [
    ("\u201cDharmadevi is none other than God,\u201d", 0.6, 5.6),
    ("he said \u2014 \u201cthe creator of the universe.", 5.7, 7.8),
    ("No one else could have done this but you.\u201d", 7.9, 13.3),
    ("\u201cI did nothing,\u201d Bakuladevi replied.", 18.8, 22.1),
    ("\u201cYou did the work yourself.\u201d", 22.2, 30.5),
    ("Yet she smiled, a little proud:", 34.0, 38.0),
    ("\u201cI worked so hard on my own.", 38.1, 44.2),
    ("But when you left, it was all in vain.", 44.3, 48.4),
    ("I couldn't do it without you.\u201d", 48.5, 53.8),
    ("God alone teaches us how it's truly done.", 53.9, 55.2),
]


def clip_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration", "-of",
                          "default=noprint_wrappers=1:nokey=1", path],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def build():
    outdir = "."
    # Compact per-slug title (see title_compact.py) -- the shared
    # overlays_lib.render_title() band collides with this speaker's
    # forehead/tilak mark on this source; not a shared-code change.
    tp = render_title_compact(outdir, "Don't Take Credit for", "God's Own Work")

    dur = clip_duration(CLIP)
    sub_paths = [(render_sub(outdir, i, t), s, e) for i, (t, s, e) in enumerate(subs, 1)]

    num_str = format_reel_number(REEL_NUM)
    out_dir = reel_dir(SLUG)
    # Build to a STAGING filename, not the final name directly -- the old
    # (abrupt) reel 06 is still at the final name and must stay intact
    # until this rebuilt version is verified. The caller/CLI entrypoint
    # below renames staging -> final only after a successful build; the
    # explicit delete-then-replace of the old file happens as a separate,
    # later step (see work/build-notes.md), never implicitly here.
    out_name = f"{SLUG}_{num_str}_{TOPIC}.NEW.mp4"
    out_path = os.path.join(out_dir, out_name)

    inputs = ["-i", CLIP, "-i", tp]
    for p, _, _ in sub_paths:
        inputs += ["-i", p]
    inputs += ["-i", WM]

    fc = (
        "[0:v]scale=1920:1080[scaled];" +
        crop_reframe_filter(src_label="scaled", crop_x=CROP_X) +
        "[reframed][1:v]overlay=0:0[v0];"
    )
    prev = "v0"
    for i, (_, s, e) in enumerate(sub_paths):
        inp = i + 2
        out = f"vs{i}"
        fc += f"[{prev}][{inp}:v]overlay=0:0:enable='between(t,{s},{e})'[{out}];"
        prev = out
    wm_idx = 2 + len(sub_paths)
    fc += f"[{prev}][{wm_idx}:v]overlay=0:0[vcomposited];"
    # Cut-transition fade applied to the FULLY COMPOSITED frame (title +
    # subtitles + watermark already baked in) so every element fades
    # together as one unit -- see this file's module docstring for the
    # overlay-desync bug this fixes. Audio faded the same way via -af,
    # matching start/end exactly against the video fade.
    fade_out_start = round(dur - FADE_DURATION, 3)
    fc += (
        f"[vcomposited]fade=t=in:st=0:d={FADE_DURATION},"
        f"fade=t=out:st={fade_out_start}:d={FADE_DURATION}[vout]"
    )

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc, "-map", "[vout]", "-map", "0:a",
        "-af", f"afade=t=in:st=0:d={FADE_DURATION},"
               f"afade=t=out:st={fade_out_start}:d={FADE_DURATION}",
        "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-r", "30", "-b:v", "6M", "-maxrate", "8M", "-bufsize", "12M",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", out_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED\n", r.stderr[-2000:])
        return False, None
    print("Built", out_path, f"({dur:.1f}s source clip)")
    return True, out_path


if __name__ == "__main__":
    build()
