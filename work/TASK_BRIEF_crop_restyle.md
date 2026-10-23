# Task brief: crop-based reframe + single-line subtitles for all 7 reels

Project folder: /Users/venkyb/Documents/balaji4aws/madhwa reels/ (NOT a git
repo — do not attempt any git operations).

## Context to read first

- README.md (overview)
- docs/STYLE.md (current rules — update once new style is built/verified)
- docs/WORKFLOW.md (pipeline steps)
- docs/GUARDRAILS.md (never-do rules — follow strictly)
- docs/SOURCES.md (update status column once rebuilt)
- docs/CHANGELOG.md (append ONE new dated entry; never edit old entries)
- /Users/venkyb/Documents/balaji4aws/.kiro/steering/madhwa-reels.md (has a
  "Reframe style (as of 2026-10...)" section describing the NEW rules this
  task implements — use as spec, then mark IMPLEMENTED not pending)

## Background

Source video already downloaded: sources/venkatachala-ep01/source.mp4 (+
.en.vtt + .kn.vtt). 7 reels already built (not yet uploaded) from it:
work/venkatachala-ep01/ has build_reel01_v2.py, build_all_v2.py (builds
reels 02-05), build_reel06.py, build_reel07.py, overlays_lib.py (shared
renderer), check_reel.py (checker), clip01_names_v2.mp4..clip07*.mp4 (raw
clips), cut_report_06.json, cut_report_07.json (audit trail).
reels/venkatachala-ep01_01_four-names.mp4 through _07_lose-your-ego.mp4 (+
.caption.txt sidecars).

## Task — confirmed, approved style change (user explicitly approved every
point; do not re-litigate, implement)

**1. REFRAME.** Stop blurred-mirror-fill-the-whole-16:9-frame (current
approach: scale+crop+boxblur as background, small sharp 1080-wide copy
centered on top — looks like a letterboxed clip with blurred bars, which
the user explicitly rejected after sharing 3 reference YouTube Shorts
screenshots). NEW: crop a vertical slice directly out of the horizontal
source, centered on the speaker, so he fills MOST of the 1080x1920 frame
top-to-bottom. A scaled/blurred mirror fill for any leftover margin is
fine (user said so explicitly) — point is the sharp cropped video must
dominate, not be a small box inside a big blur frame. The source's own
baked-in channel banner MAY be cropped out of frame now (user explicitly
confirmed this reverses the old "never crop the banner" rule — state this
clearly in STYLE.md as a deliberate reversal). Inspect actual frames to
pick good crop coordinates for this specific source's framing, don't guess
blindly.

**2. SUBTITLES.** Stop any build-up/multi-line-reveal style (reel 01's
"names list" growing line by line). User: "I always like a single-line
subtitle style rather than build-up list that grows too big." NEW: one
subtitle line visible at a time, matching the single-line style already
used in reels 02-07 (overlays_lib.py's render_sub — keep that, reuse it).
Reel 01 needs its multi-line names band replaced with single-line
subtitles conveying the same four-names content one line at a time.
Re-verify SUB_Y (currently 1280) and the watermark's Y against the NEW
tighter crop — old subtitle band landed ON the speaker's body in the old
layout; with more of the frame filled by the crop, re-check so neither
subtitle nor watermark ever overlaps the face (ideally not the torso
either, if there's a clear margin after cropping). Use actual extracted
frames to verify, don't just pick a number and assume.

**3. APPLY to all 7 reels.** Rebuild reels 01-07 with the new
reframe+subtitle approach, reusing each existing script's CONTENT decisions
(title text, which clip, which source timestamps) unchanged — only change
the VISUAL composition (reframe + subtitle rendering), not the cut points
or moment selection. Refactor overlays_lib.py so the new crop logic is one
shared function, not copy-pasted across the 4+ build scripts (this project's
standing principle: shared logic lives in one module — see tools/
clip_cutter.py's rationale in CHANGELOG.md for the established pattern).

**4. VERIFY all 7.** Run check_reel.py on each (reuse each reel's existing
--src-start/--src-end from cut_report_*.json / build script comments — do
not re-derive cut timestamps). Extract 3-4 actual preview frames per reel
(early/mid/late) and LOOK AT THEM: speaker fills most of the frame (not
boxed into a letterboxed strip), subtitle is single-line and never
overlaps the face, watermark doesn't overlap the face, nothing looks
broken/glitchy (e.g. crop cutting off the top of the head, or showing an
awkward close-up with no context). If the first crop attempt looks wrong,
iterate on the coordinates — expected to take a couple of tries.

**5. CLEAN UP.** Once a reel is rebuilt+verified in the new style, old
now-superseded raw clips / overlay PNGs from the old style can be deleted
per the work-folder cleanup policy already in STYLE.md — but only AFTER the
new version is verified good, and name exact files (never a wildcard,
per GUARDRAILS.md). State exactly what's being deleted and why, before
deleting.

**6. UPDATE DOCS (required).**
- docs/STYLE.md: rewrite "Reframe" bullet (crop-based, not blurred-fill),
  rewrite "Lower-third / lists" bullet (single-line subtitles only, no
  build-up list), update "Source handling" banner rule (confirmed reversal:
  banner may now be cropped out), update safe-zone Y-coordinates if changed.
- .kiro/steering/madhwa-reels.md: update the existing "Reframe style"
  section to IMPLEMENTED with final actual numbers.
- docs/CHANGELOG.md: ONE new dated entry (today's actual date) — what
  changed, why (user's feedback + reference screenshots), old approach's
  problem, what was tried for crop coordinates and what worked, final
  verified result. Never edit/remove existing entries.
- docs/SOURCES.md: update venkatachala-ep01's reel-detail status column
  for all 7 reels (e.g. "Rebuilt in new crop/single-line style, verified").

## Constraints (from docs/GUARDRAILS.md — follow strictly)

- Do NOT touch the live YouTube channel (no upload/--delete/--replace/
  --set-privacy) — local build/style task only.
- Do NOT delete any file with a wildcard — name exact filenames always.
- Do NOT guess Sanskrit/Madhwa spellings — only use tools/sanskrit_terms.py;
  flag any genuinely new term rather than inventing a spelling.
- Do NOT change any STYLE.md rule beyond what's explicitly described here.
- Personal, non-commercial devotional project, no IP/trademark conflict —
  proceed directly with these already-approved decisions; only flag back a
  genuine open question outside this scope, not routine implementation
  choices.

## Required final report

- Exact final crop filter-graph logic (ffmpeg crop parameters + reasoning
  for the coordinates chosen).
- Exact final SUB_Y and watermark Y, confirmation neither overlaps the
  face (cite which preview frames were checked).
- Per-reel (all 7): final duration, check_reel.py PASS/WARN/FAIL summary,
  confirmation preview frames were reviewed and looked correct.
- Exact list of old files deleted (if any) and why.
- Confirmation all 4 doc files were updated as specified.
- Any genuine open question for the user, clearly separated from routine
  choices already made.
