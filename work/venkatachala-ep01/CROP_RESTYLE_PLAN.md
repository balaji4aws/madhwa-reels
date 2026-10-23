# Implementation Plan — Crop-based reframe + single-line subtitles (all 7 reels)

Scope recap (from the approved task brief): replace the blurred-mirror-fill
reframe with a direct crop centered on the speaker (scaled-mirror fill for
any leftover margin is fine), replace reel 01's build-up names list with
single-line subtitles, re-verify `SUB_Y` / watermark Y against the new crop,
rebuild+verify all 7 reels, clean up only after verification, and update the
4 doc files. Content/cut points (title text, clip choice, source timestamps)
are NOT to change — only the visual composition.

This project folder is **not a git repo** — no git operations at any step.

## Grounding already done (do not re-derive these facts)

- Source: `sources/venkatachala-ep01/source.mp4`, **1920x1080, 25fps**
  (confirmed via `ffprobe`). Speaker (swamiji) sits centered horizontally,
  roughly x≈820–1260 for head/shoulders at the sampled timestamps.
- `work/venkatachala-ep01/reframe_scratch/` and `reframe_scratch2/` contain
  **prior, unfinished manual exploration** (no script produced them — not
  referenced by any current build script) of crop x-offsets (tested x=600,
  650, 700, 716) and `SUB_Y` candidates (1280, 1420, 1500, 1560) against
  extracted frames at source t=140, 300, 780, 1105, 1140, 1230, 1260s.
  Inspecting `test_x716.png`, `test1260_x716.png`, and
  `composite_suby_1500.png` from these folders shows:
  - A **1080-wide x 1080-tall crop at x-offset ≈716** (i.e. `crop=1080:1080:716:0`
    on the 1920x1080 source), then scaled to 1080x1920, frames the swamiji's
    head+torso well with headroom above the hairline and crops the source's
    own bottom banner (website/social strip) out of frame entirely — exactly
    the deliberate banner-crop reversal the brief approves.
  - `SUB_Y≈1500` lands a subtitle pill cleanly on the robe/chest area, clearly
    below the chin, in both sampled frames.
  - These are **useful starting hypotheses only** — they were never wired
    into a build script, never checked across all 7 reels' actual framing
    (camera framing may differ slightly reel to reel since clips come from
    different points in a 21-minute static-camera talk), and never checked
    against the title card / watermark stack. Treat them as the first
    candidate to test, not a final answer — re-verify with freshly extracted
    frames once the shared crop function exists, per section (e) below.
  - These scratch folders are pre-existing clutter from an earlier abandoned
    attempt — leave them alone for now; they are named as deletion
    candidates in section (f) once the new build is verified (not before).
- `overlays_lib.py` already renders `render_title`/`render_sub` as Pillow
  PNGs (W=1080, H=1920, `SUB_Y=1280` currently) — reused as-is per the brief;
  only its reframe logic needs a new shared function.
- `assets/make_watermark.py` hardcodes the watermark text at **y=1840** on a
  full 1080x1920 transparent canvas (`assets/watermark.png`) — this, not
  STYLE.md's approximate "~y1700" prose, is the actual current value to
  re-verify.
- All 4 build scripts (`build_reel01_v2.py`, `build_all_v2.py` for reels
  02–05, `build_reel06.py`, `build_reel07.py`) currently use the **identical**
  blurred-fill filter fragment:
  ```
  [0:v]split=2[sv0][sv1];
  [sv0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2,eq=brightness=-0.18[bg];
  [sv1]scale=1080:-2[fg];
  [bg][fg]overlay=(W-w)/2:(H-h)/2[base];
  ```
  This confirms the brief's refactor concern is real: 4 copies of the same
  logic to replace with one shared function.
- Exact clip files and source timestamps already recorded in the scripts /
  `cut_report_06.json` / `cut_report_07.json` (reused verbatim, see table in
  section (c)).

## This work does NOT decompose into independent FEAT artifacts

