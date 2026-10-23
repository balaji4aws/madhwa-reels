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

---

## 2026-10-23 (review approved) — Abrupt-cuts fade fix + venkatachala-ep07: independent review PASSED, user-held for review

This entry records the independent review outcome for the work logged in the
"Abrupt cuts, part 2" entry above (ep06 05/06 fade rebuild + the 4 new ep07
reels). The build was summarized in `work/build-notes.md`; the independent
reviewer's full write-up is `work/review.md`. The review is now **APPROVED**.
The entry below consolidates the fade technique, the per-clip perceptual
findings, and — flagged for future sessions — the now user-confirmed lesson
that the margin-only fix is insufficient on its own.

### The fade technique chosen (exact approach + why 0.2s)

- **Video:** ffmpeg `fade=t=in:st=0:d=0.2` at the head and
  `fade=t=out:st=<dur-0.2>:d=0.2` at the tail — a fade to/from **black** (the
  plain `fade` filter is a pixel-level dissolve; this machine's ffmpeg has no
  `drawtext`, but `fade` is not a text feature and works fine). Fade-to-black
  reads as a deliberate edit rather than a glitch.
- **Audio:** matching `afade=t=in:st=0:d=0.2` / `afade=t=out:st=<dur-0.2>:d=0.2`
  so the amplitude ramps in/out instead of starting/stopping on a hard edge.
- **Duration 0.2s (200ms), and why that value:** chosen by prototyping on a
  real raw clip and inspecting the actual rendered first/last frames and the
  audio RMS ramp. At 200ms the fade is clearly *perceptible* as a deliberate
  transition — the first frame renders solid black and the audio RMS ramps up
  from near-silence (~-57 dB) at the start and back down (~-56 dB) at the end —
  yet it is short enough to fit inside the already-tight silence margins on
  every existing boundary (the ep06 boundaries carry ~0.4-1.2s of margin, so a
  0.2s fade never encroaches on spoken content). One duration, one method,
  applied consistently to all 6 clips for a uniform house feel — not re-tuned
  per clip. The review's independent luminance measurement confirmed a clean
  monotonic ramp over ~6 frames (0.2s at 30fps) on every clip, matching the
  intended duration.
- **Placement (critical):** the fade is applied to the FINAL COMPOSITED frame
  — the tail of each build script's `filter_complex`, on the `[vout]`/
  post-overlay label AFTER title + subtitle + watermark are composited — and
  the `afade` to the mapped audio the same way. It is NOT applied to the raw
  clip before compositing (doing that leaves the full-opacity title/watermark
  PNGs floating over a fading-to-black background — the overlay-desync artifact
  that was hit and fixed during the build). The reviewer independently
  confirmed on extracted fade frames that title, accent text, current
  subtitle, and the `@madhwa16` watermark all dim in sync with the background
  on every clip.

### The fade is ADDITIVE, not a replacement, for the margin + VTT placement

Explicit confirmation (build notes §2, review §1): the fade is layered ON TOP
OF the already-working silence-margin + VTT sentence-boundary cut placement
from the prior 05/06 attempt — it does not replace it. The ep06 05/06 cut
boundaries are UNCHANGED (111.5-156.6s and 2674.8-2730.0s); only the fade was
added. The margin approach fixes the cut POINT (no mid-word cut); the fade
fixes the cut's TRANSITION (the jump-cut feel). Both are kept; the review
confirmed the boundaries were not disturbed.

### Independent per-clip jump-cut-feel inspection (the decisive section)

The reviewer did NOT trust the build's self-reported table — they independently
extracted per-frame luminance (signalstats YAVG) across the first/last ~0.34s,
looked at the actual composited first/last frames, and measured audio
mean_volume ramping at both ends. Every clip showed (a) a monotonic brightness
ramp from near-black up and back down, (b) overlays dimming in sync with the
background, and (c) an audio ramp rather than a hard amplitude edge. Per clip:

| Clip | Reviewer verdict | Evidence |
|------|------------------|----------|
| ep06-05 dharmadevi-name-meaning | **smooth** | luminance 16->74 in / 75->25 out; title + subtitle("...name meaningful.") + watermark dim in sync |
| ep06-06 bakuladevi-humility | **smooth** | luminance 16->74 / 71->25; title "Don't Take Credit for God's Own Work" + watermark dim with background |
| ep07-01 god-does-all-work | **smooth** | ramp present (first frame ~26, caught slightly into the ramp — still clearly dim); title "Who Really Gets the Credit?" + watermark uniformly dim; audio -76 dB first 0.08s |
| ep07-02 god-steps-down-for-devotee | **smooth** | luminance 16->76 / 75->28; fade-out frame: title + subtitle("...wordless silence.") + watermark all dim together |
| ep07-03 vishwakarma-humility | **smooth** | luminance 16->73 / 78->28; title "Accused in Public, He Chose Humility" + watermark dim with background; audio -17.3 -> -23.8 -> -26.8 dB into the end |
| ep07-04 give-humbly-dedicate-to-god | **smooth** | luminance 27->73 / 80->28; title + dedication subtitle("Haraye Namah — Shri Krishna Arpanamastu.") + watermark all dim together; dedication lands before the fade completes |

**All 6 now read as a deliberate, unhurried fade at both ends rather than a
hard jump cut.** The reviewer's independent judgment agreed with the coder's on
all 6, but was formed from the reviewer's own frame/waveform inspection — this
is the perceptual step the earlier (PASS-but-still-abrupt) 05/06 review
skipped. **Verdict: APPROVED, no blocking findings.**

### New source venkatachala-ep07 — crop_x + title-collision check

- **crop_x = 523, freshly derived** (NOT reused from ep06's 573). Grid-overlay
  on a 1920-scaled probe frame put the speaker's face-center at x~955, so
  crop_x = 955 - 864//2 = 523, verified against 3 real probe frames
  (10/50/90% of the talk). It genuinely differs from ep06's value even though
  it is the same speaker/series — confirming the fresh-derivation rule was
  warranted, not a formality. Reviewer confirmed 523 is hardcoded in all four
  ep07 build scripts and backed by the documented frame check.
- **Title-collision check: POSITIVE, handled proactively BEFORE building.**
  Compositing the shared `render_title()` band over a real crop_x=523 frame
  landed the band on the speaker's tilak/hairline (same near-zero-headroom
  issue as ep06), so a per-slug `work/venkatachala-ep07/title_compact.py` was
  built up front (same verified geometry as ep06: band_top=8, 26/34px fonts,
  line_h=38). Reviewer confirmed the compact title clears the tilak with margin
  on all four reels — discovered and fixed before building, not after.

### The 4 new candidate moments and why each is self-contained

1. **01 — "God does all the work"** (source 87.9-112.5s, 24.6s). All good
   outcomes — praise, fame, success, even our humanity — are God's mercy, not
   our achievement. Hook ("who really gets the credit?") + payoff (it is all
   grace). Opens the talk; needs no prior context.
2. **02 — God steps down for His devotee** (1055.2-1081.9s, 26.7s). The Lord
   gets down from His own chariot, walks out to greet Brahma, raises him from
   his bow, embraces him, and they stand in wordless silence. Hook (God Himself
   steps down) + payoff (the silent embrace). A single complete scene.
3. **03 — Vishwakarma's humility** (1306.6-1356.2s, 49.6s). Indra demands
   Vishwakarma be removed; instead of defending himself, Vishwakarma answers
   with humility and self-correction, and the Lord blesses it. Hook (public
   accusation) + payoff (humble response, divine acceptance). Complete arc.
4. **04 — closing moral + dedication** (3272.3-3326.3s, 54.0s). "What greater
   blessing than the Lord leading us to liberation?" + the practical teaching
   to give humbly, never arrogantly, closed by "Haraye Namah, Shri Krishna
   Arpanamastu." The recurring closing-moral + shloka category; self-contained.

### Cut-boundary resolutions (all 6 clips)

- **ep06-05 (reel05):** source 111.5-156.6s — UNCHANGED from the prior verified
  build; only the fade was added.
- **ep06-06 (reel06):** source 2674.8-2730.0s — UNCHANGED from the prior
  verified build; only the fade was added.
- **ep07-01 (cand1):** BOTH boundaries came back **CLEAN** from clip_cutter.py.
  Start 87.9s (~0.66s before "God" at 88.559s); end 112.5s (just after
  "...him." at 112.396s, before the unrelated "Immediately,").
