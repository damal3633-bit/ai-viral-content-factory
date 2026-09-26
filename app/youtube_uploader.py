import os
import json
import glob
import urllib.request
import urllib.parse
import urllib.error

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"

CLIENT_FILE = "client_secret.json"

# GitHub Secret
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

# IMPORTANT:
# For the first test, only ONE video will be selected.
VIDEO_DIR = "data/generated"


def get_client_credentials():
    """
    Read client_id and client_secret from client_secret.json.

    This file must NOT be committed to GitHub.
    """
    with open(CLIENT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "installed" in data:
        client = data["installed"]
    else:
        client = data["web"]

    return client["client_id"], client["client_secret"]


def get_access_token():
    """
    Exchange refresh token for a temporary access token.
    """

    if not REFRESH_TOKEN:
        raise RuntimeError(
            "YOUTUBE_REFRESH_TOKEN GitHub Secret is missing."
        )

    client_id, client_secret = get_client_credentials()

    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
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

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode())

    if "access_token" not in result:
        raise RuntimeError(
            "Could not obtain YouTube access token."
        )

    return result["access_token"]


def find_one_video():
    """
    Find exactly ONE MP4 video for the first test.
    """

    videos = sorted(
        glob.glob(
            os.path.join(VIDEO_DIR, "**", "*.mp4"),
            recursive=True
        )
    )

    if not videos:
        raise FileNotFoundError(
            "No MP4 video found in data/generated/"
        )

    return videos[0]


def upload_video(video_path):
    """
    Upload one video to YouTube.

    This first test uses:
    - private visibility
    - Shorts-friendly title
    - basic description
    """

    access_token = get_access_token()

    title = os.path.splitext(
        os.path.basename(video_path)
    )[0]

    # Keep title within YouTube's normal title limit.
    title = title[:100]

    description = (
        "AI Viral Content Factory\n\n"
        "#Shorts #Viral #AI"
    )

    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [
                "Shorts",
                "Viral",
                "AI",
                "Bengali",
                "Hindi"
            ],
            "categoryId": "22"
        },
        "status": {
            # FIRST TEST = private
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False
        }
    }

    with open(video_path, "rb") as f:
        video_data = f.read()

    boundary = "----AIContentFactoryBoundary"

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
    ).encode() + video_data + (
        f"\r\n--{boundary}--\r\n"
    ).encode()

    url = (
        UPLOAD_URL
        + "?part=snippet,status"
    )

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": (
                "multipart/related; "
                f"boundary={boundary}"
            )
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
            "YouTube upload finished but no video ID was returned."
        )

    print()
    print("=" * 60)
    print("YOUTUBE UPLOAD SUCCESS")
    print("=" * 60)
    print(f"Video: {os.path.basename(video_path)}")
    print(f"YouTube Video ID: {video_id}")
    print("Privacy: PRIVATE")
    print("=" * 60)


def main():
    print("Searching for one generated video...")

    video_path = find_one_video()

    print(f"Selected video: {video_path}")

    upload_video(video_path)


if __name__ == "__main__":
    main()