All 7 reels must share one crop function and one verified `SUB_Y`/watermark-Y
pair, chosen and sanity-checked together so every reel looks consistent on
the channel. Splitting per-reel into isolated parallel features would risk
7 different crop numbers or a frame-inspection step done only once and
assumed to generalize. This stays a single ordered plan for one coding loop.

---

## (a) Shared crop function — add to `overlays_lib.py`

Add one new function, used by all 4 build scripts in place of each one's
copy-pasted `[sv0]...boxblur...` / `[sv1]...` / `overlay=(W-w)/2:(H-h)/2`
fragment:

```python
def crop_reframe_filter(src_label="0:v", crop_w=1080, crop_h=1080,
                         crop_x=716, crop_y=0, fill_mode="mirror_blur"):
    """Return an ffmpeg filter_complex fragment (as a string, no trailing
    semicolon-free dangling label) that reframes a 1920x1080 horizontal
    source into the 1080x1920 vertical canvas by CROPPING a vertical slice
    centered on the speaker, not blur-filling the whole frame.

    - Crops a `crop_w` x `crop_h` window at (crop_x, crop_y) out of the
      1920x1080 source, then scales it to 1080 width, preserving aspect
      (crop_h determines how tall the sharp video ends up before any
      leftover margin is filled).
    - If the scaled sharp crop is shorter than 1920 (leftover margin above/
      below), fills the leftover with a blurred, scaled-up mirror of the
      FULL original frame (not the crop) cropped to 1080x1920 and boxblurred
      -- same visual fallback already in use today, just demoted from "the
      whole background" to "leftover-margin filler only". If crop_h is tall
      enough that the scaled crop already reaches or exceeds 1920, the fill
      layer is skipped entirely (sharp crop is the whole frame, no blur
      visible).
    - Output label: `[reframed]`.

    Returns the filter string; caller appends it into their own
    filter_complex and continues the chain from `[reframed]`.
    """
```

Design decisions (made now, not left for the coder to re-decide):

- **Why crop_w=1080, crop_h=1080 as the function's default, not a fixed
  "always crop to exactly 1920 tall":** the source is only 1080px tall, so a
  1080-tall crop scaled 2x to fill 1920 vertically is the natural "crop as
  much height as exists, then scale up" choice — this matches what the
  scratch exploration already tested (`test_x716.png`, `test_crop_full_h.png`)
  and gives the sharp video the WHOLE frame (no visible blur margin at all)
  once scaled, which best satisfies "speaker fills most of the frame, not a
  small box inside a big blur frame." Keep `crop_h` as a parameter (not
  hardcoded) so a reel whose framing needs a narrower/taller slice can
  override it, but default both the function's default and every call site
  in this task to the same confirmed value once frame inspection confirms it
  — per-reel divergence should be the exception, not the norm, so all 7
  reels look consistent.
- **Why a function parameter per reel, not a single hardcoded constant
  inside the function:** different clips in this source were filmed from the
  same static camera position (confirmed: all `clipNN*.mp4` files are cut
  from one unmoving 21-min talk), so `crop_x`/`crop_y` are expected to be the
  SAME across all 7 reels — but the function must still accept them as
  parameters (not bake in a constant) so a future different source video, or
  a reel where the frame inspection in (b) reveals the swamiji shifted
  slightly, can override without editing shared code. Default values should
  equal whatever this task's frame inspection confirms (see (b)).
- **Fill mode:** implement exactly one fill mode now (`mirror_blur` — scaled
  mirror of the full frame, blurred, per the brief's explicit approval of
  "scaled mirror is also fine") rather than building a solid-color option
  that's not needed yet; don't over-build.
- Keep the function pure string-building (matches the existing style of
  `render_title`/`render_sub` returning paths / the build scripts building
  `fc` as a string) — no new dependencies, no behavior change to
  `render_title`/`render_sub` themselves.

