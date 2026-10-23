# Madhwa Reels

Turning long Madhwa / Dvaita devotional discourses from YouTube into short
vertical reels for the **Madhwa16** channel
(https://www.youtube.com/@madhwa16/). Reels go to YouTube Shorts
automatically and to Instagram Reels by hand.

This is a personal project. An AI coding assistant acts as the video editor:
you share a YouTube link, and it finds the strong moments, cuts them into
reels in a consistent style, checks them, and uploads them.

> **About this repository:** it holds only the scripts (`.py`) and docs
> (`.md`) that run the pipeline. Videos and the YouTube login secrets stay on
> the maintainer's machine and are never committed, so you won't find any
> video files here.

---

## The flow

**Long discourse in → short reels out → checked → uploaded.**

1. **Share a YouTube link.** Add timestamps if you already have a moment in
   mind; otherwise the assistant finds moments by reading the captions.
2. **Download.** The full video and its captions are saved once on this machine.
3. **Pick the moments.** The best reels are the speaker giving advice, or the
   high point of a story: moments that end on a complete thought. Short
   reels (~15s) are tried first.
4. **Cut and style.** Each moment becomes a vertical 9:16 video, cropped
   around the speaker, with a title, spell-checked English subtitles, a soft
   fade at each end, and the channel watermark.
5. **Check.** Every reel is checked before it goes out (see below).
6. **Upload.** Reels that pass go straight to YouTube Shorts as public, up to
   YouTube's daily upload limit (anything over it goes the next day). Instagram
   is posted by hand using the prepared title, description and hashtags. All
   reels and source videos are kept on this machine.

---

## What gets checked

- **Shape and length:** vertical 1080x1920, and always **under 60 seconds**.
- **Spelling:** every subtitle word, with Sanskrit and Madhwa names checked
  against a growing list of correct spellings.
- **Clean ending:** the reel doesn't cut off mid-word or mid-thought. This is
  checked against the captions and by listening to the start and end, not
  just by looking for silence (the recordings have a constant background
  drone).
- **A visual look:** a few frames are checked so the title, subtitles and
  watermark are readable and nothing overlaps.

---

## Where things live

```
madhwa reels/
├── README.md        ← this file
├── docs/            ← how-to and rules (see below)
├── tools/           ← shared scripts used for every video
├── assets/          ← channel watermark + brand icon
├── upload/          ← the YouTube upload script
├── sources/<slug>/  ← downloaded videos (not on GitHub)
├── work/<slug>/     ← per-video build scripts (on GitHub) and clips (not)
└── reels/<slug>/    ← finished reels awaiting upload (not on GitHub)
```

**Docs:**

- `docs/WORKFLOW.md`: the steps, in order. Start here.
- `docs/STYLE.md`: the exact look and rules (fonts, colors, sizes, safe zones).
- `docs/GUARDRAILS.md`: what the assistant must never do without asking.
- `docs/SOURCES.md`: every reel made, with its YouTube link.
- `docs/CHANGELOG.md`: dated log of what was tried and what was learned.

---

## Worth knowing

- The English subtitles come from YouTube's automatic captions and
  translation of the Kannada audio. They are cleaned up for spelling, but
  treat them as a close paraphrase, not a word-for-word translation.
- Moments are found by reading the captions, not by watching the video, so a
  strong visual moment with little speech can be missed. Sharing a timestamp
  always works.