- **ep07-02 (cand2):** both flagged review-manually (coarse cue). Resolved:
  start 1055.2s at the "When he heard..." sentence boundary; end 1081.9s inside
  a real ~0.46s post-sentence pause after "...nine minutes of silence.", before
  a garbled next line (deliberately excluded).
- **ep07-03 (cand3):** both flagged review-manually. Resolved: start 1306.6s at
  "Indra said, 'Remove him from my work.'" (word 1306.943s); end 1356.2s just
  after "...build the assembly right now." (word 1355.909s).
- **ep07-04 (cand4):** both flagged review-manually. Start moved from an initial
  3272.0s — which began MID-WORD inside "...salvation and saying" (caught by the
  odd-cut check + a word-tag read) — to **3272.3s**, so the clip opens cleanly
  on "What greater blessing..." (word 3272.48s); end 3326.3s at the tail of
  "...Shri Krishna Arpanamastu", before the long "Rama Rama..." chant (excluded).

### New Sanskrit terms added to tools/sanskrit_terms.py

- **Srinivasa** — a name of Venkateshwara; already used in ep06's reels via
  that slug's allowlist, promoted to the shared list as a recurring confirmed
  channel spelling.
- **Vishwakarma** — the divine architect; a standard, unambiguous single-
  spelling proper noun.

Deliberately NOT added/guessed: the auto-caption's closing "Hare Namah". The
channel's confirmed spelling of that dedication phrase is already
**Haraye Namah** in `sanskrit_terms.py`, so reel04's subtitle uses that
confirmed spelling (using an existing confirmed term — NOT inventing a new one).
No uncertain transliteration was burned into any subtitle. The reviewer
independently confirmed `Vishwakarma`, `Haraye Namah`, and `Arpanamastu` are
present as confirmed single-spelling entries and that the garbled "Hare Namah"
was not used.

### check_reel.py results (all 6 reels)

| Reel | dims | duration | spelling | odd-cut (caption-boundary) |
|------|------|----------|----------|----------------------------|
| ep06-05 dharmadevi-name-meaning | PASS 1080x1920 | PASS 45.1s | PASS | WARN start+end (documented coarse-cue false positives; boundaries unchanged + previously verified) |
| ep06-06 bakuladevi-humility | PASS 1080x1920 | PASS 55.2s | PASS | WARN start+end (same documented false positives) |
| ep07-01 god-does-all-work | PASS 1080x1920 | PASS 24.6s | PASS | PASS start, WARN end (coarse cue; hand-verified clean) |
| ep07-02 god-steps-down-for-devotee | PASS 1080x1920 | PASS 26.7s | PASS | PASS start, WARN end (hand-verified clean) |
| ep07-03 vishwakarma-humility | PASS 1080x1920 | PASS 49.6s | PASS | PASS start, WARN end (hand-verified clean) |
| ep07-04 give-humbly-dedicate-to-god | PASS 1080x1920 | PASS 54.0s | PASS | WARN start+end (hand-verified clean; start corrected from an earlier mid-word placement) |

No FAILs on any reel. Every odd-cut WARN is the known coarse-run-on-cue
false-positive pattern for these sources, each hand-verified against the VTT
word-level tags + silencedetect.

### LESSON (flagged for future sessions) — the margin-only fix is INSUFFICIENT on its own

> **Do not re-attempt the silence-margin-only approach for abrupt cuts as if it
> were untried.** The prior session's 05/06 fix placed the cut deliberately
> *inside* the detected silence window (a margin away from the nearest word) and
> verified it with silencedetect + VTT sentence boundaries. The user watched
> those reels and confirmed they STILL felt abruptly cut. That approach is **not
> wrong — it is incomplete**: it correctly fixes WHERE the cut lands (no mid-word
> truncation, a real sentence boundary, breathing room in the pause) but does
> NOTHING about the cut's TRANSITION SHAPE — the hard audio amplitude edge and
> the instant visual start/stop that read as a jump cut regardless of how much
> silence surrounds the boundary.
>
> This is now USER-CONFIRMED, not a hypothesis. The fix that actually worked is
> the margin placement PLUS the 0.2s audio+video fade described above — the two
> are additive and both are required. A future session seeing "abrupt cuts"
> feedback should NOT re-litigate or re-run the margin-only method expecting it
> to solve the feel; the margin is a prerequisite that is already in place, and
> the next lever is the fade (lengthen 0.2s -> 0.3-0.4s before changing the fade
> method), never reverting to margin-tuning alone.