**Files:** `work/venkatachala-ep01/overlays_lib.py` (add the function; do not
remove or alter `render_title`, `render_sub`, `_font`, `_center`, `_band`,
`_wrap`, `W`, `H`, `ACCENT`, `WHITE`, `FONT_BOLD`, `FONT_GEO_BOLD`, or
`SUB_Y` in this step — those are touched in step (d) only).

**Verify:** `python3 -c "from overlays_lib import crop_reframe_filter; print(crop_reframe_filter())"`
run from `work/venkatachala-ep01/` prints a non-empty filter string with no
Python error. This is a syntax/import smoke check only — real verification
of the crop's visual correctness happens in steps (b)/(e) by looking at
actual rendered frames, not by reading the string.

---

## (b) Initial crop-coordinate hypothesis — verify with real frames before use

**Do not hardcode numbers into any build script until this step's frame
inspection confirms them.** The scratch-folder hypothesis is a starting
point, not a conclusion.

1. Extract one frame per reel from each reel's OWN clip file (not just the
   full source) at early/mid/late points of that specific clip, e.g.:
   ```
   ffmpeg -y -ss <t> -i clipNN_xxx.mp4 -frames:v 1 work/venkatachala-ep01/_probe_NN_<t>.png
   ```
   for `t` at roughly 10%, 50%, 90% of each clip's duration. This checks
   whether the swamiji's framing (head position, how far into frame he
   leans) is consistent across all 7 clips, since they come from different
   points in a 21-minute talk and he may shift posture/lean between clips.
2. Starting hypothesis to test first (from the scratch-folder exploration):
   `crop_w=1080, crop_h=1080, crop_x=716, crop_y=0` on the 1920x1080 source.
   Render this crop (scaled to 1080x1920) against each probed frame using
   Pillow (`Image.crop((716,0,716+1080,1080)).resize((1080,1920))`) — faster
   to iterate on than running ffmpeg per candidate — and look at the result.
3. Accept criteria per probed frame: top of head not clipped (some headroom
   above hairline), face/chin not clipped at any edge, source's bottom
   banner strip fully outside the crop, composition doesn't feel like an
   awkward too-tight close-up (some chest/robe visible below the chin).
4. If any reel's probed frames fail these criteria at `crop_x=716`, adjust
   `crop_x` (and only if necessary `crop_y`/`crop_h`) for that reel and
   re-check — this is the "couple of tries" iteration the brief expects.
   Prefer keeping ONE shared `(crop_x, crop_y, crop_w, crop_h)` across all 7
   reels if it works for all of them (simpler, consistent look); only let an
   individual reel override if its probed frames genuinely need it.
5. Record the final confirmed numbers (and which frames were checked) — this
   is required content for the final report and for updating
   `.kiro/steering/madhwa-reels.md` / `docs/STYLE.md` in step (g).

**Files created (temporary, by hand, not committed to any script):**
`work/venkatachala-ep01/_probe_*.png` — delete these once the crop numbers
are confirmed and wired into the build scripts (they are throwaway
inspection images, not reusable artifacts — covered by cleanup in (f), named
exactly since they share the `_probe_` prefix added in this step).

**Verify:** no automated check here — this step's output is a human-reviewed
visual confirmation (view each candidate crop image directly) and a written
note of the confirmed `(crop_x, crop_y, crop_w, crop_h)` to carry into (c).

---

## (c) Per-reel build script changes — exactly what changes, what stays fixed

Apply the SAME two changes to every script: (1) replace the copy-pasted
blurred-fill fragment with a call to `crop_reframe_filter(...)` from (a)
using the numbers confirmed in (b), (2) for reel 01 only, replace the
multi-line names-band build-up with single-line `render_sub` calls carrying
the same four-names content. Nothing else in any script changes.

