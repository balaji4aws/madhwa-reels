# Lessons Learned — Madhwa Reels Workflow

Append-friendly log. Each session/task adds a new dated section below; do not
overwrite or remove earlier entries. Newest entries go at the bottom unless
noted otherwise.

---

## 2026-10-24 — Folder reorg: `artifacts/` → `docs/`, shared tools → `tools/`

The human-facing docs folder was renamed from `artifacts/` to `docs/` at the
user's request, and the shared cut-boundary/transcription tools (previously
loose files directly under `work/`) were moved into a new `tools/` folder,
separate from the per-video scratch in `work/<slug>/`. All path references in
this file, `STYLE.md`, `README.md`, and the per-slug build scripts were
updated to match (`work/clip_cutter.py` → `tools/clip_cutter.py`,
`work/transcribe.py`/`work/transcribe.venv` → `tools/transcribe.py`/
`tools/transcribe.venv`, `artifacts/STYLE.md` → `docs/STYLE.md`, etc.). The
entries below predate this rename and use the OLD paths in their prose —
left as-is since they're a historical record of what was true at the time;
read `work/clip_cutter.py` below as `tools/clip_cutter.py` at its current
location, and `artifacts/STYLE.md`/`artifacts/LESSONS.md` as `docs/STYLE.md`/
`docs/LESSONS.md`.

---

## 2026-10-22 — Building a reusable cut-boundary tool (`work/clip_cutter.py`,
now at `tools/clip_cutter.py`)

**Context:** reels 01–05 were cut with `work/venkatachala-ep01/recut.py`, a
script with a hand-typed `CUTS` list of `(output, start_sec, end_sec)` tuples
the editor eyeballed from the VTT, and checked post-hoc with
`work/venkatachala-ep01/check_reel.py --vtt --src-start --src-end`. This task
built reels 06 and 07 and, before doing so, replaced that ad-hoc flow with a
shared, reusable module.

### What the old approach (`recut.py`) got right

- It never pretended loudness alone was a safe cut signal — the editor had
  already learned (and documented in `check_reel.py`'s docstring) that these
  recordings carry a constant background drone (tanpura/shruti), so a real
  pause and continuous speech both "read loud." `recut.py`'s comment
  ("snapped to detected silence gaps") shows the boundaries were chosen with
  some care even though the snapping was manual/visual, not scripted.
  Keeping this precise non-negotiable constraint was itself the most
  important carry-over into `clip_cutter.py`.
- Re-encoding (not `-c copy`) on cut was correct for frame-accurate cuts and
  was preserved as-is.
- Simple and fast to run for a known, fixed list of clips.

### Weaknesses that motivated replacing it

- **Not reusable.** The `CUTS` list and `SRC` path are hardcoded to
  `venkatachala-ep01`; a new source video means a new copy-pasted script with
  new hardcoded numbers, not a call with different arguments.
- **No single report.** Boundary selection (silence-informed, but manual) and
  boundary verification (`check_reel.py`, run separately afterward) were two
  disconnected steps. There was no one artifact showing "here's the proposed
  cut and here's why it's trustworthy" before the ffmpeg cut command ran —
  mistakes were only caught after a full reel was already built.
- **No explicit confidence per boundary.** `check_reel.py` only emits
  PASS/WARN, which conflates "definitely fine" with "ambiguous, please look."

### What was tried building `clip_cutter.py`

- Extracted `load_cues`/`inside_cue` out of `check_reel.py` into
  `clip_cutter.py` as the single canonical implementation, then had
  `check_reel.py` import them. Verified this was a pure refactor (no behavior
  change) by re-running `check_reel.py` against the already-finished reel 03
  (`--src-start 784.0 --src-end 843.4`) before and conceptually after — same
  WARN/WARN result on both boundaries, which is the expected, previously
  documented false-positive from the coarse run-on VTT cues on this source.
- Added `find_candidate_pause` (ffmpeg `silencedetect` on a short window
  around a rough timestamp) and `snap_boundary` (snap + cue cross-check +
  confidence flag), plus `build_report`/CLI wiring.
- Ran it live against both new candidate windows (reel06: 1130.0–1169.0s,
  reel07: 1252.0–1284.0s) with the default window=4s, silence_db=-30,
  min_dur=0.25s. Saved `work/venkatachala-ep01/cut_report_06.json` and
  `cut_report_07.json`.

### What worked

- The tool ran cleanly end to end (CLI + library form) and produced valid,
  structured JSON for both candidates on the first real run — no crashes, no
  silent "it's fine" on an unverified boundary.
- It correctly caught the exact failure mode `check_reel.py`'s docstring
  already flagged as its known reliable catch: 3 of the 4 tested boundaries
  came back `review-manually` because the nearby silence pause sits a little
  *before* the VTT cue's own recorded end time (the cue's timestamp runs a
  beat long relative to where the audio actually goes quiet). This is the
  same coarse-run-on-cue slop already documented in STYLE.md (`docs/STYLE.md`
  at its current location), now caught automatically with an explicit flag
  instead of only showing up as a WARN after the whole reel was built.
