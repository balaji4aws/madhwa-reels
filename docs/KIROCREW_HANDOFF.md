# Hand-off to Kiro Crew: everything about the Madhwa Reels project

Written 2026-10-26 by the assistant that ran this project inside the Kiro IDE.
The project is moving to Kiro Crew. This file is meant to be enough for a new
assistant to carry on without asking the owner what already happened. Read it
top to bottom once, then use the cheat sheet (section 15) day to day.

Reading order for a new assistant:
1. This file.
2. `docs/GUARDRAILS.md` (things never to do) and `docs/STYLE.md` (how reels look).
3. `docs/WORKFLOW.md` (the pipeline) and `docs/SOURCES.md` (every reel + link).
4. `docs/NOTES.md` (the speech-to-text study) and `docs/CHANGELOG.md` (history,
   long; search it when you wonder why a rule exists).

---

## 1. What the project is

- The owner runs a YouTube channel, **Madhwa16** (https://www.youtube.com/@madhwa16/),
  of Madhwa / Dvaita devotional teachings.
- The assistant acts as the **video editor**: the owner shares a YouTube link to a
  long Kannada discourse (pravachana); the assistant downloads it, finds the strong
  moments, cuts each into a vertical 9:16 reel (under 60 s) with a title, English
  subtitles, watermark and fades, checks it, uploads it to YouTube Shorts, and
  schedules it. Instagram is posted by the owner by hand.
- All talks so far are by **Sri Satyatmateertha Shripadangalavaru** (Sri Uttaradi
  Math), published on the channel "Sri Uttaradimath Adhyatmavani".
- The owner is not a programmer. He wants short, plain-language answers, honest
  reporting (what was checked, what was not), and the quick question answered
  first when he asks several things.
- Everything lives in `/Users/venkyb/Documents/balaji4aws/madhwa reels/`.
  Git repo: https://github.com/balaji4aws/madhwa-reels (branch `main`). Only code
  and docs are in git; videos, secrets, and scratch are ignored.

## 2. Where things stand right now (2026-10-26, about 11:30 IST)

- **56 reels** on the channel: **23 public, 33 scheduled** (YouTube releases the
  scheduled ones by itself; the laptop can be off).
- **The last scheduled release is 2026-11-11, 6:00 PM IST. Nothing is scheduled
  after that. The next free slot is 2026-11-12, 6:00 AM IST.**
- Release rule: **two reels a day, 6:00 AM and 6:00 PM IST**. At two a day, the
  queue gives about 16 days of cover; new reels are needed to keep it full.
- Schedule order (all times IST):
  - 26 Oct 6 PM: ep05_01. 27 Oct 6 AM/6 PM: satyaparayana_03, ep05_05.
    28 Oct 6 AM/6 PM: satyaparayana_02, ep05_02. 29 Oct 6 AM/6 PM:
    satyaparayana_01, ep05_04. 30 Oct 6 AM: satyaparayana_05.
  - 30 Oct 6 PM to 1 Nov 6 PM: venkatachala-ep01 (5 reels).
  - 2 Nov 6 AM to 4 Nov 6 AM: ep02 (5). 4 Nov 6 PM to 6 Nov 6 PM: ep03 (5).
  - 7 Nov 6 AM to 10 Nov 6 AM: ep04 (7). 10 Nov 6 PM to 11 Nov 6 PM:
    madhwajayanti-sarkara (3).
  - The exact video IDs and dates are in `docs/SOURCES.md` and
    `upload/upload_log.tsv`.
- **Nothing is queued to build.** All ten source talks the owner has shared have
  been used. The next job is to ask the owner for new talk links (or look at the
  "unused moments" in section 12).
- Last commits are pushed. Working tree was clean at hand-off.

## 3. The ten sources (the "slug" is the short id used in every file name)

| Slug | YouTube id | Talk | crop_x | Reels | Look |
|------|-----------|------|--------|-------|------|
| venkatachala-ep01 | tNPyEd-FJ4I | Glory of Venkatachala, Ep 01 | 568 | 5 | v2 |
| venkatachala-ep02 | D6PdARDYLfk | Ep 02 | 518 | 5 | v2 |
| venkatachala-ep03 | hFFv_MTKAsc | Ep 03 | 513 | 5 | v2 |
| venkatachala-ep04 | Ol7D66q3sLc | Ep 04 | 568 | 7 | v2 |
| venkatachala-ep05 | 8lYvO6Z6d6c | Ep 05 | 513 | 5 | v2 |
| venkatachala-ep06 | DoHq0Eh9Rvo | Ep 06 | 573 | 9 (03 to 11) | older |
| venkatachala-ep07 | 9IDCabMthdQ | Ep 07 | 523 | 7 (01, 04 to 09) | older |
| madhwacharya-avatara | Ww7105ppkyg | Divine glory of Madhvacharya's incarnation | 548 | 5 | older |
| satyaparayana-mahime | STkFaeM7YQg | Glory of Sri Satyaparayana Teertha | 522 | 5 | v2 |
| madhwajayanti-sarkara | EKaIJrzpsGA | Government to celebrate Madhva Jayanti (announcement, 14 Oct 2026) | n/a (`reframe: fit`) | 3 | v2 |

Notes:
- `crop_x` is where the vertical crop starts in the 1920-wide frame. It is
  different for every source (speaker position). Never reuse another source's.
- "older" look = early reels (two-line Georgia title, Arial subtitles, old
  `@madhwa16` watermark on the first few). They were not rebuilt. "v2" = current
  look (section 7).
- ep06 numbering starts at 03 (its first two reels were numbered 03 and 04; no
  01/02 exist). ep07 reels 02 and 03 were rejected for abrupt endings and deleted
  from the channel. ep01 (the old first source) had earlier test reels that were
  deleted; its numbering was restarted at 01 for the October 26 batch. Reel numbers
  within a live source are never reused.
- ep06 is a 4K source (3840x2160, 25 fps); the builder scales every source to
  1920x1080 first, so `crop_x` is always in 1920-wide coordinates. The rest are
  1920x1080.
- `madhwajayanti-sarkara` is a 720x900 video of about 14 min where only the first
  ~155 s show the speaker; after that the screen is black. Only the first 150 s
  were used. It also shows a newspaper clipping (47 to 51 s) and the government
  order (64 to 66.6 s) full screen: those are real content (`glitch_ok`).
- The Kannada source titles are given in English in credits (`STYLE.md`).
- Speaker of `satyaparayana-mahime` was confirmed by the owner on 2026-10-26.
  `madhwajayanti-sarkara` is credited the same way (the same swamiji; the video
  title says it is his congratulation).

## 4. Machine and tools (what is installed, what is not)

- macOS, Apple M4 Pro, 14 cores, 48 GB RAM. Shell zsh. Today is Mon 2026-10-26.
- **Python for all build scripts:** `/Users/venkyb/envs/bie-work/bin/python3`
  (has Pillow 12). `/usr/bin/python3` has no Pillow and fails on overlays.
  zsh quirk: variables holding several words are not split; pass arguments
  explicitly.
- **ffmpeg/ffprobe 9.0.1: no `drawtext`, `subtitles` or `ass` filter** (no
  freetype/libass). All text is drawn as transparent PNGs with Pillow and laid on
  with ffmpeg `overlay`. Do not try `drawtext`; it fails.
- **yt-dlp** is installed. Always use `--cookies-from-browser chrome` (YouTube
  bot check). Always download the **full** video (never `--download-sections`).
- **Uploader venv:** `upload/.venv/bin/python` (Google API client). Never install
  Google or ML packages into a shared Python.
- **Credentials:** `upload/client_secret.json` and `upload/token.json` exist and
  are git-ignored. Never print or commit them. If one is ever shown, tell the
  owner to rotate it. The OAuth scope is the broad `youtube` scope so the script
  can also edit existing videos.
- **Fonts:** Noto Sans variable font in `assets/fonts/` (OFL licence). Georgia Bold
  and Arial Bold (system) are only for the old look. Do **not** use Amazon Ember
  (proprietary).
- **Speech-to-text (ASR):** the owner's separate project
  `/Users/venkyb/Documents/balaji4aws/madhwa-pravachana-RAG` has Kannada ASR. It
  was studied (section 11) and is **not** part of the flow. Do not modify that repo.
- Tool-call time limits: building 5 reels takes more than 2 minutes. In the Kiro
  IDE a 120 s limit applied; run long builds with a larger timeout or in the
  background.

## 5. Folder map

```
madhwa reels/
  README.md                  overview for humans
  docs/                      everything to read: STYLE, WORKFLOW, GUARDRAILS, SOURCES,
                             CHANGELOG, NOTES (ASR study), KIROCREW_HANDOFF (this file)
  tools/                     shared scripts (section 6)
  assets/                    watermark.png, make_watermark.py, brand icon, fonts/
  upload/                    youtube_upload.py, SETUP.md, schedule_ledger.json,
                             upload_log.tsv, client_secret.json + token.json (secret)
  sources/<slug>/            source.mp4, source.en.vtt, source.kn.vtt   (not in git)
  work/<slug>/reels.json     THE reel spec: cuts, titles, subtitles, captions (in git)
  work/<slug>/               clips, overlay PNGs, subs_NN.json (scratch, not in git)
  reels/<slug>/              finished <slug>_NN_<topic>.mp4 + .caption.txt (not in git)
```
Sizes now: project 7.1 GB (sources 3.5, reels 1.5, work 1.9). Disk has 163 GB free.
Keep all sources and reels (owner rule); delete nothing without the owner naming it.

## 6. The tools (all in `tools/`; run from the project folder)

| Tool | Use |
|------|-----|
| `reel_builder.py <slug> [NN ...]` | Builds reels from `work/<slug>/reels.json`: cuts the clip, reframes to 1080x1920, adds title, subtitles, watermark, 0.2 s fade, writes the `.mp4` and `.caption.txt`, scans for glitches, prints the real quiet at both ends. Refuses 60 s or longer, subtitles that do not fit on one line, and bad Kannada. About 14 s per reel. |
| `check_slug.py <slug> [NN ...]` | Checks every reel of a slug: 1080x1920, under 60 s, English spelling, trailing quiet at least 0.35 s, caption-boundary cut check. Exit 1 on a FAIL. Add unusual proper nouns to `EXTRA_NAMES` in this file. |
| `vtt2txt.py <vtt> [secs]` | Caption file to readable chunks with start seconds. Read a whole talk fast. |
| `cut_inspect.py <slug> <a> <b>` | Kannada cue lines + real speech pauses for a window. Use it to choose cut points. |
| `pauses.py <slug> <a> <b> [min]` | Finer pause list to check the exact tail of a planned cut. |
| `cue_rel.py <slug> <a> <b>` | Kannada and English cues with times relative to the cut. Use the Kannada times to time subtitles. |
| `frame_sheet.py out.png reel@sec ...` | Side-by-side frames. Look at them. |
| `upload_batch.py <slug> NN ...` | Uploads and schedules reels one by one, stops at the first failure, logs to `upload/upload_log.tsv`. |
| `spec_common.py` | Helpers used to write `reels.json` from code (`reel()`, `write()`). |
| `glitch_scan.py <video> [a b]` | Samples every frame at 5 fps for editor placeholders ("Missing File"), black or solid frames. |
| `kannada_check.py` | Kannada orthography check (hard-fails broken writing; lists words not in the source captions for human review). No full Kannada spell-checker exists on this machine. |
| `clip_cutter.py` | Snaps rough cut times to real pauses and checks them against caption cues. |
| `overlays_lib.py` | Draws title, subtitle, watermark PNGs and the crop reframe filter. |
| `fade_clip.py`, `reel_numbering.py`, `sanskrit_terms.py` | Fade helper, next free reel number, confirmed Sanskrit/Madhwa spellings. |

`upload/youtube_upload.py` options: `--schedule-daily` (next free 6 AM/6 PM IST
slot), `--next-slot`, `--publish-at ISO`, `--update-description ID --caption f`,
`--set-privacy ID --privacy ...`, `--delete ID`, `--replace OLD_ID file`,
`--reschedule-pending preview|apply`, `--yes` (skips the delete prompt). The
upload quota is unknown; 20 and then 25 uploads in a day went through. On the first
quota refusal stop and continue the next day.

## 7. The reel recipe (what every reel contains)

- 1080x1920, 30 fps, H.264, about 6 Mbps; AAC 192k. **Under 60 s: hard rule.**
  Average so far about 40 s (range 21 to 55 s); the owner said 30 s is good and
  15 s only when a moment allows. Do not force 15 s.
- **Reframe:** crop a vertical slice around the speaker (864x1080 scaled up) with a
  blurred mirror fill. Re-derive `crop_x` per source: grab a frame at about 300 s,
  draw a grid (`ffmpeg -vf drawgrid=w=100:h=100:t=1:c=yellow@0.5`), read the face
  centre x, `crop_x = face_x - 432`, then build one reel and look at it. The speaker
  moves a little during a talk; slightly left of centre is fine.
- **Non-16:9 source:** set `"reframe": "fit"` in `reels.json` (full width over a
  blurred copy, picture starts at y=170, ends above the subtitles).
- **Title** (top, one line, Noto Sans Bold 38 px, shrinks to 32): white lead words,
  saffron `#F5A623` main words. `title_lead` + `title_main` must fit one line at
  32 px: about 40 characters in all.
- **Subtitles: English only**, one line at a time, Noto Sans Bold 46 px, at y=1560.
  A line must fit one row (about 30 characters; the builder refuses longer).
  They are written by the assistant as short paraphrases of what is said, timed
  from the Kannada caption cue starts (`cue_rel.py`), clip-relative seconds, not
  overlapping, last one ending before the clip ends. Owner tried Kannada+English
  subtitles and went back to English only (the first version shrank the English
  to 36 px and looked blurry).
- **Watermark:** `assets/watermark.png` at y about 1700: brand icon + the full URL
  `https://www.youtube.com/@madhwa16`, Noto Sans Bold.
- **Fade:** 0.2 s in and out on picture and sound, applied after everything else.
- **Caption file** (`.caption.txt`): TITLE / DESCRIPTION / HASHTAGS. Title ends
  with `🙏 | Madhwa16` (the uploader adds `#Shorts`). Description is English, then
  the credit line `From "<talk>" by Sri Satyatmateertha Shripadangalavaru (Sri
  Uttaradi Math Adhyatmavani).`, then a **Kannada description**. Hashtags: English
  set including `#SatyatmateerthaShripadangalavaru`, then Kannada hashtags
  (`#ಕನ್ನಡ #ಪ್ರವಚನ ... #ಮಧ್ವ`). The Kannada text must pass `kannada_check`
  orthography (the builder enforces it). Type Kannada vowel signs carefully: a
  look-alike Devanagari sign once slipped in and had to be fixed.
- A Sanskrit shloka inside a clip: Kannada script on the Kannada line plus the
  English meaning (owner choice (a)). In practice the English-only subtitle shows
  the meaning; never guess a Sanskrit word.

## 8. The pipeline for a new source (step by step, with the commands used)

1. **Download** (full video + both caption tracks):
   `yt-dlp --cookies-from-browser chrome -f "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" --merge-output-format mp4 --write-auto-subs --sub-langs "kn,en,kn-orig,en-orig,en-kn,kn-en" --sub-format vtt -o "sources/<slug>/source.%(ext)s" "https://www.youtube.com/watch?v=<id>"`
   Delete `source.kn-orig.vtt` if it is identical to `source.kn.vtt`. Check the
   duration with ffprobe against the YouTube length.
2. **Glitch scan the whole source:** `python3 tools/glitch_scan.py sources/<slug>/source.mp4`
   (about 25 s per 30 minutes). Flags in the first 8 s and last 4 s are the
   uploader's intro and outro. Anything in the middle: do not cut across it, or
   cover with `hold_frames`, or mark `glitch_ok` if it is real content.
3. **crop_x:** see section 7. Make a slug (kebab-case).
4. **Read the talk:** `python3 tools/vtt2txt.py sources/<slug>/source.en.vtt 30`.
   The English is YouTube's machine translation, so treat it as a paraphrase.
5. **Choose moments.** Best: (a) the speaker **giving advice** to people, (b) the
   **high point of a story**. Avoid the middle of an explanation: it feels cut off
   whatever you do. A reel must end on a **complete thought**. Skip anything
   divisive or sensitive (two such passages were skipped in this batch, a cow
   slaughter remark in ep03 and a passage on what girls should be like in ep04);
   ask the owner when unsure.
6. **Place cuts from the Kannada captions and real pauses**, not the English:
   `python3 tools/cut_inspect.py <slug> <a> <b>`. Start at the **end of a pause**
   (right before a sentence begins). End **inside a pause**, about 0.5 s after the
   last word, so there is a real settle before the fade. Pauses of 0.4 s or more
   are listed; use `pauses.py` for finer ones. If no pause exists where the thought
   ends, move the end to the next real pause or pick another ending. The caption
   cue times can lag or lead by up to a second: the pauses are the truth.
7. **Time the subtitles:** `python3 tools/cue_rel.py <slug> <start> <end>` and write
   short English lines.
8. **Write `work/<slug>/reels.json`** (see an existing one; `tools/spec_common.py`
   helps). Fields: `slug, crop_x, look:"v2", speaker, source_title, source_url, note`
   and per reel `num, topic, start, end, title_lead, title_main, subs, caption{title,
   description, description_kn, hashtags, hashtags_kn}`; optional `hold_frames`,
   `glitch_ok`, and top-level `reframe`. Reel numbers: `reel_numbering.next_reel_number`
   (never reuse). Build the shortest candidates first.
9. **Build:** `python3 tools/reel_builder.py <slug>` (use the Pillow python). Read the
   line it prints per reel: duration, `quiet: head / tail`, glitch scan.
10. **Check:** `python3 tools/check_slug.py <slug>`; tail quiet should be 0.4 s or
    more (0.35 s is the hard floor). "spell-review" lists words not in the
    dictionary (proper nouns are normal; look for real typos). Then
    `tools/frame_sheet.py` and **look at frames**: title not touching the
    forehead, subtitle readable, watermark present, face centred.
    Listening to the first second and last 1.5 s is the final gate; the assistant
    in the IDE could not play audio, so it relied on silence measurements. If Kiro
    Crew can listen, do it.
11. **Upload and schedule:** `python3 tools/upload_batch.py <slug> 1 2 3 ...`
    (no owner review needed for new reels that passed every check; owner reviews
    on the channel).
12. **Record:** add rows to `docs/SOURCES.md` (columns Source | Reel | Date |
    YouTube; Date = `goes live YYYY-MM-DD, 6 AM|6 PM IST` until public; the link
    exists straight away); a dated note in `docs/CHANGELOG.md`; commit and push.

If the owner re-shares a source already in SOURCES.md: make **new, different**
moments from it, reuse the slug and `crop_x`, no duplicate row, never touch the
live reels.

## 9. Rules from the owner (standing; some are in STYLE.md, listed here in one place)

- Every reel **under 60 s**. Average about 30 s is fine. Shortest first.
- Best moments: advice, or the high point of a story. End on a complete thought.
- **No human review before upload.** Keep every reel and source after upload.
- **Two reels a day at 6 AM and 6 PM IST** using YouTube scheduled publishing.
- **English-only subtitles.** Descriptions and hashtags in **English and Kannada**.
- Credit the speaker as **Sri Satyatmateertha Shripadangalavaru** with the talk
  title and "Sri Uttaradi Math Adhyatmavani". Ask if a source's speaker is unclear.
- Spell-check English and Kannada before upload. Confirmed spellings: Madhwacharya
  (Madhvacharya also fine), Rudra, Rudradeva, Shukacharya, Tirumala, Tiruchanur,
  Padma Sarovar, Yashoda, Shani, Ugadi, Phalguna Amavasya, darshan. Never invent a
  Sanskrit spelling: use `tools/sanskrit_terms.py` or flag it.
- Noto Sans for everything on screen. No Amazon Ember.
- Delete, replace or change privacy of a live video **only when the owner names
  that video** in the current conversation. Say the video id and title first.
  Deletion is permanent. `--replace` gives a new link and loses views.
- Instagram is manual (no business account, no API). Never try to automate it.
- Do not change a rule in STYLE.md without the owner agreeing. A one-off request
  is not a new standing rule.
- Do not re-introduce Whisper-style tools unless asked (the owner did ask for the
  ASR study in October; result in section 11).
- Background music: planned, not built. The owner will supply tracks later (very
  low volume under speech). Do nothing until files arrive.

## 10. Lessons learned (each one cost something; do not repeat)

1. **Off-centre speaker:** a `crop_x` reused from another source. Derive it per
   source and view a rendered frame.
2. **Abrupt endings:** a cut on a sentence end plus a fade is not enough. Fades
   do not fix speech running into the last half second, and caption cue times lie
   by up to a second. Measure silence on the **finished file**, aim for 0.5 to
   0.7 s of quiet, and choose endings where the thought is complete. Mid-explanation
   cuts always feel abrupt.
3. **"Missing File" frame:** a 1.6 s editor placeholder in the uploader's own video
   (ep06 reel 10) got through because only a few preview frames were checked. The
   scan is now every frame and the builder refuses a flagged range.
4. **Double-booked days:** YouTube's uploads list does not show a just-scheduled
   private video, so ten quick uploads landed two per day. The local ledger
   `upload/schedule_ledger.json` fixes it. Do not delete the ledger.
5. **Blurry bilingual subtitles:** came from shrinking the English line to 36 px.
   Never go below 46 px for English.
6. **English captions are a machine paraphrase.** Cut with the Kannada cues; the
   English is for the meaning only. Do not present subtitles as exact quotes.
7. **Cue times are not audio truth.** Use `silencedetect` pauses to place cuts,
   and the caption text to know which words sit between pauses. Loudness alone is
   useless here because of a constant drone (tanpura) in the recordings.
8. **Sanskrit in YouTube's captions is often garbled** (verses are dropped or
   mangled). The ASR does better there (section 11) but is also not final. Flag
   shlokas for the owner when the words are unclear.
