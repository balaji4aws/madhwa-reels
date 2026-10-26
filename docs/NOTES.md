# NOTES: ASR study (26 Oct 2026)

Question: would the ASR in the sibling repo `madhwa-pravachana-RAG` give the
reel pipeline a better Kannada transcript, better context, and so better reels?

Verdict: **a small yes, not a big one.** Use it only where it clearly beats
YouTube's captions (shlokas). Do not switch the whole pipeline to it.

## How the study was done

- Ran the RAG repo's own code (`pravachana.transcribe`, `pravachana.fuse`) on
  three clips of our talks. Read-only: nothing written to the RAG repo, nothing
  downloaded (`PYTHONDONTWRITEBYTECODE=1`, `HF_HUB_OFFLINE=1`). Outputs in
  `/tmp/madhwa/asr_study/` (temporary).
- Python: `madhwa-pravachana-RAG/experiments/.nemo-venv` (3.12).
- Models used: Indic-Transcribe-core (writes the text) and IndicConformer-600M
  (silence gate, verse detector).
- Clips (16 kHz mono): ep06 340-580s (parents advice, "Nachamatrasamam" shloka),
  ep06 1850-2090s (Shukacharya dance, the prayer at ~1946s), satyaparayana-mahime
  380-530s (Ramanna / Tammanna Nayaka story).
- Compared with YouTube's `source.kn.vtt` for the same seconds.
- Speed: ~15 s per 4 min of audio for the main model; the repo's own estimate
  is ~30 min end to end for a 2-hour talk.

## Findings

1. **Plain Kannada speech: no real gain.** The satyaparayana story matched
   YouTube's captions almost word for word. The ASR text is cleaner (fewer
   fragments) but made a few errors the captions did not: "ಇಂದ್ರಾಜ" for
   "ಇಂದ್ರಾದಿ", and "ಹಳೆಯನನ್ನಾಗಿ" where the meaning looks like "ವಶನನ್ನಾಗಿ".
2. **Shlokas: clear gain.** YouTube's captions garble or drop verses. For the
   Shukacharya prayer YouTube gave "ಭವತವೀಕ್ಷತಯಸ್ತುತರರ್ಜಿತ" then a ~5 s blank.
   The ASR gave "ಭವತಾ ವೀಕ್ಷತೆ ಯಸ್ತು ತಸ್ಯ ತ್ವದ್ಭಕ್ತಿರೂರ್ಜಿತ ಉಪೇಕ್ಷತೆ ಚ ಯಸ್ತಸ್ಯ
   ಭೋಗೇಚ್ಛಾ ಚಾಭಿಜಾಯತೆ", which reads as the real verse. It also recovered the
   Bhagavata verses "ದಿಗಂಬರಂ ವಕ್ರ ವಿಕಿರಣ ಕೇಶಂ…", "ಆತ್ಮಾರಾಮಾಶ್ಚ ಮುನಯಃ…" and
   "ಭಿಂದನ್ ಕಮಂಡಲಂ…". Still not final: the RAG repo's own notes say about 8% of
   letters are wrong on Sanskrit, and all its shloka entries are pending human
   validation.
3. **The garbled caption line near 1946-1960s.** ASR: "ದಯಮಾಡಿ ನನ್ನ ಮೇಲೆ ಉಪೇಕ್ಷೆ
   ನೋಡಿದರೆ". My earlier reconstruction ("ನನ್ನ ಕಡೆ ನೋಡು") was wrong. The line is
   still hard to read as a clear thought.
4. **Timing: no gain.** Only segment-level timestamps (~10 s segments cut at the
   quietest point). No word timing. Cut placement stays with `clip_cutter.py`
   (silencedetect + caption cues).
5. **No hallucinated loops** were seen in these three clips (the RAG repo notes
   that another model, vasista22, invented text from silence).

## Limits of this study

- No human answer key, so accuracy was judged by comparing the two transcripts
  and by coherence. The RAG repo has not yet measured WER/CER either.
- Only ~10 minutes of audio, three clips, one speaker.

## What the RAG repo offers (read from its docs, not all tested)

- Native-script and Latin (ISO 15919 / IAST) transcripts.
- A Sanskrit shloka register `corpus/shlokas/SHLOKAS.txt` (all pending human
  validation).
- A BGE-M3 search index (one talk indexed so far).
- Its guardrails: never fill register entries, never trust ASR Sanskrit as
  final, do not change its rules. We did not modify that repo.

## Recommendation

- Add an optional ASR pass only for reels that contain a shloka, to get a better
  Kannada line for the subtitle. A human check on the Sanskrit is still needed.
- Keep YouTube's `source.kn.vtt` + `clip_cutter.py` as the default for
  everything else.
- Possible use for finding moments: the cleaner text and the search index could
  speed up reading a talk. Not tested for that.
- Whisper stays out of the project unless the owner asks again (see
  `CHANGELOG.md`, 2026-10-22 and 2026-10-24).

---

# NOTES: decisions from the owner (26 Oct 2026)

- **Speaker of satyaparayana-mahime** is Sri Satyatmateertha Shripadangalavaru
  (confirmed by the owner). Credit goes in those reels' descriptions.