- One boundary (reel07's end, snapped 1283.527s) came back `clean` on the
  first try — pause found 0.473s from the rough mark, lands cleanly outside
  any cue — showing the "clean" path isn't dead code, just rarer on this
  particular source's cue timing style.

### What didn't / open issue to revisit

- The tool's `review-manually` rate was 3/4 on this run, not because the
  underlying cut points are bad (reading the cue text confirms both are real
  sentence ends — "...taught to us through this story." and "...it is called
  Venkatachala.") but because this source's VTT cue end-timestamps
  consistently run slightly past where the actual audio pause is. A future
  improvement worth trying: widen `INSIDE_CUE_PAD` specifically for sources
  with this run-on pattern, or detect "snapped point is within ~1s before a
  cue's end and a pause was found there" as its own higher-confidence case
  instead of folding it into `review-manually`. Left as-is for now because
  loosening the pad is exactly the kind of threshold-chasing STYLE.md already
  warns against doing without a human checking the actual caption text first.
- Did not attempt to make `find_candidate_pause` adaptive (e.g. auto-loosen
  `--silence-db` if nothing is found) — every tested boundary did find at
  least one pause in-window with the fixed default, so there was no evidence
  yet that adaptive thresholds are needed. Revisit if a future source's audio
  mix produces `pause_found: false` often.

### Why `clip_cutter.py` lives outside any per-slug folder (now `tools/clip_cutter.py`)

`work/<slug>/` folders (e.g. `work/venkatachala-ep01/`) are scratch space for
one source video's clips, overlay PNGs, and subtitle JSON — everything in
there already hardcodes that slug's paths by convention. `clip_cutter.py`
takes `--video`/`--vtt` as explicit arguments and has zero knowledge of any
particular slug, so it belongs outside any single slug's folder, the same
way `assets/` (shared watermark) and `upload/` (shared uploader) already sit
outside any single slug's folder. (At the time this was written it lived
directly under `work/`; a later reorg moved it, and `transcribe.py`, into a
dedicated `tools/` folder — see the 2026-10-24 entry above.) The alternative
— copying a per-slug `clip_cutter.py` into each new `work/<new-slug>/` —
would recreate the exact duplication problem this task was started to fix
(two copies of `inside_cue` already existed before this change). Any future
source video can call `python3 tools/clip_cutter.py --video
sources/<new-slug>/source.mp4 --vtt sources/<new-slug>/source.en.vtt --start
... --end ...` with no modification to the tool itself.

### Building reel 06 — trusting vs. overriding `clip_cutter.py`'s snap

**Chosen moment:** Candidate A from `CUTTING_PLAN.md` — "the sinner who was
purified" (Madhava / Kapila Tirtha). Self-contained hook-turn-payoff arc, no
dependency on earlier reels' material, matches the plan's reasoning for why
it compresses well.

**Both boundaries came back `review-manually`** in `cut_report_06.json`.
Per STYLE.md's rule, each was checked by hand against `source.en.vtt` and
`ffmpeg silencedetect` directly (not just trusting the flag or discarding it):

- **Start — tool's snap (1129.564s) was WRONG, overridden.** Reading the VTT
  cue around it ("This principle has been taught to us through this story.",
  1128.47-1131.35) showed the snap landed inside the *previous*, unrelated
  closing line, not at the start of "Earlier, a Brahmin named Madhava...".
  The real cue gap is 1131.35-1135.35 (silence, confirmed by both the VTT and
  a direct `silencedetect` pass). Used **1135.05** (small 0.3s lead-in before
  the cue's own start, confirmed continuous speech from 1134.5s on with no
  silence in that window) instead of the tool's snap.
- **End — tool's snap (1167.725s) was RIGHT, kept as-is.** The flag fired
  because the snap sits inside a single long run-on VTT cue
  ("...performing Shraddha and making a pilgrimage, in this Kali Yuga, the",
  1164.24-1168.79). But re-running `silencedetect` on that exact window found
  a genuine ~0.97s pause at 1167.23-1168.21s, and reading the cue's own word
  order confirms that pause sits right after "...pilgrimage" and before "in
  this Kali Yuga" — a real clause break the coarse cue grouping just doesn't
  expose as a formal boundary. Kept the tool's **1167.72**.

This is exactly the asymmetry the tool was designed to surface rather than
hide: `review-manually` on this source is dominated by cue-timestamp slop,
not bad snaps, but it is NOT safe to assume every flagged boundary is fine
without reading the text — this session's start boundary was a genuine bad
snap that would have cut into an unrelated sentence if trusted blindly.

**Resulting clip:** 1135.05-1167.72s source, 32.7s duration. Over the
15-30s Gen-Z ideal from `CUTTING_PLAN.md`, but the payoff line ("...lost all
his sins by performing Shraddha and making a pilgrimage") needs to land whole
for the story to pay off; trimming further would have meant a mid-sentence
cut, which the plan itself says to avoid in favor of trimming at a sentence
boundary. Landed in the general 20-45s band instead.

**`check_reel.py` result:** PASS on dimensions (1080x1920) and duration
(32.7s). Spelling initially WARNed on "Brahminhood" and "committed" — both
real words (a devotional compound noun and a common English past-tense verb
missing from the macOS `web2` wordlist, not typos) — added "brahminhood" to
`ALLOWLIST` and "commit/commits/committed/committing" to `EXTRA_OK` in
`check_reel.py`, then re-ran clean. Start/end WARN on the odd-cut check, as
expected given the manual analysis above (false positives from the run-on
cue pattern, both boundaries confirmed clean by direct audio + text review).

### Data-loss incident during this task — `reels/` emptied mid-build

While finishing reel 06's cleanup step, the entire `reels/` folder was found
empty — not just the new reel, but all 5 previously-finished reels (01-05)
and their `.caption.txt` sidecars were gone. The only file operation run in
that step was `rm -f` with an explicit list of ~9 filenames, all inside
`work/venkatachala-ep01/`, no wildcards, nothing referencing `reels/` — but
the timing (system logs showed a `reels/` file still being accessed 2 minutes
before the folder's mtime changed) was close enough that it could not be
ruled out as the cause, so the task paused and reported the incident instead
of guessing at a fix.

**Recovery:** nothing substantive was actually lost. Every reel's raw clip
(`clip_raw.mp4`, `clip02_senses.mp4` ... `clip05_venkata.mp4`) and build
script (`build_reel01.py`, `build_all.py`) were untouched in `work/`, so all
5 reels were regenerated by simply re-running those two scripts — byte-for-
byte the same composition logic, just re-rendered. The `.caption.txt`
sidecars had no script to regenerate them from; 2 of 5 (reels 03 and 05) were
restored verbatim from text already read into context earlier in the same
session, and the remaining 3 (01, 02, 04) were rewritten from scratch in the
house format, summarizing each reel's own title/subtitle content already
visible in `build_reel01.py`/`build_all.py` — not reconstructed from memory of
the original prose, which was never re-read before being lost.

**Lesson:** when a cleanup step's own command list looks unambiguously safe
but a sibling directory still turns up empty, stop and verify the full
blast radius (`ls`/`mdfind` across the whole project, not just the files you
touched) before doing anything else, and say so explicitly rather than
silently re-running builds. In this case rebuilding was safe because the
source material for every lost file was independently verified intact first.

### Building reel 07 — "Lose your ego" (closing moral + dedication shloka)
**Chosen moment:** Candidate B from `CUTTING_PLAN.md` (now at
`docs/archive/CUTTING_PLAN.md`) — the discourse's own closing summary line
("lose all our sins, abandon our ego...") sealed by the speaker's traditional
Sanskrit closing dedication. Self-contained, needs no earlier setup, and
matches STYLE.md's "closing moral + shloka" recurring moment category.

**Cut boundaries used:** source 1251.157s - 1283.527s (32.4s). Both were the
tool's own snapped values from `cut_report_07.json` — neither was overridden.

- **Start (1251.157s) — flagged `review-manually`, trusted after manual
  verification, not overridden.** The flag fired because the snap lands
  inside the VTT's *displayed* cue for "Therefore, it is called
  Venkatachala." (cue interval 1250.149-1252.95s). Reading the cue's own
  word-level timing tags showed the actual spoken words finish by ~1250.15s
  — the cue's trailing display window overruns the real speech, the same
  run-on-cue slop already documented for reel06's end boundary. A direct
  `silencedetect` sweep at four thresholds (-30/-25/-20/-18dB) consistently
  found a genuine ~0.5s pause at 1250.93-1251.39s, with continuous audio
  before and after it — a real inter-sentence gap, not mid-speech. The
  tool's snap (midpoint of that pause, 1251.157) was kept as-is.
- **End (1283.527s) — flagged `clean`, kept as-is**, no manual override
  needed.

**Lesson reinforced:** `review-manually` on this source continues to be
dominated by the cue-display-vs-actual-speech-timing mismatch rather than
bad snaps, exactly as reel06 showed — but each flagged boundary still has to
be read by hand before trusting it, since reel06's *start* boundary that
session was a genuine bad snap. This session's flagged boundary turned out
to be a false positive, confirmed independently via silencedetect at
multiple thresholds, not assumed from the pattern alone.

**Resulting clip:** 32.4s, over the 15-30s Gen-Z ideal (same situation as
reel06) — the closing line + traditional Sanskrit dedication needs to land
whole for the payoff to read as a complete "today's lesson" close; trimming
further would cut the dedication short.

**Spelling:** `check_reel.py` WARNed on a few Sanskrit terms from the closing
dedication line — genuine words, not typos. Added them (lowercased) to
`ALLOWLIST` in `check_reel.py`, re-ran, spelling PASSed clean. Corrected one
auto-caption transliteration error against the standard form of the
traditional closing-dedication phrase, per STYLE.md's spell-check rule.

**`check_reel.py` result:** PASS on dimensions (1080x1920) and duration
(32.4s). PASS on spelling after the allowlist extension. Odd-cut check:
end PASS (clean caption boundary); start WARN ("inside a caption cue") —
expected, and already resolved by the manual verification above (false
positive from the run-on-cue display-timing mismatch, not a real bad cut).

### Evaluated a local Whisper model for cut-boundary timing — NOT adopted

**Why this was tried:** the user asked directly whether transcription could
be improved, and confirmed the root cause behind this session's repeated
`review-manually` flags is that cut boundaries are snapped against
`source.en.vtt`/`source.kn.vtt` cue timestamps, and those cues are YouTube's
own auto-generated + auto-translated captions with coarse, run-on timing
(see reel06/reel07 writeups above). The hypothesis: a dedicated local
speech-to-text model, run directly on the audio, would produce its own
segment timestamps independent of YouTube's cue grouping, and might snap to
real sentence boundaries more precisely than the VTT does.

**What was installed:** `faster-whisper` 1.2.1 (CTranslate2 reimplementation
of OpenAI Whisper), inside a **new, fully isolated virtualenv** at
`work/transcribe.venv` (created from `/usr/bin/python3`, the system
interpreter — explicitly NOT the shared `bie-work` env already on this
machine's PATH, learning the lesson from the earlier YouTube-uploader
protobuf conflict). Install took ~15s, footprint 214MB; model weights
(`medium`, ~1.5GB) download separately to the HuggingFace cache on first
run. Disk (208GB free) and install time were both a non-issue — this was
NOT the blocker.

**What was run:** wrote `work/transcribe.py` (durable, reusable — CLI +
importable `transcribe()` function, takes `--video`/`--language`/`--task`/
`--model`/`--out-prefix`). Tested it, not on the full 21-minute video, but
on a focused 70-second clip (source 1120.0-1190.0s) straddling the exact
reel06-start problem region already documented above, using the `medium`
model:

- **Kannada transcribe pass:** word-timestamp mode took ~6.3 minutes for 70s
  of audio (≈5.4x real time on this M4 Pro's CPU path — faster-whisper here
  has no MLX acceleration, unlike the sibling project's MLX-based large-v3
  runs). At that rate the full 21.4-minute video would take roughly
  **~2 hours**, which is a real but not fully disqualifying cost on its own.
  The bigger problem was the output: only 3 segments for 70s (one blob
  spanning 30s), garbled Kannada text matching
  `madhwa-pravachana-RAG/docs/ASR_NOTES.md`'s prior, more rigorous finding
  that plain Whisper (not the Kannada-finetuned `vasista22` model) mangles
  this exact kind of devotional discourse audio, and — critically for THIS
  question — individual word timestamps that swallowed up to **14.7 seconds**
  into one "word" span, a sign the model lost alignment, not a usable
  boundary signal.
- **Kannada-audio-to-English `task=translate` pass** (same model, same
  clip): much faster in practice (~24s for 70s of audio — translate decoding
  took a different/shorter path than the word-timestamp transcribe pass
  here) and genuinely more readable English, with 10 sentence-level segments
  instead of 3. This looked promising at first glance, but checking its
  segment start against the known-correct VTT boundary
  (`"Earlier, a Brahmin named Madhava, who had committed great sins..."`,
  confirmed starting at **1135.35s** in the VTT and independently verified
  by this session's manual `silencedetect` work on reel06) showed Whisper's
  own segment for that same sentence starts at **1130.92s** — 4.4 seconds
  early, landing inside the *previous*, unrelated sentence. That is the same
  failure mode (and roughly the same error size) as `clip_cutter.py`'s
  original wrong snap (1129.564s) that a human had to catch and correct by
  hand. Whisper's segment timing did not clear up the ambiguity here; it
  reproduced it. The translate pass also showed visible repetition-loop
  hallucination (the same sentence "Venkatachala's work in this Kali Yuga is
  more in this Kali Yuga." generated twice for two different audio spans),
  a known Whisper failure mode on hard/noisy source audio.

**Decision: NOT adopted.** Per the task's own instruction to be honest
either way — this was tested against a real, previously-documented problem
spot and it did not demonstrably improve boundary precision there. The
~2-hour full-video runtime for the transcribe path (the only path with
word-level timestamps at all) makes iterating on this impractical for now
even before the accuracy problem; the much faster translate path's sentence
boundaries were not more reliable than the existing VTT-plus-silencedetect
approach. This matches `ASR_NOTES.md`'s own conclusion from a more rigorous
multi-model comparison on similar audio: generic Whisper mangles this
content, and only a Kannada-finetuned model (`vasista22/whisper-kannada-medium`)
did well on word accuracy — but that comparison never claimed to have fixed
segment-boundary timing either, and still found the shloka/chant portions
wrong across all models. No model was tested here that this session has
reason to believe would fix cut-boundary timing specifically.

**What stays / what doesn't:** `work/transcribe.venv` and `work/transcribe.py`
are kept as durable, reusable artifacts (per this task's MUST-KEEP-scripts
requirement) in case a Kannada-finetuned model or a faster accelerated
runtime is evaluated in a future session — but nothing from this evaluation
is wired into the standard pipeline. The throwaway test clip and its two
transcript outputs were deleted after inspection; no transcript file from
this evaluation should be treated as an input to cutting any reel.
`work/clip_cutter.py` + `source.en.vtt`/`source.kn.vtt` remain the sole
boundary-snapping approach for all reel cutting, including reels 01-07 in
this run. `review-manually` flags on this source continue to need a human
read of the caption text + a direct `silencedetect` check, exactly as
reels 06 and 07 already did above — there is no new automated shortcut for
that step.

**Honesty caveat (still open, unrelated to this evaluation's outcome):**
even if a transcript's *timing* were someday shown to be better, that is a
separate question from whether its *words* are a faithful rendering of the
original Kannada meaning. No transcript used by this project — YouTube's
VTT or any Whisper variant tested here — has been independently checked
against the source Kannada by a human reviewer fluent in it. That remains
an open concern regardless of which tool produces the timestamps.

---

## 2026-10-24 (later) — Removed the Whisper evaluation tool from the project

Per the user's explicit request, `tools/transcribe.py` (the faster-whisper
evaluation script) and its isolated venv `tools/transcribe.venv` (~214MB)
were deleted from the project entirely, along with the related references in
`STYLE.md`'s "transcript source" and "work-folder cleanup policy" sections.

**Why removed, not just left unused:** the 2026-10-22 evaluation already
concluded Whisper was NOT adopted for this pipeline (see that entry above),
so the tool and its dependency footprint were dead weight once the user
asked for Whisper-related things to be cleaned out of the project.

**What was NOT touched, and why:** the actual Whisper model weights
downloaded during the 2026-10-22 evaluation live in the global HuggingFace
cache at `~/.cache/huggingface` (~11GB), which is OUTSIDE this project
folder and shared across any tool on the machine that uses HuggingFace
models — not specific to this project. The user confirmed this is fine to
leave on the laptop; only project-internal Whisper artifacts were removed.

**If a Kannada-finetuned or otherwise meaningfully different speech-to-text
model is worth evaluating in the future** (the 2026-10-22 entry notes plain
Whisper mangled this devotional audio, but a Kannada-finetuned model like
`vasista22/whisper-kannada-medium` was never tested here), rebuild the tool
from scratch using the same isolated-venv pattern (never install ML
dependencies into the shared project/system Python — see the YouTube-
uploader protobuf-conflict lesson) rather than expecting `transcribe.py` to
still exist.

---

## 2026-10-23 — New source `venkatachala-ep06`, first 2 reels, and a
per-source title-card collision

**Slug chosen:** `venkatachala-ep06`, from the actual video title ("Glory of
Venkatachala | Ep - 06 | ವೇಂಕಟಾಚಲ ಮಹಿಮೆ | By Sri Satyatmateertha
Shripadangalavaru"), the same discourse series/speaker as `venkatachala-ep01`
but a different episode (Ep. 06) and, as it turned out, a visibly different
camera framing — downloaded full (2887.4s, ~48.1 min; matches the published
2887.0s duration) via `yt-dlp --cookies-from-browser chrome` with English +
Kannada auto-captions, per the standing house rule (never
`--download-sections`).

**Source is 4K (3840x2160, 25fps)**, unlike venkatachala-ep01/
utsarjana-upakarma (1920x1080) — this is the first source this project has
hit at that resolution. Handled by scaling down to 1920x1080 at the start of
each build script's filter chain, BEFORE calling the shared
`crop_reframe_filter()` (which assumes a 1920-wide input) — `crop_x` was
measured and is expressed in that same 1920-wide coordinate space, so it
stays directly comparable to how it's derived for any other source.

### Candidate moments picked and why

Read the whole `source.en.vtt` (after writing a small one-off dedup pass to
collapse the VTT's karaoke-style rolling-caption duplication into a clean
line-per-cue transcript, since the raw file repeats each growing line
multiple times — this was throwaway reading-aid code, not a new tool, and
the transcript dump files were deleted after use). The discourse turned out
to be a continuous Padmavati/Srinivasa narrative with no single short
"closing moral + shloka" moment at the very end (checked: the talk's last
~150s is the tail of an unrelated marriage-arrangement scene ending in a
terse chant with no self-contained lead-in moral, so that STYLE.md category
was considered and deliberately NOT used this time — it didn't fit this
episode).

Two candidates were picked instead, both mid-discourse "hook + payoff"
teachings that stand alone without needing the surrounding story:

1. **"There's no friend like a mother"** (source ~301-345s) — Dharmadevi
   wakes Padmavati, quotes "Nachamatrasamam Mitram Putrinam Asthi Nandini"
   (there is no friend like a mother for her children), then the speaker
   generalises it into a teaching about parents and children exchanging
   trust and love. Self-contained, relatable even without any Venkatachala-
   specific context, clean hook (the quoted line) + payoff (the
   generalisation).
2. **"Why the chakra & conch?"** (source ~616.7-671.4s) — a "did you know"
   teaching, citing the Aditya Purana: the Sudarshana chakra's radiance
   (bright as crores of suns) dispels not just outer darkness but the
   darkness of ignorance within, and the conch isn't just for sound — it
   gives knowledge of the truth, being the Lord's own form. Two parallel
   "not just X, but Y" statements about two different objects, self-
   contained doctrine, no dependency on the surrounding story.

### clip_cutter.py confidence results — all 4 boundaries flagged, all 4
resolved by hand

Ran `tools/clip_cutter.py` against both candidates' rough windows (see
`cut_report_01.json`/`cut_report_02.json` in `work/venkatachala-ep06/`).
**All 4 boundaries came back `review-manually`** on the first pass — this
source shows the exact same coarse-run-on-cue pattern already documented for
venkatachala-ep01's reels 06/07, so none of this was a surprise, but each
flag was still checked by hand against the actual caption text and a direct
`ffmpeg silencedetect` pass before trusting or overriding it, per STYLE.md:

- **Reel (no-friend) start — rough guess corrected before even running the
  tool cleanly.** An initial rough start of 309.0s snapped the tool to
  308.697s, which — reading the cue text — lands mid-clause ("he woke
  [pause] her up and asked her, Do not hide anything...", a real pause but
  grammatically the wrong place to cut). Rather than overriding the tool's
  snap, the rough window was widened earlier to 301.0s (the actual scene-
  change sentence boundary, "...Srinivas went outside." / "Dharani Devi
  came directly to Padmavati's room..."), confirmed by a direct
  `silencedetect` pass (clean ~0.53s pause at 300.70-301.23s). Re-running
  `clip_cutter.py` on this corrected window came back **CLEAN** (snapped
  300.973s) — the first-pass flag here was a mis-chosen rough guess, not a
  tool failure.
- **Reel (no-friend) end — `review-manually` (345.088s), KEPT as-is.** Flag
  fired because the snap lands inside the coarse cue "children should be
  the same as for parents. There is" (340.72-345.43s). Confirmed by direct
  `silencedetect` (genuine ~1.07s pause at 344.55-345.62s) and by reading the
  cue's own word order: the pause sits right after "...for parents." and
  before "There is love, of course..." — a real sentence break the cue
  grouping doesn't expose. Same false-positive pattern as venkatachala-
  ep01's reel06/reel07 end boundaries.
- **Reel (chakra-conch) start — `review-manually` (616.661s), KEPT as-is.**
  Flag fired because the snap lands inside the cue "one by one. As"
  (613.04-617.59s). Confirmed by direct `silencedetect` (genuine ~0.6s pause
  at 616.31-616.92s) and by reading the cue text: the pause sits right after
  "...the Supreme Soul has described all the weapons one by one." and before
  "As indicated in the Aditya Purana..." begins the next sentence — a real
  sentence break.
- **Reel (chakra-conch) end — tool's first snap (670.11s) was WRONG,
  OVERRIDDEN.** An initial rough end guess of 667.5s snapped to 670.11s,
  which — checked directly with `silencedetect` and by reading the cue
  text — falls mid-clause ("...the conch was the [pause] form of the
  Lord", splitting "the" from "form"). Widened the search window and
  re-ran against a corrected guess of 671.38s; this landed on the real
  pause (confirmed ~0.6s gap at 671.09-671.68s) between "...the form of the
  Lord." and "In addition, in the chakra..." — the actual sentence
  boundary. Re-running `clip_cutter.py` on the corrected window came back
  **CLEAN** (snapped 671.407s).

Same lesson as venkatachala-ep01's reel06/reel07: `review-manually` on this
source is dominated by the cue-display-vs-actual-speech-timing mismatch, but
it is NOT safe to assume every flagged boundary is fine OR broken without
reading the actual text each time — this session had both a genuine bad
snap (chakra-conch end) and confirmed-clean false positives (both final
kept boundaries), in the same run.

**Resulting clips:** no-friend-like-mother 44.2s (within the 20-45s default
band); chakra-conch 54.8s (over the 20-45s band and the 15-30s Gen-Z range,
but within STYLE.md's 15-60s acceptable range — the chakra and conch
teachings are one continuous parallel-structure passage, and trimming either
half would leave one payoff dangling, the same trade-off already accepted
for venkatachala-ep01's reels 06/07).

### crop_x derivation for this new speaker/source

Extracted a probe frame, downscaled the 4K source to 1920x1080 (frame_1080),
overlaid a 100px `drawgrid`, and read the speaker's face-center x directly
off the grid: approximately x=1005 in the 1920-wide frame. With
`crop_w=864`: **crop_x = 1005 - 432 = 573**. Verified by rendering the actual
crop (`ffmpeg crop=864:1080:573:0`) against probe frames from BOTH reels'
time ranges (not just one) before using it in either build script — the
speaker's framing was confirmed consistent across the ~6 minutes separating
the two clips. This is a different speaker/source from venkatachala-ep01, so
per STYLE.md this value was derived fresh and NOT copied from any other
slug.

### Title card collision — found during visual preview review, fixed with a
per-slug override

Both reels' preview frames (extracted at Step 8, before declaring either
reel done) showed the shared `overlays_lib.render_title()` band (band_top=
160, tuned for venkatachala-ep01's speaker) landing directly on this
speaker's forehead/tilak mark. Measured the actual headroom on a probe
frame: this speaker's hairline sits only ~90-120px from the top of the
1080-tall crop, with no usable gap for a 2-line band at the existing
font/position — and no `crop_y` fix was possible either, since `crop_h`
already equals the full source height (crop_y=0 is the only option; there's
nothing above the head in the original footage to crop into instead, unlike
`crop_x` which has room to shift left/right).

Paused and asked the user how to resolve it rather than guessing or
silently editing the shared `overlays_lib.py` (a STYLE.md-governed file).
**User direction: shrink/reposition the title for this source only, as a
per-slug override — do not touch the shared default (venkatachala-ep01's
already-built reels must stay unaffected).** Built `title_compact.py` in
`work/venkatachala-ep06/` (band_top=8, fonts shrunk to 26px lead / 34px
main, line_h=38 — tucked right at the very top edge, above the hairline)
and verified the new geometry against a real composited probe frame
(`title_test_composite.png`, since deleted post-verification per the
cleanup policy) BEFORE wiring it into either build script. Rebuilt both
reels; the two earlier builds (numbered 01/02 by `reel_numbering.py` before
the fix) were deleted by exact filename (no wildcards) and the corrected
builds landed at 03/04 per the numbering tool's normal auto-increment
behavior — reel numbers are not reused once assigned, so the final reels
for this slug start at 03, not 01 (recorded in `docs/SOURCES.md`).
Re-extracted preview frames after the fix and confirmed: title clear of the
forehead/tilak mark with visible margin, still legible, no other safe-zone
rule (subtitle `SUB_Y`, watermark y, crop geometry) touched or affected.

### New Sanskrit terms added

Added **Dharmadevi** and **Padmavati** to `tools/sanskrit_terms.py` (both
appear consistently, with a single spelling, throughout this source's
captions — not an invented or uncertain spelling, same confidence level as
existing no-variant entries like "Shatananda"). Did NOT add the quoted
shloka words ("Nachamatrasamam", "Mitram", "Putrinam", "Nandini", "Asthi")
to the shared file — these are a one-off quoted verse transcribed as heard,
not a recurring channel/Madhwa proper noun, so they went into this slug's
own `check_reel.py` ALLOWLIST extension instead (same split venkatachala-
ep01's `check_reel.py` already uses for slug-specific terms like "kapila"/
"tirtha"). Also allowlisted "Aditya" (the Purana's name) and reused the
already-shared "Sudarshana"/"chakra"/"srinivasa" entries from venkatachala-
ep01's allowlist. Standardised the auto-caption's "Venkatesa" to the
already-canonical "Venkateshwara" (`tools/sanskrit_terms.py`) in the
chakra-conch reel's subtitles rather than introducing a second near-
duplicate spelling.

One spelling false-positive unrelated to Sanskrit: "dispelling" (correct
English, web2 has "dispel" but not the doubled-consonant gerund) WARNed
and was added to this slug's `check_reel.py` `EXTRA_OK`, the same category
as venkatachala-ep01's "Brahminhood"/"committed" fixes.

### check_reel.py final results

Both reels: **PASS** dimensions (1080x1920), **PASS** duration (44.2s /
54.8s, both ok for a Short), **PASS** spelling (clean after the allowlist
additions above). Odd-cut check: each reel has exactly one WARN (the
no-friend reel's end boundary, the chakra-conch reel's start boundary) —
both are the SAME confirmed false positives already resolved by hand above
(coarse run-on VTT cues, not real bad cuts); the other boundary on each reel
(start / end respectively) is a clean PASS. No FAILs on either reel.

Preview frames were extracted and visually inspected for both finished
reels, both before and after the title-card fix — confirmed: title legible
and clear of the speaker's face, subtitles legible and correctly
positioned, watermark present at the correct position, no collisions, and
the margin's blurred-mirror fill area happens to read as near-solid-black
on this source (because the original footage's own laptop lid sits low in
frame and is dark-colored) — confirmed by isolating the `[reframed]` filter
stage output on an actual composited frame that this is the real blurred
source content, not a rendering bug.

Final reels: `reels/venkatachala-ep06/venkatachala-ep06_03_no-friend-like-mother.mp4`,
`reels/venkatachala-ep06/venkatachala-ep06_04_chakra-conch-meaning.mp4`,
each with a `.caption.txt` sidecar. Not uploaded (out of scope for this
task). `sources/venkatachala-ep06/source.mp4` kept (more reels planned from
this source later), along with both build scripts, `check_reel.py`,
`title_compact.py`, and both `cut_report_*.json` files.

---

## 2026-10-23 (later) — Deleted the live reel01 test-title video (`fFjuaOxPx_Y`)

The user watched the live copy of `venkatachala-ep01_01_four-names.mp4`
(video ID `fFjuaOxPx_Y`, title "The 4 Names of Venkatachala, across the 4
Yugas (Updated) #Shorts" — the leftover from the earlier OAuth/upload
testing documented above) and said "this video was not right," asking for
it to be removed from the channel.

Before deleting, confirmed the video's identity directly via `yt-dlp
--skip-download --print` (title, uploader=Madhwa16, channel URL, upload
date 20261022) rather than trusting the pasted URL alone — matched exactly
what `docs/SOURCES.md` already had on record for reel01's test upload. Ran
`upload/youtube_upload.py --delete fFjuaOxPx_Y --yes` (the user had already
named this specific video/action in the current turn). Deletion succeeded
and is permanent — no undo via this project's tooling.

**Resulting state:** reel01 has no live copy on the channel now. The local
file `reels/venkatachala-ep01_01_four-names.mp4` (and the project's own
build scripts for it) were not touched — only the live YouTube upload was
removed. A rebuild with the current crop/subtitle style is still needed
before any future re-upload of reel01, same as noted before this deletion.

---

## 2026-10-23 (later) — Reels 05/06 for `venkatachala-ep06`, built in
direct response to "the reels seem to cut abruptly" feedback

After reels 03/04 went live (uploaded in this same session), the channel
owner gave explicit feedback: the cuts felt abrupt, and asked for 2 more
reels from the same source with that specifically in mind. This entry
covers what was done differently as a result, before covering the 2 new
reels themselves. Numbers 05/06 were assigned by `tools/reel_numbering.py`'s
`next_reel_number()`, not hardcoded.

### What changed this session to address "abrupt cuts"

Previous sessions on this source (reels 03/04, and venkatachala-ep01's
06/07) already used `tools/clip_cutter.py` + manual `silencedetect`
verification to confirm a boundary was a REAL sentence break rather than a
mid-word snap — but once confirmed real, the boundary was generally placed
at or very close to the detected pause's own edge (frame-accurate against
the nearest edge of silence). That is correct for avoiding a mid-word cut,
but it is not the same thing as a cut that *feels* unhurried — a cut placed
right at the first/last instant of detected silence can still read as
abrupt if there's no audible breath before the first word or after the
last.

This session added a deliberate second step on top of the existing
verification: once a boundary was confirmed as a real sentence break, the
actual cut point was placed with a MARGIN ***inside*** the detected silence
window, not at its nearest edge — closer to the far edge of the pause (the
quietest part, furthest from speech) rather than the edge closest to the
word. Concretely:
- **Start boundaries**: cut a few tenths of a second BEFORE the detected
  pause ends (i.e. before the first word begins), rather than right at
  pause-end/speech-start. This leaves an audible beat of near-silence
  before the hook line starts, instead of a hard attack on the first
  syllable.
- **End boundaries**: cut a few tenths of a second AFTER the detected pause
  begins (i.e. after the last word's sound has fully died out), rather than
  right at speech-end/pause-start. This leaves the last syllable room to
  settle instead of truncating it the instant volume drops.
- Where a `review-manually` flag's own coarse-cue text didn't make the real
  pause obvious, the exact pause window was re-derived with a direct
  `ffmpeg silencedetect` pass scoped tightly around the rough boundary
  (window 6-18s, d=0.15-0.25s) AND cross-checked against the VTT's own
  word-level karaoke timestamps (the `<HH:MM:SS.mmm>` tags inside each cue)
  to confirm exactly when the first/last word of the intended line is
  actually being spoken — not just when the cue's own (often run-on)
  displayed window claims it starts/ends. This is a more precise signal
  than reels 03/04 used, which relied on the pause + cue-text reading alone
  without pulling the individual word timestamps.

**Measured margins, this session vs. reel03/04:**

| Reel | Boundary | Lead-in/lead-out silence to nearest word |
|------|----------|-------------------------------------------|
| 03 (no-friend) | start | CLEAN snap, tool's own pause midpoint used directly — no deliberate margin added |
| 03 (no-friend) | end | `review-manually`, kept at the tool's snap (345.088s) — at the edge of the confirmed ~1.07s pause (344.55-345.62s), not pulled further in |
| 04 (chakra-conch) | start | `review-manually`, kept at the tool's snap (616.661s) — at the edge of the confirmed ~0.6s pause, not pulled further in |
| 04 (chakra-conch) | end | CLEAN snap (671.407s) — tool's own pause midpoint, no deliberate margin added |
| **05 (dharmadevi-name)** | **start** | **0.73s** of silence between the cut point (111.5s) and the first word ("that", 112.23s) — deliberately placed inside the ~0.75s detected pause (111.43-112.18s), not snapped to its edge |
| **05 (dharmadevi-name)** | **end** | **~1.2s** of silence between the end of speech (~155.4s, inferred from the word-tag on "meaningful.") and the cut point (156.6s) — deliberately placed past the far edge of the ~1.0s detected pause (155.44-156.46s) |
| **06 (bakuladevi-humility)** | **start** | **0.58s** of silence between the cut point (2674.8s) and the first word ("That", 2675.383s) — placed inside the ~0.81s detected pause (2674.42-2675.22s) |
| **06 (bakuladevi-humility)** | **end** | **~0.4s** of silence between the end of speech (~2729.6s, inferred from the word-tag on "business.") and the cut point (2730.0s) — placed past the detected ~0.4s pause (2729.15-2729.56s) |

**Did it work?** Measured directly against the finished, composited output
(not just the plan): running `ffmpeg silencedetect` on the first/last 2s of
each FINISHED reel confirms both new reels open with a clean beat of
near-silence before speech (0.68s on reel05, 0.42s on reel06) and close
with speech settling into silence before the hard cut (reel05's last 2s
show ~1.0s of trailing silence; reel06's show ~0.38s). Reel03/04's own
boundaries, by contrast, were placed at or right against the detected
pause's edge once confirmed real — correct (no mid-word cuts) but with
less deliberate breathing room than 05/06. This is a genuine difference in
method, not just in outcome: 03/04 asked "is this pause real?" and stopped
once the answer was yes; 05/06 asked that AND THEN "where inside this real
pause should the cut land to feel unhurried?".

**One trade-off this surfaced:** the full first-pass window for reel06
(the entire "What is your leela?...God will teach me how to do business"
arc, 2662.5-2733.0s) measured 69s — over STYLE.md's 60s hard limit. Rather
than force a mid-explanation cut to hit a shorter duration, the window was
tightened to the tightest self-contained hook+payoff core (dropping the
narrative scaffolding "Meanwhile Bakula Devi is slowly coming..." and
starting directly at the hook line "That Dharmadevi is none other than
God..."), landing at 55.2s — still over the 20-45s ideal band but within
STYLE.md's 15-60s acceptable range, and a real sentence-boundary trim, not
an arbitrary one.

### PROPOSED STYLE.md addition (not applied — flagged for user confirmation)

Worth considering as a permanent addition to STYLE.md's "Cut placement"
section, NOT applied here per GUARDRAILS.md (standing rules only change
with explicit user confirmation): *"When placing a confirmed-clean cut
boundary inside a detected silence/pause window, don't snap to the edge of
the pause nearest the speech — deliberately place the cut 0.3-1.0s further
into the pause (away from the word) so there's an audible breath before the
first word / after the last, rather than a frame-accurate cut at the exact
instant speech starts/stops."* This session's measurements (above) suggest
it measurably helped, but it's one data point (2 reels) against the user's
qualitative "abrupt" complaint — worth confirming with the user's reaction
to reels 05/06 before writing it into STYLE.md as a standing rule.

### The 2 new candidate moments and why they're self-contained

Read the full `source.en.vtt` end to end again (a throwaway dedup pass was
written to collapse the karaoke-style rolling captions into one line per
cue for easier reading — same one-off reading aid as the 2026-10-23 entry
above, deleted after use, not a new tool). Looked specifically for moments
that don't overlap reel03 (~300.97-345.09s) or reel04 (~616.66-671.41s), and
checked the "closing moral + shloka" category per STYLE.md: the talk's
actual ending (~2737-2878s) turned out to be mostly music/chant with very
sparse, gappy speech (long silent stretches 2748-2804s and 2809-2875s) and
no substantial self-contained moral in continuous prose — considered and
deliberately NOT used, the same kind of "doesn't fit this episode" call
already made for reel03/04's session.

1. **"What does the name Dharmadevi mean?"** (source 111.5-156.6s) — EARLIER
   in the talk than reel03 (not after it). The Lord explains that Dharani
   Devi's disguise is named "Dharmadevi" because the name itself signals
   she bears responsibility for Padmavati's dharma/life: if Padmavati is
   given to Him, her life (and the dharma it serves) will be preserved.
   Self-contained etymology/"did you know" teaching, same structural shape
   as reel04's chakra-conch reel (a name's hidden meaning explained),
   no dependency on surrounding story.
2. **"Don't take credit for God's work"** (source 2674.8-2730.0s) — a
   humility teaching late in the discourse (after both the Hanuman/
   Shukacharya section and the letter-writing section, in the closing
   third of the talk, though not literally the final scene). The Lord
   credits Bakuladevi for arranging His marriage; she insists she did
   nothing, then admits that her own unaided effort, in the past, came to
   nothing without His grace. Self-contained hook (who really did the
   work?) + payoff (true humility credits grace, not self), no dependency
   on the surrounding story beyond what's naturally re-stated in-clip.

A third candidate was considered and rejected: the Hanuman/Shukacharya
"your karma vs. Hanuman's karma" passage (~2303-2340s) read as a strong
doctrinal point on paper, but its auto-captions are noticeably more garbled
there than elsewhere in this source (repeated rolling-caption artifacts like
"What is the happiness that is the result of that merit?" appearing four
times with no clean resolution) — judged too risky to build clean,
spell-checked subtitles from without materially rewriting/guessing at the
speaker's actual meaning, which STYLE.md's transcript-honesty rule doesn't
allow. Also considered and rejected for the same reason: most of the
1850-2060s stretch (Shukacharya's penance/detachment passage), which has
similar garbling.

### clip_cutter.py results — all 4 boundaries flagged, all 4 resolved by hand

Exactly the same pattern as every previous session on this source: ran
`tools/clip_cutter.py` on both rough windows (`cut_report_03.json`,
`cut_report_04.json` in `work/venkatachala-ep06/` — NOTE: these filenames
reuse `03`/`04` from this slug's own build-script-local numbering, which is
independent of and does NOT collide with the final reel numbers 05/06
assigned by `reel_numbering.py`; the slug's existing `cut_report_01.json`/
`cut_report_02.json` from the reel03/04 session were left untouched). All 4
boundaries (2 per clip) came back `review-manually` — resolved by hand
against the VTT word-level timestamps and direct `silencedetect` passes, as
detailed in the margin-placement section above and in each build script's
own docstring (`build_reel03.py`, `build_reel04.py`). No tool snap was
blindly trusted or blindly overridden — each was independently re-derived.

### New Sanskrit terms added

Added **Bakuladevi** to `tools/sanskrit_terms.py` — the nurse/companion who
helps arrange Padmavati's marriage in this source's narrative, appearing
consistently with a single spelling throughout the captions (same
confidence tier as the already-added Dharmadevi/Padmavati, not an invented
or uncertain spelling).

**One term deliberately NOT added, flagged as uncertain instead:** the raw
auto-caption in the dharmadevi-name-meaning window includes an isolated,
garbled word "Koravanji" ("Devi Koravanji, the goddess who teaches Dharma")
that doesn't parse as a clean, independently-confirmable Sanskrit/Kannada
term — it reads like a mis-transliteration or ASR artifact, but there's no
way to verify a correct spelling from the available materials. Per
GUARDRAILS.md's rule against guessing a Sanskrit/Madhwa proper noun's
spelling, it was NOT added to `tools/sanskrit_terms.py` and NOT used in the
reel's subtitles — the subtitle line was paraphrased around it using only
the clearly-translated English meaning ("the goddess who teaches Dharma")
instead. If the user can confirm the intended word, add it to
`tools/sanskrit_terms.py` properly rather than guessing here.

Also added to `work/venkatachala-ep06/check_reel.py`'s `EXTRA_OK` (not
Sanskrit terms, same category as the existing "dispelling"/"Brahminhood"
entries — real English words missing from web2's morphology coverage, not
typos): "couldn't", "replied", "proud".

### check_reel.py final results

Both reels: **PASS** dimensions (1080x1920), **PASS** duration (45.1s /
55.2s, both ok for a Short), **PASS** spelling (clean after the `Bakuladevi`
+ `EXTRA_OK` additions above). Odd-cut check: each reel has a WARN on BOTH
boundaries (4 total) — all 4 are the same confirmed false-positive pattern
already extensively documented for this source (coarse run-on VTT cues
whose displayed window runs past where the actual audio goes quiet), each
individually resolved by hand via direct `silencedetect` + VTT word-tag
cross-checks as detailed above. No FAILs on either reel.

Preview frames were extracted and visually inspected for both finished
reels (start/mid/end): title legible and clear of the speaker's
forehead/tilak mark (the `title_compact.py` override, reused unchanged from
reel03/04, re-verified against THIS session's own probe frames rather than
assumed to still fit — framing confirmed consistent), subtitles legible and
correctly positioned at `SUB_Y=1560`, watermark present at the correct
position, no collisions. `crop_x=573` was re-verified (not re-derived) by
rendering the crop against probe frames from both new clips' own time
ranges — framing confirmed consistent with reel03/04's speaker positioning
before use. Additionally, per this session's specific "abrupt cuts" focus,
`ffmpeg silencedetect` was run directly on the first/last 2s of each
FINISHED (composited) reel to confirm no abrupt start/mid-word attack or
clipped-off ending — see the margin table above for the measured results.

### Scope confirmation

Reels 03/04 (already live on YouTube) and venkatachala-ep01's reels were
NOT touched, rebuilt, re-cut, or re-uploaded — out of scope for this task,
per GUARDRAILS.md. Nothing was uploaded, deleted, or had its privacy
changed on YouTube in this session. Final reels:
`reels/venkatachala-ep06/venkatachala-ep06_05_dharmadevi-name-meaning.mp4`
and `reels/venkatachala-ep06/venkatachala-ep06_06_bakuladevi-humility.mp4`,
each with a `.caption.txt` sidecar, left finished in
`reels/venkatachala-ep06/` for the user's manual review before any future
explicit upload request. `sources/venkatachala-ep06/source.mp4` kept (the
user said "later we will do more as well", so further reels may still come
from this source).

---

## 2026-10-23 (later still) — Abrupt cuts, part 2: the FADE fix + venkatachala-ep07 (4 new reels)

### The problem the margin fix did NOT solve
Reels 05/06 (ep06) were rebuilt in the previous session with deliberate
SILENCE MARGIN at the cut boundaries (snapping further into the surrounding
pause) and that was verified via silencedetect + VTT sentence-boundary
checks. The user watched 05/06 and reported they STILL feel abruptly cut.
Root cause (confirmed directly with the user, not re-diagnosed here): the
abruptness is about HOW the cut transitions, not WHERE it lands. Even with
the boundary sitting in genuine silence and no mid-word truncation, a hard
jump-cut feel remains — a sudden audio amplitude edge and an instant visual
start/stop. Margin placement is necessary but NOT sufficient: it fixes the
cut POINT, not the cut's TRANSITION.

### The fix: audio + video fade at every cut
A genuinely different technique, ADDITIVE to the already-correct
silence-margin + VTT boundary placement (that part is kept, not replaced):
a short fade-in at the start of each clip and fade-out at the end, on BOTH
audio and video.
- **Duration: 0.2s (200ms).** Chosen by prototyping on an existing raw clip
  and inspecting the actual rendered first/last frames: 200ms is clearly
  visible/audible as a deliberate transition (first frame solid black, audio
  RMS ramps from near-silence up), while staying short enough not to eat into
  the already-tight silence margins (the existing ep06 boundaries had ~0.4-1.2s
  of margin; a 0.2s fade fits inside that on every boundary). Applied
  CONSISTENTLY to all 6 clips in this task (2 rebuilt ep06 + 4 new ep07) for a
  uniform house feel.
- **Method: fade to/from BLACK** (ffmpeg `fade=t=in/out` on video,
  `afade=t=in/out` on audio). This machine's ffmpeg has no drawtext but DOES
  have the plain `fade` filter (a pixel-level dissolve, not a text feature).
  Fading through black reads as an intentional edit rather than a hiccup.
- **CRITICAL placement lesson (learned the hard way this session):** the fade
  must be applied to the FINAL COMPOSITED frame — the tail of the
  filter_complex, on `[vout]` AFTER the title/subtitle/watermark overlays —
  NOT to the raw clip before compositing. A first attempt faded the raw clip
  and fed it into the unchanged overlay chain; the title-card and watermark
  PNGs are composited at full opacity for the clip's whole duration (no
  `enable=` gating on them), so they stayed fully bright while the video
  underneath faded to black, leaving the title/watermark floating in a black
  frame — an overlay-desync artifact, exactly the failure mode the task
  warned to check for. Caught by directly extracting and LOOKING AT the
  start/end frames, not by trusting the filter graph. Fixed by moving the
  `fade`/`afade` to the end of the chain so the whole composited frame fades
  as one unit. Re-verified on extracted frames: title, subtitle, watermark,
  and background now dim together. `tools/fade_clip.py` was added as the
  shared reference/prototyping helper (and documents the 0.2s choice); the
  build scripts apply the fade inline at the end of their own filter chains
  so it lands on the composited frame.
- **STYLE.md was NOT edited** (per GUARDRAILS — needs user confirmation). The
  proposed new house rule is carried as a pending suggestion in
  `work/build-notes.md` for the user to confirm.

### Part A — ep06 reels 05/06 rebuilt with the fade
Same cut boundaries as before (111.5-156.6s for reel05, 2674.8-2730.0s for
reel06 — placement already confirmed correct, only the fade was added),
same crop_x=573, same per-slug title_compact. Build scripts
(`work/venkatachala-ep06/build_reel03.py`/`build_reel04.py`) pinned to
REEL_NUM 5/6 (a rebuild of already-assigned numbers, so next_reel_number was
NOT called for these). Built to `.NEW.mp4` staging names, verified
(ffprobe + check_reel + perceptual frame inspection), and only THEN were the
4 old abrupt files deleted by exact filename and the new builds promoted into
place. check_reel: both PASS dimensions/duration/spelling; the odd-cut WARNs
are the same documented coarse-run-on-cue false positives, boundaries
unchanged from the verified prior build. Not uploaded — left for user review.

### Part B — venkatachala-ep07: new source, 4 new reels
Source: "Glory of Venkatachala | Ep - 07" (https://www.youtube.com/watch?v=9IDCabMthdQ),
same speaker/series as ep06, Hubli recording, 3474.5s (~57.9 min). Downloaded
in FULL with `yt-dlp --cookies-from-browser chrome` (en+kn captions), duration
verified against the published ~3475s. The merged download came out as webm
(av1/opus); losslessly remuxed to `source.mp4` (`-c copy`) for convention
consistency, webm removed.
- **crop_x=523 FRESHLY DERIVED** (NOT reused from ep06's 573): grid-overlay on
  a 1920-scaled probe frame put the face-center at x~955, crop_x = 955 -
  864//2 = 523. Verified against 3 real probe frames (10/50/90% of the talk).
  It genuinely differs from ep06 — confirming the task's insistence on a fresh
  derivation was warranted, not a formality.
- **Title-collision check done proactively:** compositing the shared
  render_title() band over a real crop_x=523 frame collided with the tilak
  (same near-zero-headroom issue as ep06), so a per-slug
  `work/venkatachala-ep07/title_compact.py` was built up front (same verified
  geometry as ep06's: band_top=8, 26/34px fonts), BEFORE building — not
  discovered afterwards.
- **4 moments** (all self-contained hook+payoff): (01) "God does all the work"
  — all good outcomes are God's mercy, not our own (24.6s, Gen-Z band); (02)
  the Lord steps down from His chariot to greet Brahma and embraces him in
  wordless silence (26.7s); (03) Vishwakarma, publicly accused by Indra,
  answers with humility instead of defensiveness (49.6s); (04) the closing
  moral + dedication shloka — give humbly, offer it to God, "Haraye Namah
  Shri Krishna Arpanamastu" (54.0s, the recurring closing-moral category).
- **Cut boundaries:** all placed with clip_cutter.py (cut_report_cand1-4.json).
  cand1 came back CLEAN on both ends; cand2/3/4 flagged review-manually (the
  usual coarse-run-on-cue pattern) and were each resolved by hand against the
  VTT word-level tags + direct silencedetect. One real catch: reel04's first
  pass started at source 3272.0s, which began mid-word inside "...salvation
  and saying" — caught by the odd-cut check + a word-tag read, corrected to
  3272.3s so the clip opens cleanly on the quote "What greater blessing...".
- **New Sanskrit terms added to the shared `tools/sanskrit_terms.py`:**
  `Srinivasa` (already used in ep06's reels via that slug's allowlist, a
  recurring confirmed channel spelling — promoted to the shared list) and
  `Vishwakarma` (standard single-spelling proper noun, the divine architect).
  The auto-caption's closing "Hare Namah" was NOT treated as a new term — the
  channel's confirmed spelling of that dedication phrase is already
  `Haraye Namah` in sanskrit_terms.py, so the subtitle uses that confirmed
  spelling (using an existing confirmed term, not inventing one). No uncertain
  spelling was guessed or burned in.
- **Numbering:** `next_reel_number('venkatachala-ep07')` returned 01 on the
  fresh slug's first build (01-04 assigned in order); the build scripts were
  then PINNED to those numbers afterwards (REEL_NUM 1-4) so re-running a script
  to tweak a subtitle doesn't re-increment to 05/06. (This exact re-increment
  DID happen once mid-session when reel01/04 were rebuilt to fix a British
  spelling and a mid-word start — it produced stale _05/_06 duplicates, which
  were then cleaned up by deleting the 2 superseded originals by exact filename
  and promoting the fixed builds into _01/_04.)
- **check_reel.py** (per-slug, imports shared inside_cue/load_cues from
  tools/clip_cutter.py — not reimplemented): all 4 PASS dimensions
  (1080x1920), duration, and spelling. Odd-cut WARNs are the documented coarse-
  cue false positives, each hand-verified.
- Preview frames extracted and inspected for all 4 (title clears the tilak,
  subtitle legible at SUB_Y=1560, watermark present, speaker centered, no
  collisions) PLUS the jump-cut-feel check: start/end frames confirm the whole
  composited frame (title + subtitle + watermark + background) fades together
  as one unit.

### Perceptual judgment (per clip, my own subjective pass — reviewer re-checks)
All 6 read as a smooth, deliberate fade rather than a hard jump cut:
ep06-05 smooth, ep06-06 smooth, ep07-01 smooth, ep07-02 smooth, ep07-03
smooth, ep07-04 smooth. See `work/build-notes.md` for the per-clip notes.

### Scope / guardrails
Nothing uploaded, deleted-on-channel, replaced, or privacy-changed on YouTube.
ep06 reels 03/04 (live) and venkatachala-ep01 were not touched. STYLE.md was
not edited (fade rule proposed pending confirmation in build-notes.md). No
wildcard deletes — the only deletions (ep06's 4 old abrupt files; ep07's 2
stale duplicate reels) were done by exact filename, stated before deleting,
and only after the replacements were verified. No Whisper/STT tooling
reintroduced.