9. **A shared Python with Google/ML packages broke** once (protobuf conflict).
   Keep isolated venvs.
10. **A "possible incident" of missing files** turned out to be the owner's own
    deletion. Check before assuming data loss.
11. **`reel_numbering` reads `reels.json`**, so writing a spec makes the next free
    number jump: assign numbers once when writing the spec.
12. **zsh does not word-split** variables; loops over "a b" pairs need explicit args.
13. A first builder pass for 5 reels exceeds a 2-minute tool timeout; use a longer
    timeout.

## 11. The speech-to-text (ASR) study (details in `docs/NOTES.md`)

- Question: would the owner's ASR (Indic-Transcribe + IndicConformer, in
  `madhwa-pravachana-RAG`) make reels better?
- Result: **small yes, not a big one.** Plain Kannada: no real gain over YouTube's
  Kannada captions. Shlokas: clear gain (YouTube drops or garbles verses; the ASR
  recovers real verse text). Timing: no gain (segment-level only, about 10 s).
- Cost (measured): ASR speed about 0.10 s per audio second (3 min for a 30 min talk;
  the repo's full pipeline about 0.25); about 2.5 CPU cores and 9.1 GB peak memory;
  about 17 GB of disk (models 14.9 GB + env 2 GB) against this project's 7.1 GB.
  Captions from YouTube take about 6 s and cost nothing. It saves no thinking time.
- Decision: not in the standard flow. Optional, only for a clip containing a
  shloka; Sanskrit still needs human checking. Do not modify the RAG repo; run its
  code read-only (`PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1`), outputs to a temp
  folder. The ASR environment is
  `madhwa-pravachana-RAG/experiments/.nemo-venv/bin/python`; entry points used:
  `pravachana.transcribe.transcribe`, `pravachana.fuse.read_segments`,
  `pravachana.fuse.choose` (see `src/pravachana/asr.py`).

## 12. Unused good moments (ready candidates for future reels)

Approximate source seconds; check with `cut_inspect.py` before use. Do not repeat
the topics already made (see SOURCES.md titles).

- **ep04:** time/"padma" meaning (1466 to 1560); Ganapati and the elephant that
  bows (1795 to 1837); the Lord as the hunter of all beings (135 to 204); the Lord
  not "travelling" (69 to 135); how elders arranged the marriage and why consent
  matters (2039 to 2130); the horse and the senses (2133 to 2260); Vayu serving as
  horse, ornament and voice (600 to 690).
- **ep01:** Matanga sages and Anjanadevi (590 to 760); the brahmin Madhava who lost
  his sins at Venkatachala (1131 to 1205); the name in your hometown (793 to 859);
  the four names of the hill (130 to 175).
- **ep02:** the previous incarnation story intro (45 to 115); Narada and the sages
  (190 to 320); Brahma and Rudra tested by Bhrigu (420 to 650); the Lord's marks on
  the chest (1109 to 1200); Lakshmi and Karaveera (1203 to 1262).
- **ep03:** Lakshmi as a cow and Brahma as the bull (370 to 403); milk offered to
  the Lord and Saraswati (499 to 592); the cowherd and the king's responsibility
  (802 to 872); the remedy for the curse (1003 to 1038); Brihaspati and the
  medicine (1075 to 1138); Varaha gives land (1392 to 1450).
- **Shorter, more-than-one-per-talk** is fine: ep04 is 44 minutes and gave only 7.
- Skipped on purpose: the cow-slaughter passage (ep03, 657 to 770) and the
  "qualities girls should have" passage (ep04, 1405 to 1470). Ask the owner if he
  wants them.

## 13. Known weak spots and open items

- Early reels (ep06 03 to 06, ep07 01 to 04, first madhwacharya-avatara reels) have
  the older look and some the old watermark. Not rebuilt; ask before touching.
- The assistant could not **listen** to audio. Endings were verified by silence
  measurements, caption checks and frames. Spot-listening by the owner or Kiro Crew
  is advised for the 25 newest reels (especially ep04 reel 03, which ends on the
  worship message and drops the closing chant, and the Madhva Jayanti reels).
- ep03 and ep04: dark area behind subtitles (pill hard to see); accepted.
- English subtitles are paraphrases; no human has read them against the Kannada
  for most reels. Kannada descriptions pass an orthography check, not a meaning check.
- A few lines of the Sanskrit verses recited inside reels are not shown as
  Sanskrit text (only the meaning).
- The owner's Instagram posting is manual, from the `.caption.txt` files.
- Background music: planned, not built.
- Queue length: 16 days at hand-off. At two reels a day, a talk of 30 to 45
  minutes feeds about a week.
- Quota: unknown. If an upload fails with `quotaExceeded`, stop and retry after
  midnight Pacific.

## 14. How to talk to the owner

- Short, plain sentences. Answer the question he asked first, then the rest.
- Say what was verified and what was not. Do not claim a reel is "fine" from a
  passing script alone.
- Do not ask permission for routine reel-making steps already covered by standing
  rules (build, check, upload, schedule). Do ask before anything destructive on the
  live channel, before changing a standing rule, and before rebuilding old reels.
- He likes tables for status, and decisions explained in one or two lines.
- When the owner changes a rule, update STYLE.md/WORKFLOW.md/GUARDRAILS.md, the
  steering file, CHANGELOG.md, and SOURCES.md if affected, then commit and push.

## 15. Cheat sheet

```
cd "/Users/venkyb/Documents/balaji4aws/madhwa reels"
P=/Users/venkyb/envs/bie-work/bin/python3

# Where does the schedule end?   (prints the next free slot)
upload/.venv/bin/python upload/youtube_upload.py --next-slot

# New source
yt-dlp --cookies-from-browser chrome -f "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" \
  --merge-output-format mp4 --write-auto-subs --sub-langs "kn,en" --sub-format vtt \
  -o "sources/<slug>/source.%(ext)s" "<url>"
$P tools/glitch_scan.py sources/<slug>/source.mp4
$P tools/vtt2txt.py sources/<slug>/source.en.vtt 30
$P tools/cut_inspect.py <slug> <a> <b>
$P tools/cue_rel.py <slug> <start> <end>
# write work/<slug>/reels.json, then:
$P tools/reel_builder.py <slug>
$P tools/check_slug.py <slug>
$P tools/frame_sheet.py /tmp/sheet.png reels/<slug>/<file>.mp4@12 ...
python3 tools/upload_batch.py <slug> 1 2 3
# then SOURCES.md rows, CHANGELOG note, git add/commit/push
```

Fix a description on a live or scheduled video:
`upload/.venv/bin/python upload/youtube_upload.py --update-description <ID> --caption reels/<slug>/<file>.caption.txt`

Verify the schedule from YouTube: use the uploader's service (`youtube_upload.get_service()`)
and `videos().list(part="status", id=...)`; compare `publishAt` (UTC) with the
`upload/upload_log.tsv` times (IST = UTC + 5:30).

## 16. History in one page (details in `docs/CHANGELOG.md`)

- 22 Oct: first reels from Ep-01; built a cut-boundary tool; evaluated Whisper
  (not adopted, tool removed).
- 23 Oct: Ep-06 and Ep-07 reels; abrupt-cut complaints led to the 0.2 s fade, the
  trailing-quiet check and the "advice or story peak" rule; GitHub repo created;
  strict under-60 s rule; upload without review, keep everything; speaker credit
  added; "Missing File" glitch found and the every-frame scan added; one reel a
  day at 6 PM; bilingual subtitles tried and dropped (English only); Noto Sans
  everywhere; Kannada descriptions and hashtags added; first scheduled batch (10
  reels from Ep-05 and the Satyaparayana talk).
- 24 to 25 Oct: scheduled reels went public daily; reels documents tidied.
- 26 Oct: two reels a day (6 AM/6 PM), all pending reels re-packed; speaker credit
  for satyaparayana-mahime; 25 new reels from five new talks, all scheduled
  through 11 Nov; ASR study and its cost study; helper scripts moved into `tools/`;
  this hand-off.

## 17. First things to do as Kiro Crew

1. Read GUARDRAILS.md and STYLE.md; skim SOURCES.md.
2. Confirm access: `python3 -c` the uploader's `get_service()` (no secrets printed) or
   run `--next-slot`; it should print 2026-11-12 06:00 IST.
3. Tell the owner the queue ends 2026-11-11 and ask for the next talk links.
4. For each link follow section 8. Keep two reels a day in mind: at least 14 new
   reels are needed per week to keep the queue full.
5. Keep this file and the other docs current after every batch.
