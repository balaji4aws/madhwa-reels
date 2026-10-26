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
