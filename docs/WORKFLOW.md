# Workflow: how a talk becomes reels

This is the pipeline at a high level. How a reel should look is in
`STYLE.md`; the checks and safeguards are in `GUARDRAILS.md`.

```
 Talk link
    │
    ▼
 1. Download ──► 2. Transcript ──► 3. Pick moments ──► 4. Place cuts
                                                          │
    ┌─────────────────────────────────────────────────────┘
    ▼
 5. Build reel ──► 6. Check ──► 7. Schedule on YouTube ──► 8. Record
```

## 1. Download

The owner shares a YouTube link. The **whole** talk is downloaded once, never
a trimmed piece. Every frame is scanned for glitches, such as black flashes or
placeholder cards, so no reel is cut across one.

## 2. Transcript

The words of the talk, with timings, are needed to find moments and write
subtitles.

- Usually this is **YouTube's own Kannada captions**, with YouTube's English
  translation as a rough guide.
- When a talk has no captions, a **dedicated Kannada speech-to-text model**
  writes the transcript instead (see `NOTES.md`).

## 3. Pick moments

The transcript is read in full to find moments that **stand on their own**:

- the speaker giving advice, or
- the high point of a story,

each **under 60 seconds** and ending on a complete thought. Passages that
attack others are skipped. One talk usually gives five or six reels.

## 4. Place the cuts

Each start and end is moved onto a **real pause** in the speech, measured from
the audio itself. That way a reel never starts or stops in the middle of a
word.

## 5. Build the reel

Each reel is written down as a short description: where it starts and ends,
its title, its subtitle lines with their timings, and its YouTube description
in English and Kannada. A builder then turns that into the finished video:

1. Cut the clip from the talk.
2. Reframe it to vertical around the speaker.
3. Add the title, the subtitles and the watermark.
4. Fade the start and end.

## 6. Check

Automatic checks run on every reel, then a person-style review: looking at
frames and listening to the start and end. See `GUARDRAILS.md`.

## 7. Schedule

Reels that pass are uploaded and scheduled on YouTube, **one reel per slot,
at 6 AM and 6 PM India time**. YouTube releases them on its own. For a new
speaker or a new look, one reel is uploaded first for the owner to review,
and the rest follow once it's approved. Instagram is posted by hand.

## 8. Record

Each reel's link goes into `SOURCES.md`, and anything learned goes into
`CHANGELOG.md`.
