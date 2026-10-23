# Cutting Workflow Improvement Plan — venkatachala-ep01 Reels 06 & 07

Goal (from the user): make the clip-cutting step of the pipeline reusable and
self-improving, and use it right now to produce **2 new reels** sized for a
Gen-Z Instagram/YouTube-Shorts audience (short, punchy, 15-30s) from the
`venkatachala-ep01` source we already have. Upload stays YouTube-only and
automated-but-not-executed (no OAuth creds yet) — Instagram stays manual per
existing house rules.

This plan does not change the verification philosophy already locked in by
STYLE.md (now `docs/STYLE.md`) / check_reel.py: **cut-quality verification
stays caption-boundary based.** `silencedetect` is retained, but only as an input to *choosing* a snap
point, never as the final pass/fail signal — the background tanpura/shruti
drone under the speech makes raw loudness unreliable as a verifier (a real
pause and continuous speech both read "loud"). This is the one lesson from
the existing `check_reel.py` docstring that must not be re-litigated.

---

## 1. Reusable cutting module: `work/clip_cutter.py`

**Location choice:** `work/clip_cutter.py`, one level above the per-source
folders (`work/<slug>/`), not inside `work/venkatachala-ep01/`. Everything
built so far (`recut.py`, `build_all.py`, `check_reel.py`) lives inside a
single slug's folder and hardcodes that slug's paths — reusable logic has
nowhere to live without copy-pasting per video. Placing `clip_cutter.py` at
`work/` makes it a shared library/CLI any future `work/<new-slug>/` script can
import or shell out to, by passing `--video` / `--vtt` paths explicitly. This
mirrors how `assets/watermark.png` and `upload/` already sit outside any one
slug's folder as shared, cross-source resources.

### What it replaces

Today, boundary selection is manual (`recut.py`'s `CUTS` list is hand-typed
timestamps the editor eyeballed) and verification is a separate afterthought
run post-hoc via `check_reel.py --vtt --src-start --src-end`. There is no
single place that (a) proposes a snapped boundary and (b) immediately reports
its own confidence. `clip_cutter.py` fuses both steps into one tool that runs
*before* the final cut is committed, so lessons accumulate in one report
instead of being rediscovered reel by reel.

### Design

```
work/clip_cutter.py
```

A single module usable both as a library (`from clip_cutter import snap_boundary`)
and as a CLI:

```
python3 clip_cutter.py \
  --video sources/<slug>/source.mp4 \
  --vtt   sources/<slug>/source.en.vtt \
  --start 1131.0 --end 1168.5 \
  [--window 4.0] [--silence-db -30] [--silence-min-dur 0.25] \
  [--json report.json]
```

Functions:

1. `load_cues(vtt_path) -> list[(start, end, text)]`
   Parse the VTT into merged sentence-level cue intervals. **Reuse the exact
   regex/interval-merge approach already in `check_reel.py`'s
   `boundary_cut_check`** (the `(\d\d):(\d\d):(\d\d)\.(\d+)\s*-->...` pattern
   and the cue-list build) rather than re-deriving it — that parsing is
   already correct and tested against this VTT's run-on-cue quirks.

2. `find_candidate_pause(video_path, center_time, window=4.0, db=-30, min_dur=0.25) -> list[(pause_start, pause_end)]`
   Extract a short audio window around `center_time` (`ffmpeg -ss <center-window> -t <2*window> -i video -af silencedetect=noise=<db>dB:d=<min_dur> -f null -`),
   parse `silence_start` / `silence_end` pairs from stderr. Conservative
   defaults (`-30dB`, `0.25s` minimum) are deliberately stricter than a naive
   threshold *precisely because* of the constant drone — the goal here is only
   to bias the snap point toward a true gap in speech, not to certify one.
   Returns every detected gap in the window, sorted by closeness to
   `center_time`.