| # | Script | Clip file (unchanged) | Source timestamps (unchanged, reused as-is) | Title text (unchanged) | What changes |
|---|--------|------------------------|----------------------------------------------|--------------------------|----------------|
| 01 | `build_reel01_v2.py` | `clip01_names_v2.mp4` | 136.48–152.88s (16.4s) | "The 4 Names of" / "Venkatachala" | Replace `build_names_png`/`ov01_names_*.png` build-up band entirely with 4 single-line `render_sub` cues carrying the same Yuga↔name content (one line at a time, timed to the existing `NAME_REVEAL_T` mention points `7.6/9.8/11.5/13.4` already in the script — reuse those timestamps as the new single-line subtitle cue boundaries instead of re-timing from scratch); keep the existing 4 spoken-word `subs` cues (0.2–16.2s) as-is since they already convey the same sentence; apply `crop_reframe_filter`. |
| 02 | `build_all_v2.py` (REELS[0]) | `clip02_senses_v2.mp4` | 295.44–328.00s (32.56s) | "Offer your head to God?" / "What it really means" | Only the reframe fragment → `crop_reframe_filter`. Subtitles already single-line; no change. |
| 03 | `build_all_v2.py` (REELS[1]) | `clip03_anjana_v2.mp4` | 776.27–805.84s (29.57s) | "Why is it called" / "Anjanachala?" | Only the reframe fragment. |
| 04 | `build_all_v2.py` (REELS[2]) | `clip04_shesha_v2.mp4` | 1101.44–1128.26s (26.82s) | "Seshachala's lesson:" / "Never be arrogant" | Only the reframe fragment. |
| 05 | `build_all_v2.py` (REELS[3]) | `clip05_venkata_v2.mp4` | 1227.20–1250.03s (22.83s) | "Why Venkatachala" / "burns away sins" | Only the reframe fragment. |
| 06 | `build_reel06.py` | `clip06_sinner-purified.mp4` | 1135.05–1167.72s (32.67s) | "The sinner who was" / "purified" | Only the reframe fragment. |
| 07 | `build_reel07.py` | `clip07_lose-your-ego.mp4` | 1251.157–1283.527s (32.4s) | "Lose Your" / "Ego" | Only the reframe fragment. |

Implementation note for the reframe swap (applies identically in all 4
files): replace
```
"[0:v]split=2[sv0][sv1];"
"[sv0]scale=1080:1920:force_original_aspect_ratio=increase,"
"crop=1080:1920,boxblur=20:2,eq=brightness=-0.18[bg];"
"[sv1]scale=1080:-2[fg];"
"[bg][fg]overlay=(W-w)/2:(H-h)/2[base];"
```
(and the one subsequent line that overlays the title onto `[base]`/`[v0]`)
with the string returned by `crop_reframe_filter(...)`, output label
`[reframed]`, then continue the existing chain's next overlay starting from
`[reframed]` instead of `[base]`/`[v0]` — every later overlay step (subs,
title, watermark, and for reel01 the names-band-turned-single-line-subs)
stays structurally the same, just re-based on the new label.

Reel 01's names-band replacement specifically: delete `build_names_png`,
`names`, `row_h`, `top_y`, `band_pad`, and the `ov01_names_*.png` generation
loop; delete `NAME_REVEAL_T`; add 4 new `render_sub` calls (reusing
`overlays_lib.render_sub`, already imported) with text content:
`"Krita Yuga — Vrishabhachala"`, `"Treta Yuga — Anjanachala"`,
`"Dwapara Yuga — Seshachala"`, `"Kali Yuga — Venkatachala"`, timed at the
same 4 windows the old reveal used (`[0.2,7.6]` effectively absorbed into the
existing first-sentence subs, then `[7.6,9.8]`, `[9.8,11.5]`, `[11.5,13.4]`,
`[13.4,16.2]` for the four name lines) so the four-names content is still
fully conveyed, just one line at a time instead of a growing list. Keep the
existing 4 "spoken narration" subs cues unchanged — the new name-reveal subs
run in addition to (after) them, same structure every other reel already
uses (narration subs, not simultaneous with a separate band).