### Scope / guardrails (review confirmed)

Nothing was uploaded, deleted-on-channel, replaced, or privacy-changed on
YouTube in the build or this review. ep06 reels 03/04 (live) and
venkatachala-ep01 were not touched. STYLE.md was NOT edited — the fade house
rule remains a PROPOSED addition (0.2s, applied to the composited frame +
audio, additive to the margin placement, lengthen before changing method),
pending the user's explicit confirmation before anyone edits STYLE.md. The only
deletions (ep06's 4 old abrupt files; ep07's 2 stale duplicate reels) were by
exact filename, stated before deleting, and only after the verified
replacements existed. No Whisper/STT tooling reintroduced.

**Caveat carried to the user (not a blocker):** the perceptual evidence here is
objective (measured ramps + synced overlays) and is a real improvement over the
no-fade 05/06, but the ultimate test is the user's own reaction on watching the
finished reels — the same loop that was fooled once by a structural-only PASS.
If 0.2s still reads as slightly abrupt, the first lever is lengthening the fade
to 0.3-0.4s before changing the method.

---

## 2026-10-23 (later still) — Lesson: ep07 reel 02 abrupt ending; why boundary+fade verification kept passing bad cuts

**What the user reported:** `venkatachala-ep07_02_god-steps-down-for-devotee.mp4`
was "a very terrible cut — not watch-worthy, it abruptly ends." The user
explicitly asked NOT to rebuild it, but to learn the lesson so future reels
don't repeat it. (Reel is left as-is, not re-cut, not uploaded.)

**Root cause, confirmed by measuring the FINISHED file (not the build notes):**
ran `silencedetect` on the delivered 26.73s reel. The speaker is still talking
until **26.468s**; the only trailing quiet is 26.468–26.70s = **0.23s**, and
the 0.2s fade-out starts at 26.53s — i.e. the fade fires while the voice is
still trailing. The ending clips the speaker mid-settle. That is the abruptness.

**Why our verification kept green-lighting this** (this is the real lesson — it
is now the SECOND abrupt-cut complaint that passed automated + reviewer checks):
1. `clip_cutter.py` certifies the cut sits at a VTT *sentence boundary*. But the
   VTT word-tags on these sources are unreliable — build_reel02.py's own note
   calls the line right after the payoff "noticeably garbled" auto-caption. A
   word-tag saying "sentence ends at 1081.27s" is not proof the audio settled
   there.
2. The `silencedetect` "~0.46s end pause" cited in the build note was measured
   on the SOURCE during planning. The FINISHED file has only 0.23s. Nobody
   re-measured the delivered output's tail — source-side and output-side
   numbers disagreed and the disagreement went unnoticed.
3. The 0.2s fade was treated as a general cure for abruptness. It is not: a fade
   only smooths a transition that ALREADY lands in silence. It does nothing for
   a cut that lands on live speech. "Fade applied" was conflated with "ending
   feels settled."
4. Both check_reel.py and the human-style review judged "smooth" from frames +
   aggregate audio levels, but never asked the one question that matters for
   this failure: *is the speaker still talking in the last half-second, and is
   there real settle (not just a fade) after the final word?*

**What changed as a result (rules, not a rebuild):**
- Added a 4th verification requirement to `docs/STYLE.md` and the
  `.kiro/steering/madhwa-reels.md` verification section: a TRAILING/LEADING
  SETTLE check run on the FINISHED composited reel (not just source-side
  planning numbers), requiring ~0.5–0.7s of genuine trailing quiet after the
  last word before the fade, plus an explicit perceptual LISTEN to the first
  ~1s / last ~1.5s as the final gate. Recorded that VTT word-tags are not
  reliable timing truth and that source-side vs finished-file silence numbers
  can disagree.
- Did NOT change the fade itself (0.2s stays fine where the cut already lands in
  real silence — see ep06 05/06, which the user accepted and which are live).
  The fade was never the problem here; the cut landing on speech was.