3. `snap_boundary(video_path, vtt_cues, rough_time, window=4.0) -> dict`
   - Calls `find_candidate_pause` around `rough_time`.
   - If a pause is found, snaps to its midpoint; if none is found within the
     window, keeps `rough_time` unchanged and flags `"no_pause_found"`.
   - Cross-checks the (possibly snapped) time against `vtt_cues` using the
     **same `inside_cue` logic as `check_reel.py`** (ported into this module,
     not duplicated by hand — see "Code sharing" below): pad = 0.25s, "inside"
     = strictly between `a+pad` and `b-pad`.
   - Returns a dict: `{"requested": rough_time, "snapped": t, "pause_found": bool,
     "pause_gap_sec": float|None, "inside_cue": bool, "nearest_cue_text": str,
     "confidence": "clean"|"snapped-low-confidence"|"review-manually"}`.

   Confidence rule (deliberately conservative, mirrors the known false-positive
   note in STYLE.md):
   - `"clean"`: a pause was found AND the snapped point lands at/near a cue
     boundary (not inside a cue).
   - `"snapped-low-confidence"`: either no clear pause was found but the point
     still lands at a cue boundary, OR a pause was found but it's not very
     close to a cue boundary (ambiguous — long run-on cue is a known cause).
   - `"review-manually"`: the snapped point still falls clearly inside a cue
     with no nearby pause — the one pattern `check_reel.py` already says it
     "reliably catches."

4. `build_report(video, vtt, windows: list[(label, start, end)]) -> dict`
   Runs `snap_boundary` for every `(label, start, end)` pair's start and end,
   and returns one JSON-able structure:
   ```json
   {
     "video": "...", "vtt": "...",
     "boundaries": [
       {"label": "reel06_start", "requested": 1131.0, "snapped": 1130.6,
        "confidence": "clean", "pause_found": true, "inside_cue": false,
        "nearest_cue_text": "Earlier, a Brahmin named Madhava..."},
       ...
     ]
   }
   ```
   This is the **structured report** the task calls for. It is advisory: the
   CLI prints a human-readable summary (one line per boundary, confidence
   flagged) and optionally writes `--json <path>`. It never exits non-zero
   purely on a low-confidence flag — a human reads it and decides, exactly as
   `check_reel.py`'s own docstring already insists WARN is not FAIL.

### Code sharing with `check_reel.py`

`check_reel.py`'s `boundary_cut_check`/`inside_cue` logic should be extracted
into `clip_cutter.py` as the canonical implementation (`load_cues`,
`inside_cue`), and `check_reel.py` updated to import it
(`from clip_cutter import load_cues, inside_cue`) instead of keeping its own
copy — same regex, same pad constant, used in two places today. This removes
future drift between "the tool that picks the cut" and "the tool that checks
it," which is exactly the kind of inconsistency that erodes trust in both.

### Verify

- `python3 work/clip_cutter.py --video sources/venkatachala-ep01/source.mp4 --vtt sources/venkatachala-ep01/source.en.vtt --start 1131.0 --end 1168.5 --json /tmp/report.json`
  completes without a traceback, prints a per-boundary confidence line, and
  `/tmp/report.json` parses as valid JSON with both boundaries present.
- Re-run `work/venkatachala-ep01/check_reel.py` on an **existing** finished
  reel (e.g. `reels/venkatachala-ep01_03_why-anjanachala.mp4` with its known
  `--src-start 784.0 --src-end 843.4 --vtt sources/venkatachala-ep01/source.en.vtt`)
  after the `inside_cue`/`load_cues` extraction and confirm it prints the same
  PASS/WARN verdicts as before the refactor — the behavior must not change,
  only where the logic lives.

---

## 2. Two new candidate moments (from `source.en.vtt`)

