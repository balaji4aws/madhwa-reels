#!/usr/bin/env python3
"""Upload a Madhwa reel to YouTube as a Short (PUBLIC by default).

Run with the isolated venv:
    upload/.venv/bin/python upload/youtube_upload.py reels/<reel>.mp4

Reads title/description/tags from the matching <reel>.caption.txt sidecar if
present. First run opens a browser for one-time Google authorization and stores
a token in upload/token.json for reuse.

Default privacy is PUBLIC (changed from the original unlisted-first-review
default, per the channel owner's explicit direction once the pipeline was
proven end to end on a test upload). Pass --privacy unlisted or
--privacy private to override for a specific run if you want to hold a reel
back for review before it goes live.

Setup (one time): see upload/SETUP.md. You need upload/client_secret.json
(an OAuth "Desktop app" client for a Google Cloud project with the
YouTube Data API v3 enabled, authorized by the account that owns Madhwa16).
"""
import argparse
import os
import re
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET = os.path.join(HERE, "client_secret.json")
TOKEN = os.path.join(HERE, "token.json")
# youtube.upload alone can insert videos but CANNOT call videos.update
# (needed to change privacy on an already-uploaded video) -- that requires
# the broader youtube scope. Re-authorizing with this broader scope will
# prompt a fresh browser login once (delete upload/token.json first if an
# old narrower-scoped token is cached).
SCOPES = ["https://www.googleapis.com/auth/youtube"]

VALID_PRIVACY = {"private", "unlisted", "public"}


