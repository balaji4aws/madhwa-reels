# Workflow

How one YouTube discourse becomes live reels. Follow the steps in order.
Visual rules (fonts, colors, sizes) are in `docs/STYLE.md`; things never to
do are in `docs/GUARDRAILS.md`.

**At a glance:** download → pick moments → cut → style → check → upload →
record the link.

**Run everything from the project folder** (`madhwa reels/`) with the Python
that has Pillow: `/Users/venkyb/envs/bie-work/bin/python3`.
(`/usr/bin/python3` has no Pillow and will fail.)

---

## 1. Download the source

- Get the **full** video with `yt-dlp --cookies-from-browser chrome`, plus
  English and Kannada captions. Never download a trimmed section.
- Check the downloaded length matches the length on YouTube.
- **Scan the whole source for glitches:**
  `python3 tools/glitch_scan.py sources/<slug>/source.mp4`. Uploaders'
  videos can contain editor placeholders ("Missing File"), black or solid
  flashes, or frozen cards. Flags in the first/last few seconds are normal
  intros and outros. Note any flag in the middle and don't cut across it,
  or cover it with `hold_frames` in `reels.json` (holds the last good frame
  while the audio continues).
- Pick a short **slug** for this source (e.g. `venkatachala-ep07`). It is
  used in every file name from here on.
- **Already in `docs/SOURCES.md`?** Then it's a repeat on purpose. Skip the
  download, reuse the slug, and pick moments that are **different from every
  reel already cut from it** (see the cut ranges in `work/<slug>/build_reel*.py`).
  Never delete the reels already live. See `docs/STYLE.md` → "Repeated sources".
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
- **Use the Kannada captions (`source.kn.vtt`) to place cuts, not the
  English.** The English is a machine translation: its word timings are
  evenly-spaced guesses and its sentences don't line up with the audio. The
  Kannada cues follow the real speech. Pick each start/end from where a
  Kannada sentence begins/ends **and** a real pause (`ffmpeg silencedetect`)
  sits there. Avoid ending on a dangling `ಅನ್ನುವುದನ್ನು` / mid-clause word.
- Leave a little quiet after the last word (aim for 0.5–0.7s; never less
  than ~0.4s — if the pause is shorter, choose a different ending).
- Output: confirmed start/end + `work/<slug>/cut_report_NN.json`

## 4 + 5. Cut and style the reel

Add the reel to `work/<slug>/reels.json` (cut points, title, subtitles with
clip-relative times, caption text), then run:

```
/Users/venkyb/envs/bie-work/bin/python3 tools/reel_builder.py <slug> <NN>
```

`tools/reel_builder.py` cuts the raw clip (re-encoded, frame-accurate) to
`work/<slug>/clipNN_<topic>.mp4`, styles it, writes the reel + `.caption.txt`,
and prints the real quiet at the head/tail of the finished file. It refuses
cuts of 60s or longer and subtitles that would wrap to two lines.
(Older reels were built with per-reel `build_reelNN.py` scripts; those stay
as-is, new reels use the spec + builder.) In order, it does:

1. **Reframe** to 1080x1920 by cropping around the speaker. Work out a fresh
   `crop_x` for every new source; never reuse another source's value.
2. **Title card** at the top. Check one frame first: if the title touches the
   speaker's forehead, use a per-source `title_compact.py` (see ep06/ep07).
3. **Subtitles, Kannada + English** (owner rule from 2026-10-23): add the
   Kannada line as the 4th item of each subtitle in `reels.json`
   (`["English", start, end, "ಕನ್ನಡ"]`). Kannada goes on top in Noto Sans Kannada
   Bold 44px, English below in Noto Sans Bold 36px (same family as the Kannada). Each line gets its own band with
   a 26px gap between them, and each must fit on one line. Take the Kannada
   from `source.kn.vtt` (the speaker's own words) and clean up only obvious
   auto-caption errors. If a line is garbled, rebuild it faithfully and
   record it in the reel's `note`. (Older English-only reels use one line
   at `SUB_Y = 1560`.)
4. **Watermark:** `assets/watermark.png` (channel URL + brand icon).
5. **Fade:** 0.2s fade in/out on the finished picture **and** the audio,
   applied after everything is composited so it all fades together.
   A fade only smooths a cut that already lands in quiet; it can't fix a cut
   that lands on speech.