Reels 01-05 already used these source ranges (confirmed from `recut.py` and
each reel's `.caption.txt`): **134.1-153.6s** (four names), **284.8-328.9s**
(senses), **784.0-843.4s** (Anjanachala), **1080.0-1129.3s** (Shesha/Vayu),
**1188.0-1247.4s** (Venkatachala burns sins). The full source is ~1285s
(21:25). The two candidates below sit in the two unused gaps: between reel04
and reel05 (1129.3-1188.0s), and after reel05 to the end of the talk
(1247.4-1285.1s). Neither overlaps any existing reel's range.

### Candidate A — "The sinner who was purified" (Madhava / Kapila Tirtha)

- **VTT timestamps / text** (from `source.en.vtt`):
  - `1131.36 --> 1135.35` "Earlier, a Brahmin named Madhava, who had committed great sins due to the fault of the noble Sangha,"
  - `1139.20 --> 1141.99` "lost his Brahminhood and became"
  - `1142.00 --> 1144.31` "corrupt."
  - `1144.32 --> 1148.55` "However, after making this pilgrimage to Venkatachala, he addressed his"
  - `1150.80 --> 1154.55` "ancestors at Kapila Tirtha.  Since"
  - `1164.24 --> 1168.79` "Venkatachala is said to have lost all his sins by performing Shraddha and making a pilgrimage, in this Kali Yuga, the"
- **Why self-contained at short length:** it is a complete three-beat story —
  a named man (hook: "a Brahmin committed great sins and lost his
  Brahminhood") → turning point ("pilgrimage to Venkatachala") → payoff
  ("lost all his sins"). No prior context is needed to understand it; it does
  not depend on the Yuga-names or Vrishabhasura material used in reels 01-03.
  It compresses naturally to ~20-25s once trimmed to just this beat (skip the
  Kapila Tirtha procedural detail, keep hook + turn + payoff).
- **Why it fits Gen-Z/Shorts pacing:** strong, concrete "before" state in the
  first line (sinner, lost status) states the stakes in under 2 seconds of
  speech-equivalent reading, one clean redemption arc, one payoff line — no
  multi-part list structure like reel01 (four names) or reel04 (two-deity
  comparison), which is exactly the "single clear payoff" shape the shorter
  15-30s target needs.

### Candidate B — "The one-line close: give it all up" (closing moral + shloka)

- **VTT timestamps / text:**
  - `1252.96 --> 1257.03` "We should make such a special approach, lose all our"
  - `1257.04 --> 1260.87` "sins, abandon our ego, and become"
  - `1269.28 --> 1272.95` "pure by rendering special service to the Supreme Lord, the Supreme Lord of the Wind, with all our dedication."
  - `1275.92 --> 1280.63` "The message to be understood from the sequence of these four names is: Haraye Namah"
  - `1280.64 --> 1283.64` "Shri Krishna Arpanamasta."
- **Why self-contained at short length:** this is the discourse's own summary
  line delivered as a single payoff — "lose your sins, abandon ego, serve the
  Supreme Lord" — closed by the speaker's own Sanskrit dedication shloka
  ("Haraye Namah... Krishna Arpanamastu" — "salutations to Hari, I offer this
  to Krishna"). It needs no earlier setup to land: it reads as a complete
  teaching + a mantra-like closing line, which is a familiar short-form shape
  (a "today's lesson" clip ending on a chantable line).
- **Why it fits Gen-Z/Shorts pacing:** it is naturally the shortest, punchiest
  unit in the whole talk — one imperative sentence (hook: "lose your ego")
  immediately followed by the payoff mantra. At ~31s total source span it
  trims to the ~20-28s range without losing anything; it also works well as a
  recurring "closing reel" format for future videos (every discourse likely
  ends with a similar moral + shloka), which is worth noting as a pattern.

---

## 3. New reel names and target cut windows (before snapping)

| Reel | File name | Target window (rough, source seconds) |
|---|---|---|
| 06 | `venkatachala-ep01_06_sinner-purified.mp4` | **1130.0 – 1169.0** (~39s rough; trim to hook+payoff only during subtitle authoring, target final ~20-25s) |
| 07 | `venkatachala-ep01_07_lose-your-ego.mp4` | **1252.0 – 1284.0** (~32s rough, close to final length already) |

These are the *rough* windows to feed into `clip_cutter.py --start/--end`; the
implementation step must run the snap/verify pass and use the tool's
`"snapped"` times for the actual `ffmpeg -ss/-to` cut, not these rough numbers
directly. Topic slugs (`sinner-purified`, `lose-your-ego`) follow the existing
`<slug>_<number>_<topic>.mp4` convention used by reels 01-05.

**Target final duration:** both should land in **15-30s** after trim (per the
user's explicit Gen-Z/Instagram framing in this task), narrower than the
general house-style 20-45s band in STYLE.md (now `docs/STYLE.md`) — see
the rule update in section 4.

---

## 4. STYLE.md / steering file updates to apply verbatim

[Note: STYLE.md has since moved to `docs/STYLE.md` as part of a later
reorg — apply these to the file at its current location.]

Apply these to `madhwa reels/docs/STYLE.md` and the mirrored
`.kiro/steering/madhwa-reels.md` (keep both in sync, as they already
duplicate the same rules):

1. **Document the cutting tool.** Add under "Clip selection" or a new "Cut
   placement" subsection:
   > Use `work/clip_cutter.py` as the standard cut-boundary tool for every
   > source video (not just one slug) — it proposes a silence-snapped
   > boundary near a rough timestamp and cross-checks it against the VTT cue
   > boundaries, emitting a confidence flag (`clean` /
   > `snapped-low-confidence` / `review-manually`) per boundary. Run it before
   > committing a cut; always review `review-manually` flags by reading the
   > caption text at that timestamp, same as the existing odd-cut check.

2. **Clarify the role of `silencedetect` vs. verification**, to prevent future
   confusion given how easy it is to conflate "use silencedetect" with "trust
   loudness":
   > `ffmpeg silencedetect` is allowed and useful for *choosing where to snap*
   > a rough cut point to a real pause in speech. It must never be used as
   > the final pass/fail check on a finished cut — that stays caption-boundary
   > based (`check_reel.py`'s `inside_cue` check), because the constant
   > background drone on these recordings makes loudness alone unreliable as
   > a verifier.

3. **Add a short-form length tier for Instagram/Gen-Z-targeted reels.**
   STYLE.md's (now `docs/STYLE.md`) current "Target length 20-45s; 15-60s
   acceptable" is the general band; add:
   > When a reel is explicitly meant for Instagram Reels / Gen-Z-paced
   > consumption, target the shorter **15-30s** end of the range: one hook in
   > the first 1-2s, one payoff, no multi-part list. The 20-45s band remains
   > the default for YouTube-first or multi-point teachings (e.g. the 4-names
   > list format).

4. **Record the "closing moral + shloka" pattern** as a reusable moment type
   for future sources:
   > Discourses often end with a short summary line + a Sanskrit dedication
   > shloka. Treat this as its own recurring candidate-moment category when
   > auto-picking moments — it is usually self-contained and short.

5. **Note the code-sharing requirement** so the two scripts don't re-diverge:
   > `check_reel.py`'s caption-boundary cut check (`inside_cue`/`load_cues`)
   > is implemented once in `work/clip_cutter.py` (now `tools/clip_cutter.py`)
   > and imported by `check_reel.py` — do not re-implement this logic a
   > second time in a new per-slug script; import the shared module.

(These are described here for the implementer to copy into both files
verbatim or near-verbatim; this plan file does not edit STYLE.md
or the steering file itself.)

---

## 5. Upload readiness — explicit scope boundary

**Do not attempt any live YouTube upload.** `upload/client_secret.json` is not
configured yet (per `upload/SETUP.md`, this requires a one-time Google Cloud
OAuth setup the user hasn't done). The implementation step should:

- Build reels 06 and 07 fully (cut, style, subtitles, watermark, checks,
  `.caption.txt` sidecars) and leave them in `reels/`.
- Leave a plain-text readiness note (e.g. printed in the final summary, or a
  short note alongside the reels) stating: both reels are built and each has
  a `.caption.txt` sidecar with title/description/hashtags ready for
  `upload/youtube_upload.py reels/<reel>.mp4` once
  `upload/client_secret.json` exists; until then, no upload call should be
  made.
- Do not create, modify, or probe `upload/client_secret.json` or
  `upload/token.json`, and do not run `upload/youtube_upload.py`.

---

## Implementation order

1. Extract `inside_cue`/`load_cues` out of `check_reel.py` into
   `work/clip_cutter.py`; update `check_reel.py` to import them; re-run
   `check_reel.py` against an existing finished reel to confirm unchanged
   output (regression gate before building anything new).
2. Add `find_candidate_pause`, `snap_boundary`, `build_report`, and the CLI
   entry point to `work/clip_cutter.py`.
3. Run `clip_cutter.py` for both candidates' start/end rough windows from
   section 3; record the snapped times and confidence per boundary.
4. Cut `clip06...` and `clip07...` raw clips at the snapped times (reuse the
   `ffmpeg -ss ... -to ... -c:v libx264 ...` pattern from `recut.py`).
5. Write spell-checked, clip-relative subtitles and titles for both (following
   `build_all.py`'s `REELS` list pattern), build the two reels via
   `overlays_lib.py` + the existing ffmpeg filter-graph pattern (PNG overlays
   only — no drawtext), including the watermark.
6. Write `.caption.txt` sidecars for both (title/description/hashtags,
   following the existing 5 reels' format).
7. Run `check_reel.py` on both finished reels with `--vtt`, `--src-start`,
   `--src-end` set to the snapped boundaries; resolve any FAIL, review any
   WARN by reading the caption text at the boundary.
8. Extract and visually sanity-check a couple of preview frames per reel
   (legible captions, watermark present, no collisions).
9. Apply the STYLE.md / steering file rule additions from section 4 to both
   files.
10. Leave the upload-readiness note from section 5. Do not call the uploader.
