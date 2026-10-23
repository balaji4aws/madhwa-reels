# YouTube Uploader — One-Time Setup

This lets the uploader script push a finished reel to the **Madhwa16**
YouTube channel as a Short. **Default privacy is public** — a reel goes live
on upload. Pass `--privacy unlisted` (or `private`) for a specific run if you
want to hold a reel back for review before it goes live.

You do this setup once. It takes about 10 minutes.

---

## Step 1 — Create a Google Cloud project

1. Go to https://console.cloud.google.com/ and sign in with the Google account
   that **owns the Madhwa16 YouTube channel**.
2. Top bar → project dropdown → **New Project**. Name it e.g. `madhwa-reels`.
   Create it, then select it.

## Step 2 — Enable the YouTube Data API

1. Left menu → **APIs & Services → Library**.
2. Search **"YouTube Data API v3"**, open it, click **Enable**.

## Step 3 — Configure the OAuth consent screen

1. Left menu → **APIs & Services → OAuth consent screen**.
2. User type: **External** → Create.
3. Fill the required fields (app name `Madhwa Reels Uploader`, your email).
   You can skip optional fields.
4. **Scopes:** you can skip adding scopes here (the script requests them).
5. **Test users:** add **your own Google account email** (the Madhwa16 owner).
   This is important — while the app is in "testing", only listed test users
   can authorize it. (That's fine for personal use; no need to publish the app.)
6. Save.

## Step 4 — Create the OAuth client (Desktop app)

1. Left menu → **APIs & Services → Credentials**.
2. **Create Credentials → OAuth client ID**.
3. Application type: **Desktop app**. Name it `madhwa-reels-desktop`. Create.
4. Click **Download JSON** on the client you just made.
5. **Rename the file to `client_secret.json`** and put it in this folder:
   `madhwa reels/upload/client_secret.json`

That's it. Tell Kiro the file is in place.

---

## First upload (Kiro runs this)

```
upload/.venv/bin/python upload/youtube_upload.py reels/venkatachala-ep01_01_four-names.mp4
```

- The first run opens your browser → pick the Madhwa16 Google account →
  "Google hasn't verified this app" → **Continue** (it's your own app) → allow
  the YouTube permission (the script requests the broader `youtube` scope,
  not just `youtube.upload`, so it can also update an existing video's
  privacy later without re-uploading).
- A `upload/token.json` is saved so you won't be asked again.
- The reel uploads **public** by default. The script prints a `youtu.be/...`
  link — it's already live on the channel.

To hold a reel back for review before it goes live, upload it unlisted or
private instead, then flip it public later:
```
upload/.venv/bin/python upload/youtube_upload.py reels/<reel>.mp4 --privacy unlisted
# ... review it, then:
upload/.venv/bin/python upload/youtube_upload.py --set-privacy <VIDEO_ID> --privacy public
```

---

## Notes & limits

- **Quota:** Google's docs suggest roughly **6 uploads/day** on a fresh
  project (~1600 units each, 10,000/day). In practice 20 went through on
  2026-10-23 with no refusal, so treat 6 as a floor. You
  can request more in the Cloud console if needed.
- **Secrets:** `client_secret.json` and `token.json` are private. They are
  gitignored and must never be committed or shared.
- **Shorts:** the script adds `#Shorts` to the title and the video is already
  1080x1920 ≤60s, so YouTube files it as a Short automatically.
- **Title/description/tags** come from the reel's `.caption.txt` sidecar.