def get_service():
    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET):
                sys.exit(
                    f"Missing {CLIENT_SECRET}.\nSee upload/SETUP.md to create it."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def parse_caption(path):
    """Parse a .caption.txt sidecar into title, description, tags."""
    title, description, tags = None, "", []
    if not os.path.exists(path):
        return title, description, tags
    with open(path) as f:
        text = f.read()

    def section(name):
        m = re.search(rf"^{name}\n(.*?)(?=\n[A-Z]+\n|\Z)", text, re.S | re.M)
        return m.group(1).strip() if m else ""

    title = section("TITLE") or None
    description = section("DESCRIPTION")
    hashtags = section("HASHTAGS")
    # YouTube tags: strip '#', split on whitespace
    tags = [t.lstrip("#") for t in hashtags.split() if t.strip()]
    # Append the hashtag line into the description too (helps discovery/Shorts)
    if hashtags:
        description = (description + "\n\n" + hashtags).strip()
    return title, description, tags


def set_privacy(video_id, privacy):
    """Update an already-uploaded video's privacy status (no re-upload)."""
    yt = get_service()
    body = {"id": video_id, "status": {"privacyStatus": privacy}}
    yt.videos().update(part="status", body=body).execute()
    print(f"Video {video_id} is now '{privacy}'.")
    print("Watch:", f"https://youtu.be/{video_id}")


def update_description(video_id, caption_path):
    """Replace an already-uploaded video's description + tags with the ones in
    its .caption.txt, IN PLACE (same video ID/URL, views kept, no re-upload).
    The live title and category are left exactly as they are."""
    _, description, tags = parse_caption(caption_path)
    if not description:
        sys.exit(f"No DESCRIPTION found in {caption_path}")
    yt = get_service()
    items = yt.videos().list(part="snippet", id=video_id).execute().get("items", [])
    if not items:
        sys.exit(f"Video {video_id} not found on this channel.")
    snippet = items[0]["snippet"]
    body = {"id": video_id, "snippet": {
        "title": snippet["title"],                 # unchanged
        "categoryId": snippet["categoryId"],       # unchanged
        "description": description,
        "tags": tags[:40],
    }}
    yt.videos().update(part="snippet", body=body).execute()
    print(f"Updated description of {video_id} ({snippet['title']!r}).")
    print("Watch:", f"https://youtu.be/{video_id}")


def delete_video(video_id):
    """Permanently delete an uploaded video. NOT reversible."""
    yt = get_service()
    yt.videos().delete(id=video_id).execute()
    print(f"Video {video_id} deleted.")


def main():
    ap = argparse.ArgumentParser(description="Upload a reel to YouTube as a Short.")
    ap.add_argument("video", nargs="?", help="path to the reel .mp4")
    ap.add_argument("--privacy", default="public", choices=sorted(VALID_PRIVACY),
                    help="privacy status (default: public)")
    ap.add_argument("--title", help="override title")
    ap.add_argument("--caption", help="path to caption sidecar (default: auto)")
    ap.add_argument("--shorts", action="store_true", default=True,
                    help="ensure #Shorts is in the title (default on)")
    ap.add_argument("--set-privacy", metavar="VIDEO_ID",
                    help="update an already-uploaded video's privacy instead "
                         "of uploading a new one; use with --privacy")
    ap.add_argument("--delete", metavar="VIDEO_ID",
                    help="PERMANENTLY delete an already-uploaded video. "
                         "Not reversible. Prompts for confirmation unless "
                         "--yes is also given.")
    ap.add_argument("--yes", action="store_true",
                     help="skip the confirmation prompt for --delete")
    ap.add_argument("--replace", metavar="OLD_VIDEO_ID",
                    help="delete OLD_VIDEO_ID, then upload the given video "
                         "as its replacement (used when a reel needs rework "
                         "and a re-upload). Prompts for confirmation unless "
                         "--yes is also given. The replacement gets a NEW "
                         "video ID/URL -- YouTube has no in-place file swap.")
    ap.add_argument("--update-description", metavar="VIDEO_ID",
                    help="replace an already-uploaded video's description and "
                         "tags with the ones in --caption (or the given "
                         "video's sidecar). Same video/URL, no re-upload; the "
                         "title is not changed.")
    args = ap.parse_args()

    if args.update_description:
        cap = args.caption or (os.path.splitext(args.video)[0] + ".caption.txt"
                               if args.video else None)
        if not cap or not os.path.exists(cap):
            sys.exit("--update-description needs --caption <file.caption.txt> "
                     "(or the reel .mp4 path, to use its sidecar).")
        update_description(args.update_description, cap)
        return

    if args.set_privacy:
        set_privacy(args.set_privacy, args.privacy)
        return

    if args.delete:
        if not args.yes:
            resp = input(f"Permanently delete video {args.delete}? "
                          f"This cannot be undone. Type 'yes' to confirm: ")
            if resp.strip().lower() != "yes":
                print("Cancelled.")
                return
        delete_video(args.delete)
        return

    if args.replace:
        if not args.video:
            sys.exit("--replace requires a new video path to upload after deleting.")
        if not os.path.exists(args.video):
            sys.exit(f"Video not found: {args.video}")
        if not args.yes:
            resp = input(f"Delete video {args.replace} and replace it with "
                          f"'{args.video}'? The old video cannot be recovered "
                          f"and the new one gets a DIFFERENT URL. Type 'yes' "
                          f"to confirm: ")
            if resp.strip().lower() != "yes":
                print("Cancelled.")
                return
        delete_video(args.replace)
        # fall through to the normal upload path below using args.video

    if not args.video:
        sys.exit("Provide a video path to upload, or --set-privacy/--delete/"
                  "--replace VIDEO_ID to manage an existing video.")
    if not os.path.exists(args.video):
        sys.exit(f"Video not found: {args.video}")

    caption_path = args.caption or (os.path.splitext(args.video)[0] + ".caption.txt")
    title, description, tags = parse_caption(caption_path)
    if args.title:
        title = args.title
    if not title:
        title = os.path.splitext(os.path.basename(args.video))[0]

    # Nudge YouTube to treat it as a Short.
    if args.shorts and "#shorts" not in title.lower():
        title = f"{title} #Shorts"
    title = title[:100]  # YouTube title limit

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags[:40],
            "categoryId": "22",  # People & Blogs
        },
        "status": {
            "privacyStatus": args.privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    yt = get_service()
    media = MediaFileUpload(args.video, chunksize=-1, resumable=True,
                            mimetype="video/mp4")
    print(f"Uploading '{title}' as {args.privacy} ...")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    vid = resp["id"]
    print("Done. Video ID:", vid)
    print("Watch:", f"https://youtu.be/{vid}")
    if args.privacy == "public":
        print("(Privacy: public — live on the channel now.)")
    else:
        print(f"(Privacy: {args.privacy} — make it public when you're happy with it, "
              f"e.g. upload/.venv/bin/python upload/youtube_upload.py "
              f"--set-privacy {vid} --privacy public)")


if __name__ == "__main__":
    main()
