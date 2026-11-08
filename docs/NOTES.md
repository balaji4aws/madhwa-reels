# Notes: the speech-to-text models tried

Every reel starts from a transcript: the words of the talk, with the time
each line is said. That transcript is used to find good moments, place the
cuts and write the subtitles. Getting it right matters, so several ways of
making it have been tried.

**Speech-to-text** (also called ASR, automatic speech recognition) means a
computer listening to audio and writing down the words.

## The short version

| What | Used for | Verdict |
|---|---|---|
| YouTube's automatic captions | Every talk that has them | **The default.** Free, instant, good enough for ordinary Kannada speech. |
| Whisper | Tested for more precise cut timing | **Dropped.** No better, and far slower. |
| Dedicated Kannada models | Tested against YouTube's captions; used when a talk has no captions | **Kept for special cases:** talks without captions, and verses. |

## 1. YouTube's automatic captions (the default)

YouTube listens to every upload and writes captions in Kannada. It can also
translate them to English.

- **Good:** free, ready in seconds, accurate for ordinary Kannada speech.
- **Weak:** verses (shlokas) come out garbled or go missing. The English
  translation is a loose paraphrase, and its timing doesn't follow the audio.
  Some talks have no captions at all.
- **How it's used:** the Kannada captions guide the meaning. The cuts go on
  real pauses measured from the audio, not on caption timings.

## 2. Whisper (tried, dropped)

Whisper is a well-known open speech-to-text model. It was tested to see
whether it could time cut points more precisely than the captions.

- On these talks it made the **same timing mistake** a person had to fix by
  hand: a cut landing about 4 to 5 seconds too early.
- The version that times individual words would have taken about **two hours**
  for a 21-minute talk.
- **Result:** dropped, and removed from the project.

## 3. Dedicated Kannada models (kept for special cases)

These are models built specifically for Indian languages:

- **IndicConformer** (from AI4Bharat): listens to the audio and spots where
  speech is and where verses are.
- **Indic-Transcribe:** writes the Kannada text.
- **Sushrota** (from IISc): made for Sanskrit, used on verses.

They were tested on three clips, about 10 minutes of speech, and compared
line by line with YouTube's captions:

1. **Ordinary Kannada speech: no real gain.** The two matched almost word for
   word. The models' text was tidier but made a few mistakes the captions
   didn't.
2. **Verses: a clear gain.** Where YouTube gave a jumble followed by silence,
   the models gave readable verse text. It still gets about 8% of the letters
   wrong on Sanskrit, so a person has to check it.
3. **Timing: no gain.** They mark time only about every 10 seconds, too coarse
   to place a cut.
4. **Cost:** several extra minutes per talk, plus a lot of memory and disk
   space. They also don't speed up the slow part, which is reading the talk
   to choose moments.

**Where they help today:** a talk with no captions at all. "What is Madhwa
Mata" by Dr. Vyasanakere Prabhanjanacharya had none, so its six reels were
made from a transcript written by these models. The subtitles were then
written from that Kannada, and the cuts were placed on measured pauses.

## What was learned

- No transcript is perfect, machine-made or not. Subtitles give the meaning,
  not an exact quote.
- Cut timing always comes from the audio itself.
- Verses always need a person to check them, whichever model wrote them.
- Models were only judged by comparing them with each other and by whether
  the text made sense; there was no human-checked transcript to measure
  against.
