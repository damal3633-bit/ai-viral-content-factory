import json
from datetime import datetime, timezone
from pathlib import Path

from trend_finder import get_trends
from ai_writer import make_content
from video_generator import create_video
from thumbnail_generator import create_thumbnail


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "generated"

OUT.mkdir(parents=True, exist_ok=True)


def main():

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    trends = get_trends(limit=5)

    results = []

    for index, trend in enumerate(trends, start=1):

        for language in ("bn", "hi"):

            content = make_content(
                trend,
                language
            )

            job_dir = (
                OUT /
                f"{run_id}_{language}_{index}"
            )

            job_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            # -------------------------
            # Save content information
            # -------------------------

            content_file = job_dir / "content.json"

            content_file.write_text(
                json.dumps(
                    content,
                    ensure_ascii=False,
                    indent=2
                ),
                encoding="utf-8"
            )

            # -------------------------
            # Generate voice + video
            # -------------------------

            video = create_video(
                content,
                job_dir
            )

            # -------------------------
            # Generate thumbnail
            # -------------------------

            thumbnail = create_thumbnail(
                content,
                job_dir
            )

            results.append({
                "language": language,
                "trend": trend["title"],
                "title": content["title"],
                "source_url": content["source_url"],
                "video": str(
                    video.relative_to(ROOT)
                ),
                "thumbnail": str(
                    thumbnail.relative_to(ROOT)
                ),
                "content": str(
                    content_file.relative_to(ROOT)
                ),
            })

    # -------------------------
    # Save summary
    # -------------------------

    summary = (
        OUT /
        f"{run_id}_summary.json"
    )

    summary.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2
        )
    )


if __name__ == "__main__":
    main()