- **Release rate: two reels a day, 6:00 AM and 6:00 PM IST.** Upload everything
  with `--schedule-daily`; YouTube releases on its own servers.
  `--reschedule-pending apply` re-packs still-scheduled reels.
- **Next batch: 5 reels from each of 5 unprocessed talks (25 reels):**
  `Ol7D66q3sLc`, `hFFv_MTKAsc`, `EKaIJrzpsGA`, `D6PdARDYLfk`, and
  `tNPyEd-FJ4I` (the old ep01, which has no live reels).
- Standing rules are in `STYLE.md`, `WORKFLOW.md`, `GUARDRAILS.md`.

---

# NOTES: cost of using the ASR (time, compute, storage), measured 26 Oct 2026

Question: does using the ASR models make reels slower to make, or faster? What
about compute power and disk space? This was NOT studied in the first round, so
it was measured afterwards on this machine (MacBook, Apple M4 Pro, 14 cores,
48 GB RAM, 163 GB free of 460 GB disk).

## Plain-words summary

- **The ASR makes reel-making slower and heavier, not faster.** Without it,
  getting a transcript takes about 6 seconds (YouTube captions, free). With it,
  a 30-minute talk takes about 3 to 7 more minutes on the machine, and needs
  about 17 GB of extra disk and about 9 GB of free memory while it runs.
- **It does not save any thinking time.** Picking the moments and writing
  subtitles is the slow part of making reels, and that is still done by reading.
  The ASR only gives segment-level times (about 10 seconds each), so the cuts
  still have to be placed with the YouTube captions plus the real silences.
- **It is only worth it for shloka lines**, where YouTube's captions are broken
  and the ASR is clearly better. For those, use it on just that clip, not on the
  whole talk.
- The thinking-time part is my estimate from doing the work, not a stopwatch.
  Every other number below was measured.

## Measured: time

| Step | Time |
|------|------|
| ASR on 630 s (10.5 min) of audio, including loading the models | 76 s total |
| ...of which model loading | about 11 s |
| ...of which transcribing (IndicConformer 25 s + Indic-Transcribe 40 s) | 65 s |
| ASR speed | about 0.10 s per second of audio (a 30-minute talk is about 3 min) |
| The RAG repo's own estimate for its whole pipeline (more steps than text only) | about 30 min per 2-hour talk, about 0.25 s per second |
| YouTube captions for one talk (download only) | about 6 s |
| Building one 27 s reel | about 14 s |
| Scanning a 30-minute source for glitches | about 23 s |
| Finding silences in a 30 s window | about 0.5 s |
| Downloading a full talk video | tens of seconds to a minute (the biggest machine step) |

Today's batch was 5 talks, 8,386 s (140 min) of audio:

- Machine time for the 25 reels **without** ASR: roughly 15 min in total
  (downloads about 3-4 min, scans about 2 min, 25 builds about 6 min, 25 uploads
  about 4 min).
- Adding the ASR to every talk: **+14 min** (text only, 0.10) to **+35 min**
  (full RAG pipeline, 0.25). That roughly doubles to triples the machine time.
  It can run in the background, so the wait is shorter than the sum, but it
  competes with the other work for the CPU.

## Measured: compute

- While running, the ASR used about 2.5 CPU cores on average (182 s of CPU in a
  76 s run) and a peak memory footprint of **9.1 GB** (resident 3.8 GB).
- This machine handles that comfortably (48 GB RAM). A smaller laptop (8 or
  16 GB) could struggle or swap while the video tools run at the same time.
- No GPU was needed on this machine for the speeds above (the repo's code picks
  the device itself; not looked into further).

## Measured: storage

| Item | Size |
|------|------|
| Indic-Transcribe-core model | 9.1 GB |
| IndicConformer-600M model | 4.8 GB |
| Sushrota (Sanskrit) model | 1.0 GB |
| Python environment for the ASR (`.nemo-venv` in the RAG repo) | 2.0 GB |
| **Total extra for ASR** | **about 17 GB** |
| For comparison: this whole reels project today | 7.1 GB (sources 3.5, reels 1.5, work 1.9) |
| Transcript output (JSON text) | a few hundred KB per talk, negligible |

So the ASR needs about 2.4 times the whole project's disk. (The shared model
cache also holds about 29 GB in total, including the RAG repo's search and
chat models. Those are not needed for reels.)

## What this means for the decision

- Not adopting the ASR for every talk is the right default: more time, more
  memory, more disk, and no time saved on the slow part of the work.
- Keep it as an optional step for a clip with a shloka (run it on that clip only:
  about 15 s for 4 minutes of audio), and still have the Sanskrit checked by a
  person.
- If the owner later wants full ASR transcripts of every talk (for example to
  build a searchable library), do it as a separate overnight job, not inside
  the reel-making flow.

## Rules that stay in force

- Do not change anything in the `madhwa-pravachana-RAG` repo; run its code
  read-only with `PYTHONDONTWRITEBYTECODE=1` and `HF_HUB_OFFLINE=1`.
- Do not install ASR packages into any shared Python.
- Whisper-style tools stay out of this project unless the owner asks.
- The helper that ran the study (`run_study.py`) was a temporary file and is not
  kept; the method is described at the top of this file.
