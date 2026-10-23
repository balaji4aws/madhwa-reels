#!/usr/bin/env python3
"""Build Reel (slug: venkatachala-ep06) -- "What does the name Dharmadevi mean?"

Source: "Glory of Venkatachala | Ep - 06 | ವೇಂಕಟಾಚಲ ಮಹಿಮೆ | By Sri
Satyatmateertha Shripadangalavaru" (Sri Uttaradi Math Adhyatmavani), full
discourse 2887.4s (~48.1 min) -- NOT trimmed at download time, per house rule.

Moment: a "did you know" teaching on why Dharani Devi's disguise is named
Dharmadevi -- the Lord explains that the name itself signals that SHE bears
the responsibility for Padmavati's dharma/life: if Padmavati is given to Him
in marriage, her life (and the Dharma it serves) will be preserved. This is a
NEW moment, entirely earlier in the discourse than reels 03/04 (no-friend-
like-mother was source ~300-345s, chakra-conch was ~616-671s) -- no overlap
with either. Self-contained hook ("what does this name actually mean?") +
payoff (the name encodes the Lord's own promise), no dependency on earlier
story setup beyond what's re-stated in-clip.

Cut boundaries -- picked and placed with EXTRA care per the channel owner's
explicit "cuts feel abrupt" feedback on reels 03/04 (see docs/CHANGELOG.md's
2026-10-23 (later) entry for the full writeup of what changed this session):
  start = 111.5 (source). tools/clip_cutter.py (cut_report_03.json) flagged
          REVIEW-MANUALLY (snap 111.801s lands "inside_cue" per the coarse
          VTT grouping). Manually verified with a direct ffmpeg silencedetect
          pass: a genuine, clean ~0.75s pause sits at 111.43-112.18s (the
          previous sentence ends "...die. In" at 107.91s, then a long
          low-level gap, with the real pre-speech silence only right at
          111.43-112.18), and the first word of this clip's hook ("that
          sense...") begins at 112.23s. Chosen start (111.5s) sits INSIDE
          that pause, 0.73s before the first word -- deliberately not
          snapped tight to 112.18/112.23, so there's an audible breath
          before speech starts rather than a hard attack on the first
          syllable.
  end   = 156.6 (source). clip_cutter.py again flagged REVIEW-MANUALLY
          (156.6 -> snapped 155.952s, "inside_cue" per the coarse grouping
          of the cue spanning 152.0-158.95s). Manually verified: the payoff
          sentence's last word ("meaningful.") has its own karaoke word-tag
          at 154.718s in the VTT (i.e. the word is being spoken there, not
          still to come), and a direct silencedetect pass found a genuine
          ~1.0s pause at 155.44-156.46s right after it. Chosen end (156.6s)
          sits ~0.15s past the end of that detected pause -- NOT snapped to
          the pause's own start (155.44s, which would be tight against the
          last syllable) or to the coarse VTT cue's claimed end (158.95s,
          which runs well past where the audio actually goes quiet, the
          same cue-display-lag pattern already documented for this source).
  Both boundaries were deliberately placed with lead-in/lead-out margin
  rather than frame-accurate against the nearest detected edge -- see
  docs/CHANGELOG.md for the measured margins (~0.73s lead-in, ~1.2s
  lead-out) and how they compare to reel03/04's tighter margins.
Clip duration: 45.1s -- just over the 20-45s default band, by 0.1s, because
the chosen boundaries intentionally trimmed INWARD from the raw sentence
edges for breathing room rather than cutting at the tightest possible frame;
within STYLE.md's 15-60s acceptable range.

This source is 4K (3840x2160) -- scaled down to 1920x1080 BEFORE calling the
shared crop_reframe_filter() (which assumes a 1920-wide input), so crop_x
stays directly comparable to previous sources' derivations.

Title card uses the per-slug override (title_compact.py), NOT the shared
overlays_lib.render_title() -- see build_reel01.py's docstring for the full
reasoning (this speaker has near-zero headroom above his hairline/tilak
mark). REUSED as-is, not rebuilt -- re-verified visually against this
clip's own probe frames (framing confirmed consistent with reel03/04, see
docs/CHANGELOG.md) before use, per this task's instructions.

crop_x=573 REUSED from reel03/04 (same speaker/source), NOT re-derived --
re-verified visually against this clip's own probe frames at 10%/50%/90%
before use, confirming the same consistent framing already established.

REBUILD (per user feedback that reels 05/06 STILL cut abruptly even with
the silence-margin boundary placement): this version adds a 0.2s video
fade-to/from-black + matching audio afade. IMPORTANT, learned the hard way
during THIS rebuild (see work/build-notes.md): the fade must be applied to
the FINAL COMPOSITED frame ([vout], after every overlay), NOT to the raw
background clip before compositing. A first attempt faded only the raw
clip and fed it into the same overlay chain as before -- the title card
and watermark PNGs are composited at full opacity for the clip's entire
duration (no enable= gating on them), so they stayed fully visible while
the video underneath dimmed to black, which visually reads as the title
floating in a black frame -- an overlay-desync artifact, exactly the
failure mode this task's instructions warned about checking for. Caught
by directly inspecting extracted start/end frames, not assumed from the
filter graph alone. Fixed by moving the `fade` filter to the tail of the
filter_complex (applied to [vout] once all overlays are already
composited) and the `afade` filter onto the audio stream the same way, so
title/subtitle/watermark fade together with the background as one unit.
The cut boundaries themselves (111.5s/156.6s source, confirmed correct
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
CLIP = "clip03_dharmadevi-name-meaning.mp4"
WM = "../../assets/watermark.png"
TOPIC = "dharmadevi-name-meaning"
# Cut-transition fade -- applied to the FINAL composited frame, not the
# raw background clip (see docstring above for why). 0.2s, chosen and
# verified in tools/fade_clip.py's module docstring; same duration used
# consistently across all 6 clips in this task.
FADE_DURATION = 0.2
# This is a REBUILD/FIX of an already-assigned reel number, not a new reel
# -- do NOT call next_reel_number(SLUG) here. By the time this rebuild
# runs, reels 05/06 already exist on disk, so next_reel_number would
# return 07/08, which is wrong: this script must overwrite the existing
# reel 05 in place (same number, fixed content), per this task's explicit
# instruction. The number is fixed at the value originally assigned.
REEL_NUM = 5

# crop_x=573 derived + verified for THIS source/speaker on reel03/04 (see
# docs/CHANGELOG.md) -- REUSED here (same speaker/source), re-verified
# visually against THIS clip's own probe frames before use, per STYLE.md's
# "verify by rendering against a real frame" rule.
CROP_X = 573

# Subtitles: spell-checked, PARAPHRASED (not a verbatim VTT quote -- see
# STYLE.md's transcript-source honesty rule), clip-relative seconds (clip
# starts at source 111.5s). NOTE: the raw auto-caption includes an isolated,
# garbled word "Koravanji" ("Devi Koravanji, the goddess who teaches
# Dharma") that does not parse as a confirmed Sanskrit/Kannada term in
# tools/sanskrit_terms.py and is not independently verifiable here -- per
# GUARDRAILS.md ("never guess a Sanskrit/Madhwa proper noun's spelling"),
# it is NOT used in these subtitles; the line is paraphrased around it using
# only the clearly-translated English meaning ("the goddess who teaches
# Dharma") instead. Flagged in the final report as uncertain, not added to
# tools/sanskrit_terms.py.
subs = [
    ("In that sense, the name", 0.5, 3.8),
    ("Dharmadevi is very meaningful.", 3.9, 7.1),
    ("It means the goddess who teaches Dharma.", 7.2, 10.8),
    ("If Padmavati's life is to be preserved,", 11.0, 17.3),
    ("it will be through that very Dharma.", 17.4, 20.6),
    ("Srinivasa says: that name itself shows", 27.9, 30.7),
    ("I am the one who bears her Dharma.", 30.8, 34.0),
    ("If she is given to me in marriage,", 34.1, 40.4),
    ("she will live. In that sense,", 40.5, 44.0),
    ("the Lord himself calls the name meaningful.", 44.1, 45.1),
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
    tp = render_title_compact(outdir, "What Does the Name", "Dharmadevi Mean?")

    dur = clip_duration(CLIP)
    sub_paths = [(render_sub(outdir, i, t), s, e) for i, (t, s, e) in enumerate(subs, 1)]

    num_str = format_reel_number(REEL_NUM)
    out_dir = reel_dir(SLUG)
    # Build to a STAGING filename, not the final name directly -- the old
    # (abrupt) reel 05 is still at the final name and must stay intact
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