**Files:** `work/venkatachala-ep01/build_reel01_v2.py`,
`work/venkatachala-ep01/build_all_v2.py`,
`work/venkatachala-ep01/build_reel06.py`,
`work/venkatachala-ep01/build_reel07.py`, importing the new function from
`work/venkatachala-ep01/overlays_lib.py` (already imported as a module in
all 4 — just add `crop_reframe_filter` to each file's existing `from
overlays_lib import ...` line).

**Verify:** run each script (`python3 build_reel01_v2.py`,
`python3 build_all_v2.py`, `python3 build_reel06.py`,
`python3 build_reel07.py`, from inside `work/venkatachala-ep01/`) and confirm
each prints its "Built ..." success line, not "FAILED" — this confirms the
ffmpeg filter graph is syntactically valid and the encode completes. Visual
correctness is checked separately in (e).

---

## (d) `SUB_Y` / watermark-Y re-check plan

1. After (b) confirms the final crop numbers but BEFORE rebuilding all 7
   reels in (c), render one real composite test frame: take a probe frame
   from step (b), apply the confirmed crop, and overlay a test `render_sub`
   PNG (at the current `SUB_Y=1280`) and the actual `assets/watermark.png`
   (current y=1840) on top, the same way `reframe_scratch2/composite_suby_*`
   did. Look at it directly.
2. If `SUB_Y=1280` or watermark y=1840 overlaps the face or (ideally) the
   torso under the NEW tighter crop, test the scratch-confirmed alternative
   `SUB_Y=1500` (and if needed, a correspondingly adjusted watermark y, kept
   far enough below the subtitle pill to avoid colliding with it) against
   the same probe frames. Pick the smallest change that clears the face
   (and torso where there's clear margin) — don't move either further than
   needed, since STYLE.md's existing safe-zone intent (nothing critical in
   the bottom ~280px / against the right edge, platform UI clearance) must
   still hold at whatever new Y is chosen.
3. Update `SUB_Y` in `overlays_lib.py` (single constant, used by
   `render_sub`) and the watermark y in `assets/make_watermark.py` to the
   confirmed final values — re-run `make_watermark.py` to regenerate
   `assets/watermark.png` if its y changes.
4. Re-confirm after the full rebuild in (c)/(e) using the REAL rendered
   reels' own preview frames, not just the isolated composite test — the
   isolated test in step 1 is a fast pre-check, not the final confirmation.

**Files:** `work/venkatachala-ep01/overlays_lib.py` (`SUB_Y` constant only),
`assets/make_watermark.py` (the `y = 1840` line, only if changed) and the
regenerated `assets/watermark.png`.

**Verify:** the composite test image in step 1 and the real preview frames
in step 4 are reviewed directly (no automated check for visual overlap
exists in this project — matches the existing `check_reel.py` scope, which
has no face-overlap check); state in the final report exactly which frames
were looked at and confirm no overlap, per reel.

---

## (e) Verification plan — all 7 reels

For each reel, after rebuilding in (c):

1. **Run `check_reel.py`** with the SAME `--src-start`/`--src-end`/`--vtt`
   arguments each reel's build script or `cut_report_*.json` already
   documents (reuse, do not re-derive):
   - 01: no stored cut_report; the script's own docstring gives
     `--src-start 136.48 --src-end 152.88`.
   - 02: `--src-start 295.44 --src-end 328.00`.
   - 03: `--src-start 776.27 --src-end 805.84`.
   - 04: `--src-start 1101.44 --src-end 1128.26`.
   - 05: `--src-start 1227.20 --src-end 1250.03`.
   - 06: `--src-start 1135.05 --src-end 1167.72`.
   - 07: `--src-start 1251.157 --src-end 1283.527`.
   All runs: `--vtt ../../sources/venkatachala-ep01/source.en.vtt
   --subs-json <a-json-file-of-that-reel's-subtitle-text-list>` (write one
   small throwaway `_subs_NN.json` per reel from each script's existing
   `subs`/`REELS[i]["subs"]` list — first element of each tuple — purely to
   satisfy `check_reel.py`'s required `--subs-json` argument; these are
   scratch, name them `_subs_01.json`...`_subs_07.json` and delete after
   verification per (f)).
   Command form (run from `work/venkatachala-ep01/`):
   ```
   python3 check_reel.py ../../reels/venkatachala-ep01_0N_<topic>.mp4 \
     --subs-json _subs_0N.json \
     --vtt ../../sources/venkatachala-ep01/source.en.vtt \
     --src-start <S> --src-end <E>
   ```