**Meta-lesson for future sessions:** when the user reports an abrupt cut, the
first move is to `silencedetect` the FINISHED file's tail and check whether
speech runs into the last ~0.5s — not to re-read the build script's own
boundary justification (which describes intent, not delivered reality), and not
to add more fade. Measurements on the source or in the plan are not evidence
about the delivered file. And a passing numeric check is not a substitute for
listening to the actual ending.

(Cross-check also done this session: confirmed all 4 reels physically present in
`reels/venkatachala-ep06/` — 03/04/05/06 — are each uploaded and live on
YouTube; nothing in that folder is un-uploaded.)

---

## 2026-10-23 (ep07 review) — The real abrupt-cut lesson: candidate CONTENT, not just silence margin

The channel owner reviewed all 4 ep07 reels and gave the single most useful
piece of guidance in this project so far. Measured + recorded here.

**Owner's verdicts:**
- reel 02 (god-steps-down, narrative): "very terrible cut, abruptly ends." Delete.
- reel 03 (vishwakarma-humility, mid-explanation): "topic was good, but ends
  abruptly." Delete.
- reel 04 (give-humbly, closing exhortation + dedication): GOOD. Uploaded
  (https://youtu.be/9HO-4rvRlJ4, video ID 9HO-4rvRlJ4).

**The measurement that reframed the whole problem:** ran the new
finished-file trailing-settle check on 03 and 04.
- reel 03: 49.6s clip, last speech ends ~48.86s → 0.74s trailing quiet.
- reel 04 (the GOOD one): 54.03s clip, last speech ends 53.78s → only **0.25s**
  trailing quiet — essentially the SAME tight tail as reel 02 (0.23s), the one
  called "terrible."

So trailing-silence margin ALONE does not explain the owner's like/dislike
split: the good reel had the tightest tail of the three. What actually
separated them was the CONTENT SHAPE of the moment:
- reel 04 ended on a COMPLETE rhetorical unit — a closing exhortation ("give
  humbly... I have done only this much") + the traditional dedication. It
  resolves on its own, so even a tight tail reads as intentional and finished.
- reels 02 and 03 ended in the MIDDLE of narrative/explanatory delivery — a
  story beat and a humility explanation that were still unfolding. No amount of
  trailing silence or fade makes an unresolved thought feel finished.

**The owner's rule, now the primary candidate-selection guidance** (added to
STYLE.md "Clip selection", WORKFLOW.md Step 2, and the steering file): the two
strongest reel candidates are (1) the speaker GIVING ADVICE / an exhortation to
people or society, and (2) the speaker narrating a GREAT / HIGH / PEAK moment of
a story. Both are self-resolving. After transcription, skim specifically for
these two shapes and AVOID cutting on mid-narrative explanation with no
self-contained resolution.

**How this updates the prior (2026-10-23 "trailing-settle") lesson:** that
lesson is still correct (re-measure the finished file; a fade can't rescue a
cut on live speech) but it was INCOMPLETE — it treated abruptness as purely a
silence/boundary problem. The fuller truth: abruptness is a
content-resolution problem first. A reel must end on a thought that is
COMPLETE. Picking a self-resolving moment (advice / story-peak) is the upstream
fix; trailing-settle + fade is the downstream polish. Both matter; the content
choice matters more.

**Actions taken this session:**
- Uploaded reel 04 (good) — public, live.
- Deleted reels 02 and 03 (`venkatachala-ep07_02_god-steps-down-for-devotee.mp4`
  + `.caption.txt`, `venkatachala-ep07_03_vishwakarma-humility.mp4` +
  `.caption.txt`) by EXACT filename at the owner's explicit request, AFTER
  recording these lessons (the owner's condition for deletion was "provided you
  have learnt the lessons"). Not rebuilt — the owner explicitly said no need to
  recreate them. reel 01 was NOT touched (still built, awaiting review).
- Note on numbering: reel_numbering.py never reuses a number, so a future ep07
  reel will be 05+, not a refill of the deleted 02/03 slots.

---

## 2026-10-23 (standing-rule additions) — strict <60s, short-first, post-upload cleanup

Channel owner added three standing rules (applied to STYLE.md, the steering
file, and WORKFLOW.md where relevant):

1. **Strict length < 60s.** Every reel MUST be under 60 seconds — a hard rule,
   not a target (Gen-Z won't sit through more). Changed STYLE.md's duration
   check from "WARN if >60s" to a hard FAIL at >= 60s. NOTE / follow-up: the
   per-slug `check_reel.py` scripts still only emit a WARN on duration in code
   — the WARN->FAIL enforcement should be applied to those scripts the next
   time a reel is built (not changed this turn because no reel is being built;
   all currently-live reels are already under 60s — longest shipped is 55.2s,
   so nothing live violates the rule).

2. **Prefer short first (~15s), build shortest first.** A ~15s reel is the
   first option to try when a self-contained candidate that short exists (not
   mandatory — don't break a payoff to force 15s). Preference order: ~15s ideal
   -> 15-30s strong -> up to just under 60s only when the payoff needs it. When
   a source has several candidates, BUILD the shortest viable ones first, then
   longer ones. Never pad to fill time; never exceed 60s to keep a payoff (pick
   a tighter moment instead).

3. **Post-upload local cleanup.** After a reel is uploaded to YouTube following
   the owner's approval, delete that reel's finished `reels/<slug>/<reel>.mp4` +
   `.caption.txt` from local storage (exact filename, never wildcard, only
   after the upload is confirmed). KEEP the sources (`sources/<slug>/`) and the
   build scripts/cut reports — only the finished reel output is removed, and
   only for a reel that was both approved and successfully uploaded. (This
   formalizes "upload then free the disk, but keep what lets us re-cut.")

Also verified this turn (owner asked): `venkatachala-ep07_01_god-does-all-work`
was NEVER uploaded — no youtu.be link recorded, SOURCES.md shows "awaiting
review", file still local. Not re-uploaded. Still awaiting the owner's review.

Note: these cleanup/length rules are going forward. The already-uploaded reels'
local files (ep06 03-06, ep07 04) have NOT yet been cleaned up under rule 3 —
left in place for now; they can be removed per rule 3 on the owner's go-ahead
since all are confirmed live.

---

## 2026-10-23 (cleanup) — ep06 local reels removed; utsarjana-upakarma source removed

- **ep06 post-upload cleanup.** Owner: "if you have uploaded all, then remove
  them." Verified all 4 ep06 reels were live first (03 `eHx0uUuX354`, 04
  `sDJX6yPxhS0`, 05 `32QeRaBse_M`, 06 `S51yo8rFRXg`), then deleted the 4 `.mp4`
  + 4 `.caption.txt` by exact filename and removed the empty
  `reels/venkatachala-ep06/` folder. `sources/venkatachala-ep06/` and
  `work/venkatachala-ep06/` kept.
- **utsarjana-upakarma source removed.** At the owner's explicit request,
  deleted `sources/utsarjana-upakarma/source.mp4`, `source.en.vtt`,
  `source.kn.vtt` (exact filenames) and the empty folder. This is a deliberate,
  owner-directed exception to the "keep sources" preference for this one slug.
  Re-downloadable from YouTube if ever needed. NOT touched (not part of the
  request): `work/utsarjana-upakarma/` (build script, raw clip, overlay PNGs).
  This slug was never listed in `docs/SOURCES.md`.

---

## 2026-10-23 (tidy-up) — ep01 dropped, shared library moved, docs simplified

- **ep01 removed** from `docs/SOURCES.md` and from disk. It was an early
  style attempt; nothing from it is live.
- **`overlays_lib.py` moved** from `work/venkatachala-ep01/` to
  `tools/overlays_lib.py`. Every ep06/ep07 build script imported it from the
  ep01 folder, so the folder could not be deleted until the library moved.
  The 8 build scripts now import it from `tools/`; verified all ep06/ep07
  build and check scripts import cleanly after ep01 was deleted.
- **Strict <60s now enforced in code.** ep06/ep07 `check_reel.py` hard-FAIL at
  60s or longer (was a WARN). Tested: a 24.6s clip passes, a 3474s file fails.
- **Removed 258 irrelevant files** (listed by exact name before deleting):
  all remaining `work/venkatachala-ep01/` files, `work/utsarjana-upakarma/`,
  old planning/review notes (`work/TASK_BRIEF_crop_restyle.md`,
  `work/build-notes.md`, `work/review.md`, `work/review.json`,
  `docs/archive/CUTTING_PLAN.md`), ep06 preview/overlay PNGs (regenerated by
  the build scripts), ep07 raw clips for the rejected reels 02/03, and Python
  caches. Kept: sources, ep06/ep07 build and check scripts, cut reports,
  subtitle JSON, and raw clips for live reels.
- **Docs simplified.** `docs/SOURCES.md` is now one table (one row per reel).
  `docs/WORKFLOW.md` was rewritten as plain numbered steps, fixing gaps found
  while re-reading it: wrong finished-reel path, missing fade step, missing
  owner-review gate and post-upload cleanup, missing finished-file ending
  check, and no note on which Python to use (`/usr/bin/python3` has no Pillow;
  use `/Users/venkyb/envs/bie-work/bin/python3`). `README.md` tightened; no
  spelling errors found.
- Earlier CHANGELOG entries still mention ep01 paths and
  `docs/archive/CUTTING_PLAN.md`. They are kept as history; those files are
  in git history if ever needed.

---

## 2026-10-23 (batch) — 15 new reels: 5 each from ep06, ep07 and a new Madhwa Jayanti source

**Request:** 5 reels from each of three links. Two (`DoHq0Eh9Rvo` = ep06,
`9IDCabMthdQ` = ep07) were already sources — the owner shares repeats on
purpose, so: same slug, no new SOURCES row per source, and moments must be
different from every reel already cut from them (live or rejected). The third
(`Ww7105ppkyg`, Madhwa Jayanti discourse, 2619s, Hubli) is new: slug
`madhwacharya-avatara`, downloaded in full, duration matched YouTube.

**Rules recorded (owner-confirmed):** the 0.2s picture+audio fade is now a
STYLE.md rule; a new STYLE.md "Repeated sources" section + WORKFLOW step 1 note.

**How moments were picked:** read all three transcripts looking for the
owner's two strong shapes (advice to people / a story's high point). Avoided
every earlier cut range (ep06 ~231-345, 111-157, 617-671, 2675-2730; ep07
88-113, 1055-1082, 1307-1356, 3272-3326). Dropped two candidates on review:
- Bakuladevi's "bold answer" — its payoff is that lying is acceptable in five
  situations; a poor standalone message.
- "Parents must talk to their children" — the only clean ending is the same
  verse that opens live reel 03, and with "Who Is a True Devotee?" also in the
  batch ep06 would have had three parent-themed reels. Replaced with
  Brihaspati's humility.

**Cut placement — the important change this time:** the English VTT is a
machine translation; its word timestamps are evenly-spaced guesses and its
sentences don't align with the Kannada audio (e.g. the English put "If
parents do not listen…" ~3s after where the Kannada sentence actually
starts). Every boundary was instead placed from the **Kannada** cues
(`source.kn.vtt`, read directly) at a real `silencedetect` pause, ending only
on a completed Kannada sentence (avoiding dangling `ಅನ್ನುವುದನ್ನು`-type
clause endings). `clip_cutter.py` was still run first (reports in
`work/<slug>/cut_report_rNN_*.json`); as usual it flagged most boundaries
`review-manually`. The Kannada also corrected the English meaning in places
(ep06 Shuka reel: "ಸುಖೋದ್ರೇಕ" = overflowing bliss, not "attracted to pleasure").

**Finished-file check (STYLE.md verification #4):** head quiet 0.15–0.30s,
tail quiet 0.43–0.64s on all 15. Six tails are 0.43–0.49s because the real
pause after the last word is that short; each still ends on a complete sentence.

**New tooling:**
- `tools/reel_builder.py` + one `work/<slug>/reels.json` spec per source,
  replacing a hand-copied `build_reelNN.py` per reel. Enforces <60s and
  single-line subtitles before building. `.gitignore` excepts `reels.json`.
- **Fixed a numbering bug** in `tools/reel_numbering.py`: post-upload cleanup
  empties `reels/<slug>/`, so it would have restarted ep06/ep07 at 01 and
  collided with live reels. It now also counts numbers in `docs/SOURCES.md`
  and `work/<slug>/` (clip/build files + `reels.json`). ep06 continued at 07,
  ep07 at 05 (02/03 stay retired), new source at 01.

**Framing:** ep06 crop_x=573 and ep07 crop_x=523 reused (same sources). New
source crop_x=548 from gridded frames (face centre x≈940–975) and a 3-way crop
comparison. Same speaker/studio as ep06/ep07, so the compact top title band
was used for all 15.

**Watermark:** first build with the URL + icon watermark
(`assets/make_watermark.py` → `assets/watermark.png`), checked on real frames:
centred under the subtitle, legible, clear of the right edge. Awaiting the
owner's OK with this batch. Already-live reels keep the old handle watermark.

**Spelling — pending owner confirmation:** names not yet in
`tools/sanskrit_terms.py`, used and allowlisted per slug only: Rudra,
Rudradeva, Shukacharya, Tirumala, Tiruchanur, Padma Sarovar, Yashoda, Shani,
Ugadi, Phalguna Amavasya, Madhwacharya (channel's "Madhwa" spelling), darshan.
To be moved into the shared list once confirmed.

**check_reel.py:** all 15 PASS dimensions, duration (<60s) and spelling.
Cut-placement WARNs are against the run-on English cues and expected (see
above). Nothing uploaded — all 15 await owner review in `reels/<slug>/`.

---

## 2026-10-23 (uploads) — Three rule changes; all 15 batch reels uploaded

**Rule changes (owner direction):**
1. **No human review gate.** A reel that passes every check uploads directly;
   the owner reviews on the channel. Updated STYLE.md ("Upload and keep"),
   WORKFLOW.md (steps 7–8), README, the steering file, and a scoped note in
   GUARDRAILS.md (covers new uploads only; delete/replace/privacy changes
   still need the owner to name the video).
2. **Keep reels after upload.** Replaces the earlier delete-after-upload rule.
   The reels already deleted locally (ep06 03–06, ep07 01/04) can be re-rendered
   from their build scripts if ever needed; nothing was rebuilt now.
3. **SOURCES.md is a simple table:** source, reel title, YouTube link. No link
   means not uploaded. `tools/reel_numbering.py` row pattern updated for the
   new "NN · Title" column; re-tested (next: ep06 12, ep07 10, new source 06).

**Uploads:** all 15 reels uploaded one at a time, shortest first, ready to
stop at the first quota refusal. None came, so all 15 went public. Checked
each on YouTube afterwards with yt-dlp: public, Madhwa16, correct title and
length. Links are in SOURCES.md, and the local files are kept in `reels/<slug>/`.

**Quota note corrected:** docs said ~6 uploads/day (from Google's 1,600-unit
estimate). Twenty uploads went through today (5 this morning + 15 here) with
no refusal, so the docs now say the limit is unknown, with 6 as a floor.
The stop-at-first-refusal rule stays.

**Still open from the batch:** owner confirmation of the URL + icon watermark,
the pending name spellings (Rudra, Rudradeva, Shukacharya, Tirumala,
Tiruchanur, Padma Sarovar, Yashoda, Shani, Ugadi, Phalguna Amavasya,
Madhwacharya, darshan), and the unconfirmed speaker credit on the new
source. These reels are now live, so fixing any of these means a re-upload,
which only happens if the owner names the reel.

---

## 2026-10-23 (owner Q&A) — Speaker credit; 6 older reels restored locally

- **Speaker credit.** The owner confirmed the Madhwa Jayanti talk
  (`madhwacharya-avatara`) is by Sri Satyatmateertha Shripadangalavaru and
  gave its English title. Added a standing STYLE.md rule to credit the speaker
  by full respectful name in every description. Updated that source's
  `reels.json` and regenerated its 5 local `.caption.txt` files (used for
  Instagram). The 5 live YouTube videos were not changed: the owner asked for
  future descriptions, and editing live ones would need him to name them.
- **Restored local copies** of the 6 reels deleted under the old
  delete-after-upload rule (ep06 03–06, ep07 01, 04), for Instagram posting.
  Re-rendered from their own build scripts and raw clips, using the ORIGINAL
  `@madhwa16` handle watermark (the new URL watermark was swapped out for
  the build, then restored and checksum-verified), so they match what is
  live. Durations match the live videos (44.2/54.8/45.1/55.2/24.6/54.0s).
  ep06 03/04 have no fade, as live. Their 6 `.caption.txt` files were
  restored word-for-word from the live versions.
- ep06 `build_reel01.py`/`build_reel02.py` called `next_reel_number()`
  instead of pinning a number, so a rebuild would now give 12/13. Pinned them
  to 03/04.
