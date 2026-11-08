# Notes: would better speech-to-text make better reels? (Oct 2026)

**The question:** YouTube's automatic Kannada captions are the starting point
for every reel. A separate, dedicated Kannada speech-to-text model might write
a cleaner transcript. Would that give better reels?

**The answer: a little, not much.** It's worth using only for the parts where
YouTube's captions clearly fail, which is verses. It stays out of the normal
process.

## What was compared

Three clips from the talks, about 10 minutes of speech in total, were
transcribed with the dedicated model and compared line by line with YouTube's
captions for the same seconds.

## What we found

1. **Ordinary Kannada speech: no real gain.** The two transcripts matched
   almost word for word. The model's text was tidier but made a few mistakes
   the captions didn't.
2. **Verses (shlokas): a clear gain.** YouTube garbles verses or drops them
   entirely; one prayer came out as a jumble followed by five seconds of
   nothing. The model recovered readable verse text. It still gets about 8% of
   the letters wrong on Sanskrit, so a person has to check it.
3. **Timing: no gain.** The model only marks roughly every 10 seconds, which
   is too coarse to place a cut. Cuts still use the captions plus the real
   pauses in the audio.
4. **It is slower and heavier.** Captions take seconds and cost nothing. The
   model adds several minutes per talk and needs a lot of memory and disk
   space. It also doesn't speed up the slow part of the work: choosing moments
   and writing subtitles still means reading the talk.

## Limits

There was no human-checked "correct" transcript to measure against, so
accuracy was judged by comparing the two and by whether the text made sense.
It was a small sample: three clips, one speaker.

## Decision

- YouTube's captions stay the default.
- The model may be used for a single clip that contains a verse, with the
  Sanskrit still checked by a person.
- If a searchable library of full talk transcripts is ever wanted, that would
  be a separate project, not part of making reels.