2. **Extract 3–4 preview frames per reel** (early/mid/late, e.g. at 10%,
   40%, 70%, 90% of duration):
   ```
   ffmpeg -y -ss <t> -i ../../reels/venkatachala-ep01_0N_<topic>.mp4 -frames:v 1 _preview_0N_<t>.png
   ```
3. **Look at each extracted preview frame directly** and confirm:
   - Speaker fills most of the frame top-to-bottom (not boxed into a small
     letterboxed strip).
   - Subtitle is single-line (no build-up list visible anywhere, including
     reel 01) and does not overlap the face.
   - Watermark does not overlap the face.
   - Nothing looks broken/glitchy: no clipped-off top of head, no awkward
     too-tight close-up with missing context.
4. If a reel's frames fail any check in step 3, go back to (b)/(c) and
   iterate the crop numbers for that reel specifically (expected to take a
   couple of tries per the brief) — re-run steps 1–3 after any fix.
5. Record, per reel, in the final report: final duration (from
   `check_reel.py`'s dimensions/duration line), the PASS/WARN/FAIL lines it
   printed, and a short confirmation that preview frames were reviewed and
   looked correct (or what was fixed if not, on the first pass).

**Files created (temporary):** `work/venkatachala-ep01/_subs_0N.json`,
`work/venkatachala-ep01/_preview_0N_<t>.png` for N=1..7 — all named with the
`_subs_`/`_preview_` prefix so they're easy to name exactly in cleanup (f).

**Verify:** `check_reel.py` exit code and printed PASS/WARN/FAIL lines per
reel (expect dimension PASS 1080x1920 on all 7; duration WARN only if a reel
exceeds 60s, none currently do; odd-cut WARN on the already-known
run-on-cue false positives is expected and acceptable per STYLE.md, not a
blocker) plus the direct visual review in steps 2–3.

---

## (f) Cleanup candidates — name exact files, only after verify, never a wildcard

**Do not delete anything until ALL 7 reels have passed the full check in
(e).** Once verified, these exact files are safe to remove (per
`docs/STYLE.md`'s work-folder cleanup policy — superseded/duplicate overlay
output and one-off scratch, not reusable logic or the audit-trail JSONs):

- **This task's own throwaway probe/preview/subs-json files**, named
  exactly, e.g.: `work/venkatachala-ep01/_probe_01_*.png`,
  `work/venkatachala-ep01/_probe_02_*.png`, ... `_probe_07_*.png`,
  `work/venkatachala-ep01/_subs_01.json` ... `_subs_07.json`,
  `work/venkatachala-ep01/_preview_01_*.png` ... `_preview_07_*.png` (the
  exact filenames depend on the timestamps actually used when they're
  created in (b)/(e) — list the literal filenames that exist at that point
  before deleting, do not glob `_probe_*`/`_preview_*`).
- **The pre-existing abandoned scratch folders**, now fully superseded by
  this task's own (newer, verified) crop numbers:
  `work/venkatachala-ep01/reframe_scratch/` and
  `work/venkatachala-ep01/reframe_scratch2/` — list every file inside each
  by its exact name before deleting (both folders' contents were already
  enumerated during this plan's exploration: `reframe_scratch/` has
  `composite_new_suby.png`, `composite_old_suby.png`,
  `composite_watermark_actual.png`, `face_crop.png`, `final_1140.png`,
  `final_1140_grid.png`, `ov_sub_98.png`, `ov_sub_99.png`, `src_1105.png`,
  `src_1140.png`, `src_1140_grid.png`, `src_1230.png`, `src_1260.png`,
  `src_1260_grid.png`, `src_140.png`, `src_140_grid.png`, `src_300.png`,
  `src_780.png`, `test_crop_1230.png`, `test_crop_140.png`,
  `test_crop_300.png`, `test_crop_780.png`, `test_crop_full_h.png`;
  `reframe_scratch2/` has `composite_suby_1280.png`, `composite_suby_1420.png`,
  `composite_suby_1500.png`, `composite_suby_1560.png`, `ov_sub_2180.png`,
  `ov_sub_2320.png`, `ov_sub_2400.png`, `ov_sub_2460.png`, `raw_1140.png`,
  `raw_1260.png`, `raw_140.png`, `test1260_x716.png`, `test140_x716.png`,
  `test_x600.png`, `test_x650.png`, `test_x700.png`, `test_x716.png` — then
  the two now-empty directories themselves). Re-confirm this exact list with
  a directory listing immediately before deleting, in case anything changed.
- **`__pycache__/`** — safe to delete per STYLE.md, named as the directory
  itself (`work/venkatachala-ep01/__pycache__/`), not a wildcard.

**Explicitly NOT deleted** (per STYLE.md's "must keep" / "keep for now"
policy, unaffected by this task): all `clipNN*.mp4` raw clips (still the
fastest path to re-cut if a reel needs revision later), `cut_report_06.json`
/ `cut_report_07.json` (audit trail), all `build_*.py` / `overlays_lib.py` /
`check_reel.py` (reusable logic, now updated not removed), `reels/*.mp4` and
`reels/*.caption.txt` (the deliverable), `sources/venkatachala-ep01/*`
(source + captions, still needed — more reels aren't ruled out from this
talk).

**Files:** exact deletions listed above, executed only with explicit
filenames (no `rm -rf dir/*`, no glob) — state the final literal list again
immediately before running the delete, per `docs/GUARDRAILS.md`.

**Verify:** `ls work/venkatachala-ep01/` and
`ls work/venkatachala-ep01/reframe_scratch* 2>&1` after deletion — confirm
the listed files/folders are gone and nothing else in the directory changed
unexpectedly (same "verify the blast radius" caution `docs/CHANGELOG.md`'s
2026-10-22 incident entry already established as standard practice here).

---

## (g) Doc updates — exactly 4 files, what changes in each

1. **`docs/STYLE.md`**
   - Rewrite the "Reframe" bullet under "Visual style (the house look)":
     replace "blurred, scaled-up copy of the source fills the 9:16 frame as
     the background; the original (letterboxed) video is centered sharp on
     top. Never a hard crop that cuts off the speaker." with the new
     crop-based description (crop centered on speaker fills most of the
     frame; scaled-mirror-blur fill only for leftover margin; state the
     final confirmed `crop_x`/`crop_y`/`crop_w`/`crop_h` from (b)).
   - Rewrite the "Lower-third / lists" bullet: remove "build-up reveal (one
     line at a time) when listing multiple items"; state single-line
     subtitles only, reusing `render_sub`, no multi-line reveal band
     anywhere including reel 01.
   - Update "Source handling"'s banner rule: replace "Leave it — do not crop
     it out or cover it" with an explicit statement that the banner MAY now
     be cropped out of frame, and that this is a deliberate reversal of the
     earlier rule, confirmed by the channel owner.
   - Update "Safe zones" Y-coordinates (`SUB_Y`, watermark y) to the final
     values confirmed in (d), if they changed from 1280/1840.
   - Per `docs/GUARDRAILS.md`, this is an explicitly user-approved rule
     change (the task brief itself), not a unilateral edit — proceed
     directly, no additional confirmation needed beyond what the brief
     already grants.

