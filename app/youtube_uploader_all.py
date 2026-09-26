
import glob
import os

from youtube_uploader import upload_video


VIDEO_DIR = "data/generated"


def main():
    videos = sorted(
        glob.glob(
            os.path.join(VIDEO_DIR, "**", "*.mp4"),
            recursive=True
        )
    )

    if not videos:
        raise FileNotFoundError(
            "No MP4 videos found in data/generated/"
        )

    print(f"Found {len(videos)} video(s).")
    print("Starting YouTube uploads...")

    for index, video_path in enumerate(videos, start=1):
        print()
        print("=" * 60)
        print(f"Uploading {index}/{len(videos)}")
        print(f"Video: {video_path}")
        print("=" * 60)

        upload_video(video_path)

    print()
    print("=" * 60)
    print("ALL YOUTUBE UPLOADS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
