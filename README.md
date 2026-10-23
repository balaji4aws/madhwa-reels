# Madhwa Reels

Turning long Madhwa / Dvaita devotional discourses (from YouTube) into short
vertical reels for the **Madhwa16** channel
(https://www.youtube.com/@madhwa16/) — posted to YouTube Shorts automatically,
and to Instagram Reels by hand.

This is a personal project, run with the help of an AI coding assistant acting
as the video editor. You share a YouTube link; the assistant finds the strong
moments in the talk, cuts them into short vertical reels in a consistent
house style, checks them, and uploads them.

> **About this repository:** this repo holds only the *pipeline* — the small
> plain-text scripts (`.py`) and documentation (`.md`) that run the workflow.
> The source videos, per-video working files, and finished reels are large
> binary media that stay on the maintainer's machine only and are excluded
> via `.gitignore` (so are the YouTube OAuth secrets, which are never
> committed). If you're browsing this and wondering where the videos are:
> they're not here by design — see "Where things live" below.

This README stays simple on purpose — it explains the overall flow once. For
the operational details, see `docs/`:

- **`docs/WORKFLOW.md`** — the pipeline, step by step, with the actual tool
  used at each step. Read this to re-orient quickly after time away.
- **`docs/STYLE.md`** — the current house-style rules (fonts, colors, exact
  video specs, safe zones). This changes in small ways often — expect this
  project to keep getting tuned for a long time, not a one-time build.
- **`docs/GUARDRAILS.md`** — things the assistant must never do without
  explicit confirmation (destructive actions, secrets, scope creep). Read
  this first if you're new to working on this project.
- **`docs/SOURCES.md`** — a simple table of which source videos have been
  processed and how many reels came from each.
- **`docs/CHANGELOG.md`** — a running, dated log of what was tried, what
  worked, and what didn't, across every session. Never edited after the
  fact, only appended to.

---

## The flow, in one line

**Long discourse in → several short reels out → checked → uploaded.**

---

## The flow, step by step

1. **You share a YouTube link.** Optionally you can give exact timestamps for
   a moment you already liked; otherwise the assistant finds good moments on
   its own by reading the talk's captions.

2. **Download.** The full video and its captions get downloaded once, into
   `sources/<video-name>/` on this machine. (Not uploaded to GitHub — see
   below.)

3. **Find the moments.** The talk is scanned for self-contained teachings —
   a complete thought with a clear hook and payoff, short enough to work as a
   reel on its own. A single long talk usually produces several reels, not
   just one.

4. **Cut and style each reel.** Each chosen moment becomes a vertical 9:16
   video: the background is reframed so nothing is cropped off the speaker, a
   title card is added, spell-checked English subtitles are burned in, and
   the channel watermark is placed in a spot that won't get hidden by
   Instagram/YouTube's own on-screen buttons.

5. **Check it, every time, before upload.** See the next section — nothing
   gets uploaded without going through this.

6. **Upload.** YouTube Shorts: automatic, goes live as public right away.
   Instagram: posted by hand, using the title/description/hashtags the
   assistant prepares alongside the video.

---

## What gets checked before a reel is uploaded

Every reel goes through the same checks before it's considered finished:

- **Right shape and length.** Confirms the video is proper vertical format and
  not too long to count as a Short.
- **Spelling.** Every word in the subtitles is checked. Sanskrit and Madhwa
  names (Venkatachala, Vrishabhachala, and so on) are checked against a
  growing reference list of correct spellings, so a wrong auto-captioned
  spelling gets caught and fixed rather than slipping through. This list is
  expected to keep growing — if you spot a name spelled wrong in a reel, that
  gets added to the list so it's fixed everywhere, forever after.
- **Clean cuts.** Checks that a reel doesn't start or end mid-sentence, cutting
  off a word. This is checked against the talk's own captions, not just by
  listening for a quiet moment, because the audio often has a constant
  background drone that makes "listen for silence" unreliable on its own.
- **A visual look.** A few frames from the finished reel are pulled and looked
  at directly, to confirm the title and subtitles are readable, the watermark
  is in place, and nothing overlaps badly.

If any check finds something questionable, it gets looked at and fixed before
the reel is called done — nothing goes out "good enough, probably."

---

## Where things live

```
madhwa reels/
├── README.md             ← this file
├── docs/                 ← the house style rulebook and the lessons log
├── tools/                ← small shared scripts used across every video
├── assets/               ← the channel watermark + brand icon
├── upload/                ← the YouTube upload script
├── sources/<slug>/       ← downloaded videos (large — not on GitHub)
├── work/<slug>/          ← per-video working files (large — not on GitHub)
└── reels/                ← finished reels (large — not on GitHub)
```

**What's on GitHub and what isn't:** the actual scripts that run this
pipeline (plain `.py` files in `tools/`, `work/<slug>/`, and `upload/`) are
small text files and are tracked normally. The downloaded source videos,
per-video working files, and finished reels are large video files that
change constantly — those stay local on this machine only and are excluded
via `.gitignore`, so they never get pushed to GitHub.

**The two files that keep improving over time:**

- **`docs/STYLE.md`** — the exact rulebook: fonts, colors, video specs, safe
  zones, how cuts get placed, what the checks look for. This is the file to
  edit whenever the look or the rules need to change.

---

## Honest limitations, worth knowing

- The English subtitles come from YouTube's own automatic captioning and
  translation of the Kannada audio — not a transcript made specifically for
  this project. They're cleaned up for spelling and readability, but for
  anything where the exact wording matters (a precise philosophical point, a
  Sanskrit quotation), treat them as a close paraphrase rather than a
  word-for-word translation.
- Good moments are found by reading text, not by watching the video — a
  striking visual moment with little speech could be missed. Sharing a
  timestamp directly always works as a fallback.
