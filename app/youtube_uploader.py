import os
import json
import glob
import urllib.request
import urllib.parse
import urllib.error

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"

REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")

VIDEO_DIR = "data/generated"


def get_access_token():
    if not REFRESH_TOKEN:
        raise RuntimeError("YOUTUBE_REFRESH_TOKEN is missing.")

    if not CLIENT_ID:
        raise RuntimeError("YOUTUBE_CLIENT_ID is missing.")

    if not CLIENT_SECRET:
        raise RuntimeError("YOUTUBE_CLIENT_SECRET is missing.")

    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }).encode()

    request = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode())

    except urllib.error.HTTPError as e:
        error_body = e.read().decode(errors="replace")
        raise RuntimeError(
            "Google OAuth token request failed:\n" + error_body
        )

    if "access_token" not in result:
        raise RuntimeError(
            "Google did not return an access token."
        )

    return result["access_token"]


def find_cartoon_video():
    pattern = os.path.join(
        VIDEO_DIR,
        "cartoon_daily",
        "*.mp4"
    )

    videos = sorted(glob.glob(pattern))

    if not videos:
        raise FileNotFoundError(
            "No Funny Boy cartoon video found in "
            "data/generated/cartoon_daily/"
        )

    return videos[0]


def upload_video(video_path):
    access_token = get_access_token()

    title = "Funny Boy 😂 | Daily Cartoon Short"

    description = (
        "Funny Boy-এর নতুন মজার cartoon story!\n\n"
        "New funny 3D cartoon story every day.\n\n"
        "#Shorts #FunnyBoy #Cartoon #3DCartoon #Funny"
    )

    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [
                "Funny Boy",
                "Cartoon",
                "3D Cartoon",
                "Funny Cartoon",
                "Bengali Cartoon",
                "Hindi Cartoon",
                "Shorts",
                "Funny Shorts"
            ],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False
        }
    }

    with open(video_path, "rb") as f:
        video_data = f.read()

    boundary = "----FunnyBoyCartoonBoundary"

    metadata_json = json.dumps(
        metadata,
        ensure_ascii=False
    )

    body = (
        f"--{boundary}\r\n"
        "Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{metadata_json}\r\n"
        f"--{boundary}\r\n"
        "Content-Type: video/mp4\r\n\r\n"
    ).encode()

    body += video_data
    body += (
        f"\r\n--{boundary}--\r\n"
    ).encode()

    url = UPLOAD_URL + "?part=snippet,status"

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type":
                f"multipart/related; boundary={boundary}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(
                response.read().decode()
            )

    except urllib.error.HTTPError as e:
        error_body = e.read().decode(
            errors="replace"
        )

        raise RuntimeError(
            "YouTube API upload failed:\n"
            + error_body
        )

    video_id = result.get("id")

    if not video_id:
        raise RuntimeError(
            "YouTube did not return a video ID."
        )

    print()
    print("=" * 60)
    print("FUNNY BOY YOUTUBE UPLOAD SUCCESS")
    print("=" * 60)
    print(f"Video: {os.path.basename(video_path)}")
    print(f"YouTube Video ID: {video_id}")
    print("Privacy: PRIVATE")
    print("=" * 60)


def main():
    print("=" * 60)
    print("SEARCHING FOR FUNNY BOY CARTOON")
    print("=" * 60)

    video_path = find_cartoon_video()

    print(f"Selected cartoon: {video_path}")

    upload_video(video_path)


if __name__ == "__main__":
    main()