Get the reel number from `tools/reel_numbering.py` when adding the reel to
`reels.json`, then keep it fixed there. Numbers are never reused. (The tool
counts numbers in `docs/SOURCES.md` and `work/<slug>/` too, because uploaded
reels are deleted locally and `reels/<slug>/` alone would restart at 01.)

- Output: `reels/<slug>/<slug>_NN_<topic>.mp4` + a matching
  `.caption.txt` (TITLE / DESCRIPTION / HASHTAGS)

> **Watermark:** `assets/watermark.png` now holds the URL + icon version
> (rendered 2026-10-23, approved by the owner the same day).

## 6. Check the reel

Run `work/<slug>/check_reel.py`. A reel is not ready until all of these pass:

- **Size and length:** 1080x1920 and **under 60s**. Either failing is a hard FAIL.
- **English spelling:** dictionary + `tools/sanskrit_terms.py`. Never guess a
  Sanskrit name; flag it if it isn't in the list.
- **Kannada spelling:** `tools/kannada_check.py`, run automatically by
  `reel_builder.py`. A broken word (one starting with a vowel sign or
  virama, two signs stacked, stray Latin letters) is a hard FAIL. Any word not
  found in the speaker's own Kannada captions is listed for review: read
  each one. There is no full Kannada dictionary check (none is installed or
  reliable), so the review list plus the owner's read are the real check.
- **Cut placement:** start and end sit on caption sentence boundaries.
- **Every frame, not a sample:** `tools/glitch_scan.py` on the finished
  reel. `reel_builder.py` runs it automatically and stops on any flag. Spot
  frames missed a 1.6s "Missing File" card that was in ep06's source (reel
  10, 2026-10-23).

Then check by hand:

- **The ending, on the finished file:** run `ffmpeg silencedetect` on the
  finished reel. If the speaker is still talking in the last ~0.5s, the cut
  is too tight.
- **Listen** to the first ~1s and last ~1.5s. Does it end on a complete
  thought, or does it feel cut off? Passing numbers alone have been wrong before.
- **Look** at a few frames: title, subtitles and watermark readable, nothing
  overlapping, speaker's face clear.

## 7. Upload (no review gate)

Once step 6 passes, upload directly. No owner review is needed (owner
direction, 2026-10-23); the owner reviews on the channel.

- **One reel a day, at 6:00 PM IST** (owner rule, 2026-10-23). Upload each
  finished reel as scheduled, one at a time, from the project folder:
  `upload/.venv/bin/python upload/youtube_upload.py reels/<slug>/<reel>.mp4 --schedule-daily`
  It takes the next day with no reel going public and schedules this reel
  for 6:00 PM IST that day. YouTube publishes it on its own servers, so the
  laptop can be asleep or off. `--next-slot` shows the next free day
  without uploading. Each upload's `.caption.txt` supplies the
  title/description/hashtags.
- Uploading without `--schedule-daily` publishes immediately. Use that only
  when the owner asks for a reel to go live now, e.g. a review sample or a
  replacement.
- **Daily limit:** exact number unknown (20 went through on 2026-10-23;
  resets at midnight Pacific). Upload one at a time; on the first quota
  refusal, stop and upload the rest the next day.
- Instagram is posted by hand by the owner using the same `.caption.txt`
  as-is (owner confirmed 2026-10-23: no separate Instagram version needed).
- **Fixing a live video's description** (no re-upload, same link and views):
  edit its `.caption.txt`, then
  `upload/.venv/bin/python upload/youtube_upload.py --update-description VIDEO_ID --caption <file>.caption.txt`.
  The title is left unchanged. Only do this for videos the owner names.

## 8. Record

- **Keep** the uploaded reel and its `.caption.txt` in `reels/<slug>/`. Do not
  delete them. Keep `sources/` and `work/` too.
- Add the reel's YouTube link to its row in `docs/SOURCES.md` as soon as the
  upload finishes. The link exists right away even for a scheduled reel.
  Add *(goes live DATE, 6 PM IST)* after it until that date. No link means
  not uploaded.
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
