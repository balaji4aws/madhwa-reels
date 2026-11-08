# Changelog

What changed and what was learned, newest first. Each rule in `STYLE.md` and
`GUARDRAILS.md` traces back to one of these.

## November 2026

- **One reel per slot beats batches.** The first week of YouTube data showed
  reels released one per slot had a median of about 10,800 views, against
  about 50 for reels released four or more on the same day. The channel's
  Shorts views jumped from a few dozen a day to 17,000–60,000 a day from
  28 Oct, all from YouTube's Shorts feed, none from ads.
- **The opening seconds matter most.** About two-thirds of viewers swipe away
  in the first second or two. New rule: open on the strongest line, with the
  title on screen from the first frame.
- **Length is not the deciding factor.** The biggest reels ran 32–50 seconds.
  "Shortest first" stays the order to try, but never at the cost of the
  ending.
- **Long full talks hold almost nobody.** On long uploads, viewers watched
  about 1% of the video. Short 3–6 minute pieces do far better.
- The YouTube login now recovers by itself when it expires.

## Late October 2026

- **Readable watermark.** The white web address vanished against white robes.
  It now sits on a dark rounded band, like the subtitles. The three Karthika
  reels were re-uploaded with it, which gave them new links.
- **New talk: Karthika Masa Mahatmya** by Purandara Aacharya (Sri Uttaradhi
  Matha Adhyatmavani). Three reels. The video was already vertical, so it
  sits full width over a blurred copy. The owner asked for these to go live
  straight away instead of being scheduled.
- **Kannada typing slips** (wrong vowel signs, a stray letter from another
  script) were caught by the automatic Kannada check before upload.
- **Two reels a day, at 6 AM and 6 PM India time**, up from one a day.
- **25 reels from five talks**, scheduled through 11 Nov. One short news
  clip (Madhva Jayanti made an official day) could only give three reels, so
  the other two came from a longer talk.
- **Speaker credit on every reel**, including Sri Satyatmateertha
  Shripadangalavaru for the Satyaparayana talk.
- **Better speech-to-text was tested** and not adopted for the normal flow.
  It only helps with verses. See `NOTES.md`.

## 23 October 2026: the big day of rules

Most of the current rules were set in one long day of making reels and
getting the owner's feedback.

- **Abrupt endings, solved in three steps.** First, more quiet after the last
  word: not enough. Then a soft fade at each end: better, but some reels still
  felt cut off. The real fix: choose moments whose *thought* is finished,
  meaning advice or the high point of a story, not the middle of an
  explanation.
- **Under 60 seconds became a hard rule.** Short moments are tried first.
- **No review before upload.** A reel that passes every check goes straight
  to YouTube; the owner reviews on the channel. Finished reels are kept, not
  deleted.
- **Every frame is scanned.** One source had a 1.6-second "Missing File" card
  that a single preview frame missed, and it reached a reel.
- **Scheduled publishing.** Reels are uploaded ahead of time and YouTube
  releases them at the set hour.
- **Subtitles: English only.** A Kannada-plus-English version was tried; the
  English had been shrunk to fit and looked blurry on phones. English went
  back to full size, and Kannada moved into the descriptions and hashtags.
- **One font for everything** (Noto Sans), a one-line title, and the full
  channel address in the watermark.
- **Repeated talks are fine.** When a talk comes back, new reels must be new
  moments.
- One early test video with a wrong title was deleted from the channel at the
  owner's request, after its id and title were confirmed.

## 22 October 2026: the start

- **First reels** from the Venkatachala series of talks.
- **A cut-placement tool** was built: it moves a rough cut to the nearest
  real pause and checks it against the captions, flagging anything doubtful.
- **Captions are not the audio.** The recordings carry a constant background
  drone, so "quiet" can't be judged by loudness alone. Cuts are checked
  against caption boundaries and by listening.
- **The crop must be worked out for each talk.** Reusing one talk's crop on
  another left the speaker off-centre.
- **Another speech-to-text model was tested** for more precise cut timing. It
  was no better and far slower, so it was dropped.
- **A scare: the finished-reels folder was found empty.** Nothing was really
  lost, since every reel could be rebuilt from its spec, and the cause turned
  out to be a deliberate clean-up. Hence the guardrail: check before assuming
  data is lost, and never delete with wildcards.