2. **`.kiro/steering/madhwa-reels.md`**
   - Update the existing "## Reframe style (as of 2026-10...)" section:
     change its heading/status to mark it **IMPLEMENTED** (not pending), and
     replace the descriptive bullets with the final actual numbers (crop
     params, `SUB_Y`, watermark y) rather than the current prose-only
     description. Remove or rewrite the closing sentence ("This reframe/
     subtitle change was still being implemented... check CHANGELOG.md for
     whether it's been built") since it will no longer be accurate.
   - Also update the "Every reel must have" section's item 2 ("Blurred-fill
     reframe... never a hard crop") — this is the OLDER, now-superseded
     summary elsewhere in the same file and would otherwise contradict the
     updated "Reframe style" section below it.

3. **`docs/CHANGELOG.md`**
   - Append exactly ONE new dated entry (use today's actual date — check the
     system date when writing it, do not reuse 2026-10-24 or guess) covering:
     what changed (crop-based reframe + single-line subtitles, all 7 reels),
     why (user's explicit feedback + the 3 reference YouTube Shorts
     screenshots rejecting the letterboxed blurred-fill look, and the
     separate dislike of reel 01's build-up names list), the old approach's
     problem (under-uses the vertical frame, looks like a letterboxed clip
     with blurred bars), what was tried for crop coordinates (reference the
     pre-existing abandoned `reframe_scratch`/`reframe_scratch2` exploration
     as the starting hypothesis, then this task's own frame-by-frame
     verification per reel and any per-reel adjustments needed), and the
     final verified result (numbers + per-reel check_reel.py outcomes).
   - Do not edit or remove any existing entry — append only, at the bottom.

4. **`docs/SOURCES.md`**
   - Update the `venkatachala-ep01 — reel detail` sub-table's `Status`
     column for all 7 rows to reflect the rebuild, e.g. "Rebuilt in new
     crop/single-line style, verified — not yet uploaded" (keep "not yet
     uploaded" where still true — this task does not touch upload, per
     `docs/GUARDRAILS.md`'s scope rule).
   - Update the top-level table's `Status` cell for `venkatachala-ep01` from
     "In progress — styling being revised" to reflect completion of the
     style revision (e.g. "Styling revised — ready for upload"), since this
     is the task that was pending.
   - Leave reel 01's "upload history" note as-is (upload/test-title history
     is a separate, already-accurate record unrelated to this visual
     restyle).

**Files:** `docs/STYLE.md`, `.kiro/steering/madhwa-reels.md`,
`docs/CHANGELOG.md`, `docs/SOURCES.md`.

**Verify:** no build/test command applies to markdown docs — verify by
re-reading each edited file after writing and confirming: (1) STYLE.md no
longer describes blur-fill-as-background or build-up lists anywhere, (2) the
steering file's "Reframe style" section reads as IMPLEMENTED with concrete
numbers and the older "Every reel must have" item 2 no longer contradicts
it, (3) CHANGELOG.md has exactly one new dated section appended with no
existing section altered, (4) SOURCES.md's reel-detail table has all 7
status cells updated and the top-level status cell updated.

---

## Required final report (carry forward into the implementation's own report)

- Exact final crop filter-graph logic (the `crop_reframe_filter(...)` call
  site arguments used in all 7 scripts) + reasoning for the coordinates
  chosen, grounded in which probe frames were checked.
- Exact final `SUB_Y` and watermark Y, confirmation neither overlaps the
  face in the reviewed frames, naming which frames.
- Per-reel (all 7): final duration, `check_reel.py` PASS/WARN/FAIL summary,
  confirmation preview frames were reviewed and looked correct.
- Exact list of old files deleted (if any) and why — copy the literal list
  from (f) as actually executed.
- Confirmation all 4 doc files were updated as specified in (g).
- Any genuine open question for the user (e.g. if a reel's framing couldn't
  converge on the shared crop numbers and needed a materially different
  override), clearly separated from the routine choices already made in
  this plan.
