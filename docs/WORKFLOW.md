# Workflow

How one YouTube discourse becomes live reels. Follow the steps in order.
Visual rules (fonts, colors, sizes) are in `docs/STYLE.md`; things never to
do are in `docs/GUARDRAILS.md`.

**At a glance:** download → pick moments → cut → style → check → owner
reviews → upload → clean up.

**Run everything from the project folder** (`madhwa reels/`) with the Python
that has Pillow: `/Users/venkyb/envs/bie-work/bin/python3`.
(`/usr/bin/python3` has no Pillow and will fail.)

---

## 1. Download the source

- Get the **full** video with `yt-dlp --cookies-from-browser chrome`, plus
  English and Kannada captions. Never download a trimmed section.
- Check the downloaded length matches the length on YouTube.
- Pick a short **slug** for this source (e.g. `venkatachala-ep07`). It is
  used in every file name from here on.
- Output: `sources/<slug>/source.mp4`, `source.en.vtt`, `source.kn.vtt`

## 2. Pick the moments

Read `source.en.vtt` and choose moments that **end on a complete thought**.

- **Best candidates** — look for these two first:
  1. The speaker **giving advice** to people or society.
  2. The speaker telling the **high point of a story**.
- **Avoid** the middle of an explanation or story. These feel abruptly cut
  no matter where the cut goes, because the thought isn't finished.
- **Length:** every reel must be **under 60 seconds**. Try for **~15s
  first** when a moment that short works on its own; go longer only when the
  payoff needs it.
- **Build the shortest ones first.**
- Output: a list of rough `start – end` times (in seconds) with a topic for each.

## 3. Place the cuts

- Run `tools/clip_cutter.py` on each rough start/end. It snaps to a real
  pause and checks the caption timing, flagging each boundary `clean`,
  `snapped-low-confidence`, or `review-manually`.
- For every `review-manually` flag, read the caption text at that time
  yourself before trusting or overriding the snap.
- Leave a little quiet after the last word (aim for 0.5–0.7s).
- Output: confirmed start/end + `work/<slug>/cut_report_NN.json`

## 4. Cut the raw clip

- Cut with `ffmpeg`, re-encoding (not `-c copy`) so the cut is frame-accurate.
- Output: `work/<slug>/clipNN_<topic>.mp4`

## 5. Style the reel

Write a build script `work/<slug>/build_reelNN.py` (copy the nearest
existing one). It uses `tools/overlays_lib.py` and does, in order:

1. **Reframe** to 1080x1920 by cropping around the speaker. Work out a fresh
   `crop_x` for every new source; never reuse another source's value.
2. **Title card** at the top. Check one frame first: if the title touches the
   speaker's forehead, use a per-source `title_compact.py` (see ep06/ep07).
3. **Subtitles:** one line at a time, spell-checked, at `SUB_Y = 1560`.
4. **Watermark:** `assets/watermark.png` (channel URL + brand icon).
5. **Fade:** 0.2s fade in/out on the finished picture **and** the audio,
   applied after everything is composited so it all fades together.
   A fade only smooths a cut that already lands in quiet; it can't fix a cut
   that lands on speech.

Get the reel number from `tools/reel_numbering.py` on the first build, then
keep it fixed in the script. Numbers are never reused.

- Output: `reels/<slug>/<slug>_NN_<topic>.mp4` + a matching
  `.caption.txt` (TITLE / DESCRIPTION / HASHTAGS)

> **Watermark, first time only:** the URL + icon watermark hasn't been
> rendered yet. On the next build, run `assets/make_watermark.py`, check it
> on a real frame (centered, readable, not touching the right edge), and get
> the owner's OK before using it.

## 6. Check the reel

Run `work/<slug>/check_reel.py`. A reel is not ready until all of these pass:

- **Size and length:** 1080x1920 and **under 60s**. Either failing is a hard FAIL.
- **Spelling:** dictionary + `tools/sanskrit_terms.py`. Never guess a
  Sanskrit name; flag it if it isn't in the list.
- **Cut placement:** start and end sit on caption sentence boundaries.

Then check by hand:

- **The ending, on the finished file:** run `ffmpeg silencedetect` on the
  finished reel. If the speaker is still talking in the last ~0.5s, the cut
  is too tight.
- **Listen** to the first ~1s and last ~1.5s. Does it end on a complete
  thought, or does it feel cut off? Passing numbers alone have been wrong before.
- **Look** at a few frames: title, subtitles and watermark readable, nothing
  overlapping, speaker's face clear.

## 7. Owner review

Tell the owner the reel is ready and where it is. **Nothing is uploaded until
the owner approves that specific reel.**

## 8. Upload (after approval)

- From the project folder:
  `upload/.venv/bin/python upload/youtube_upload.py reels/<slug>/<reel>.mp4`
- It goes live as **public** immediately and reads title/description/hashtags
  from the `.caption.txt`.
- Instagram is posted by hand by the owner using the same `.caption.txt`.

## 9. Clean up and record

- Delete the uploaded reel's `.mp4` and `.caption.txt` from `reels/<slug>/`
  (exact file names). **Keep** `sources/` and `work/` (build scripts, cut
  reports, raw clips).
- Add or update the reel's row in `docs/SOURCES.md` with its YouTube link.
- Add a dated note to `docs/CHANGELOG.md` for anything learned.
- Commit and push the doc/script changes to GitHub.

---

## Where things go

| What | Folder |
|------|--------|
| Downloaded source + captions | `sources/<slug>/` |
| Build scripts, cut reports, raw clips | `work/<slug>/` |
| Finished reels (until uploaded) | `reels/<slug>/` |
| Shared tools | `tools/` |
| Watermark + brand icon | `assets/` |
