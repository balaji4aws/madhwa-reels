# Workflow — the pipeline, step by step

A concrete, operational reference for "what actually happens, in order."
`README.md` explains this in plain language for a newcomer; this file is the
quick re-orientation doc — read this if you're coming back after weeks away
and need to remember the actual mechanics, not the pitch.

---

## Step 1 — Get the source video

- Input: a YouTube link (shared by the channel owner), optionally with
  timestamps for a moment already picked out.
- Tool: `yt-dlp --cookies-from-browser chrome` (this machine needs browser
  cookies to pass YouTube's bot detection).
- Output: `sources/<slug>/source.mp4` + `source.en.vtt` + `source.kn.vtt`
  (English and Kannada auto-captions, pulled alongside the video).
- A **slug** is a short id for this source video, e.g. `venkatachala-ep01`.
  Chosen once per source video, used in every filename downstream.

## Step 2 — Find candidate moments

- Input: `source.en.vtt` (the English captions).
- Process: read the captions for self-contained teachings — a complete
  thought with a hook and a payoff, short enough to work as a standalone
  reel. A single long talk usually yields several such moments.
- Output: a list of candidate `(start_time, end_time, topic)` windows in
  source-video seconds. No file artifact yet — this is a reading/judgment
  step, recorded directly into the next step's cut decisions.

## Step 3 — Place the cut boundaries precisely

- Input: a candidate rough `(start, end)` window from Step 2.
- Tool: `tools/clip_cutter.py` — runs `ffmpeg silencedetect` near each rough
  boundary to find a real pause in the speech, then cross-checks the snapped
  point against the VTT caption-cue boundaries, and reports a confidence
  flag per boundary: `clean` / `snapped-low-confidence` / `review-manually`.
- Any `review-manually` flag gets checked by hand — read the caption text at
  that exact timestamp to confirm it's a real sentence boundary, not a false
  alarm from a long run-on caption cue (a known, common pattern on this
  source material — see `docs/CHANGELOG.md`).
- Output: a confirmed `(start, end)` pair in source-video seconds, plus a
  `cut_report_NN.json` audit file recording the decision.

## Step 4 — Cut the raw clip

- Input: the confirmed `(start, end)` pair + `source.mp4`.
- Tool: `ffmpeg`, re-encoding (not a fast `-c copy` cut) so the boundary is
  frame-accurate.
- Output: `work/<slug>/clipNN_<topic>.mp4` — the raw, un-styled horizontal
  clip for this one reel.

## Step 5 — Style the reel

- Input: the raw clip, plus a hand-written title and a short list of
  spell-checked subtitle lines with their timing (clip-relative seconds).
- Tool: a per-reel build script (e.g. `work/<slug>/build_reel06.py`), using
  `overlays_lib.py` to render all text as transparent PNGs (this machine's
  ffmpeg has no `drawtext` filter — see `docs/STYLE.md`), then `ffmpeg
  overlay` to composite: reframed video + title card + subtitle + watermark.
- Exact visual rules (crop vs. fill, safe zones, fonts, colors) live in
  `docs/STYLE.md` — this step always reads that file first.
- Output: `reels/<slug>_NN_<topic>.mp4` + a matching
  `<slug>_NN_<topic>.caption.txt` sidecar (title/description/hashtags).

## Step 6 — Check the reel

- Tool: `work/<slug>/check_reel.py`.
- Checks performed:
  1. **Dimensions/duration** — must be 1080x1920; flags anything over 60s.
  2. **Spelling** — every subtitle word checked against the system
     dictionary + `tools/sanskrit_terms.py` (the growing reference list of
     correct Sanskrit/Madhwa name spellings). A KNOWN WRONG transliteration
     is a hard FAIL, not just a warning.
  3. **Clean cuts** — re-verifies the start/end against the VTT caption
     boundaries (same method as Step 3, as a final gate).
- Then: a few preview frames are extracted and looked at directly to
  confirm the title/subtitle are legible, the watermark is placed correctly,
  and nothing overlaps badly. This visual check has no automated tool —
  it's a direct look at actual frames, every time.
- A reel is not considered finished until this step passes (or every
  warning has been manually reviewed and understood).

## Step 7 — Upload

- Tool: `upload/youtube_upload.py` (isolated venv at `upload/.venv/`).
- YouTube Shorts: automatic, defaults to **public**, goes live immediately.
  Reads title/description/hashtags from the `.caption.txt` sidecar.
- The same script can also manage already-uploaded videos:
  `--set-privacy`, `--delete`, `--replace` — see `docs/GUARDRAILS.md` for
  the rules on when these are and aren't okay to use.
- Instagram: no API posting (no business account). The channel owner posts
  the `.caption.txt` content by hand.

---

## Where each step's output lives

| Step | Output | Folder |
|------|--------|--------|
| 1 | source video + captions | `sources/<slug>/` |
| 3, 4 | cut report, raw clip | `work/<slug>/` |
| 5 | finished reel + caption sidecar | `reels/` |
| 7 | nothing new locally — the video is now also live on YouTube | — |

## Quick fact sheet

- Reel spec: 1080x1920, 30fps, H.264 high/yuv420p, ~6Mbps, AAC 192k, +faststart.
- Target length: see `docs/STYLE.md`'s "Clip selection" section (it varies
  by target platform/audience).
- One source video → multiple reels, numbered `_01`, `_02`, etc.
- See `docs/SOURCES.md` for which source videos have been processed and how
  many reels came from each.
