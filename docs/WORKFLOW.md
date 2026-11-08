# Workflow: from a long talk to live reels

This is what happens to each talk, in order. How each reel should look is in
`STYLE.md`; things never to do are in `GUARDRAILS.md`.

**In one line:** get the talk, pick the moments, cut, style, check, schedule,
record.

## 1. Get the talk

- The **full** talk is downloaded once, with its Kannada and English
  captions. Never a trimmed piece.
- The whole video is scanned for glitches (placeholder cards, black flashes)
  so no reel is cut across one.
- The talk gets a short name, its *slug* (for example `venkatachala-ep07`),
  used in every file name after that.
- If a talk was already used before, it is used again on purpose: the new
  reels must be different moments from the ones already made.

## 2. Pick the moments

The captions are read to find moments that **end on a complete thought**:
advice from the speaker, or the high point of a story. Each reel is under 60
seconds and opens on its strongest line. See `STYLE.md` for the full rules.

## 3. Place the cuts

Each start and end is moved to a real pause in the speech, lined up with where
a Kannada sentence begins or ends. The English captions are not used for
timing, because their timing doesn't follow the audio.

## 4. Cut and style

Each reel is described in a small spec: its start and end, its title, its
subtitle lines with their timings, and its description. The builder in
the builder then:

1. Crops the video to vertical around the speaker.
2. Adds the title, the subtitles and the watermark.
3. Adds the short fade at each end.
4. Writes the finished reel plus a text file with its title, description
   and hashtags.

The builder refuses a reel that is 60 seconds or longer, a subtitle line too
long for one line, or a cut across a glitch.

## 5. Check

Every check in `STYLE.md` ("Checks before a reel goes out") must pass:
size, length, spelling in both languages, a clean ending, every frame scanned,
and a look and a listen.

## 6. Schedule

Reels that pass are uploaded to YouTube and scheduled into the next free
slot: 6 AM or 6 PM India time, one reel per slot. There is no extra review
step; the owner reviews on the channel. Instagram is posted by hand.

## 7. Record

Each reel's YouTube link goes into `SOURCES.md` as soon as it's uploaded, and
anything learned goes into `CHANGELOG.md`.

## Standing rules in one place

- Every reel is **under 60 seconds** and ends on a complete thought.
- **Two reels a day, one per slot.** Releasing many at once costs reach.
- **English subtitles; English and Kannada descriptions.**
- **Credit the speaker and Sri Uttaradhi Matha Adhyatmavani.** Never guess a
  name.
- **Spelling is checked every time.** Never invent a Sanskrit spelling.
- **Live videos are only deleted, replaced or hidden when the owner names
  them.** Replacing a video gives it a new link and resets its views.
- **Instagram is always posted by hand.**
- **The rules change only with the owner's agreement.** A one-off request is
  not a new rule.

## Lessons learned (each one cost something)

1. **Off-centre speaker:** every talk is filmed differently, so the crop is
   worked out fresh for each talk and checked on a real frame.
2. **Abrupt endings:** a cut at the end of a sentence isn't enough. The quiet
   is measured on the finished reel, and the moment itself must be finished.
3. **Hidden glitches:** one source had a 1.6-second "Missing File" card that a
   sample frame missed. Now every frame is scanned.
4. **Double-booked days:** YouTube doesn't always show a reel scheduled
   minutes ago, so a local list of booked slots is kept.
5. **Machine-made captions:** the English is a paraphrase, and verses are
   often garbled. Verses are flagged for a person to check.
6. **Kannada typing slips:** wrong vowel signs, or a letter from another
   script, slip into descriptions. An automatic check catches them.
7. **Reel numbers are never reused**, even after a reel is removed.

## Known weak spots

- The earliest reels have an older look and watermark. They haven't been
  rebuilt.
- On two talks the lower part of the picture is dark, so the subtitle band is
  hard to see. The text itself stays readable.
- Most English subtitles haven't been read against the Kannada by a person.
- Long full talks hold almost no viewers on YouTube; short 3–6 minute pieces do
  much better. No long-form flow exists yet.
- The watermark sits close to the subtitles.
