import subprocess
from pathlib import Path


def create_thumbnail(content, out_dir):
    """
    Creates a simple 16:9 thumbnail from the video style.
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    output_file = out_dir / "thumbnail.jpg"

    title = (
        content["title"]
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("%", "\\%")
        .replace("\n", " ")
    )

    filter_text = (
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"text='{title[:70]}':"
        "fontcolor=white:"
        "fontsize=70:"
        "x=(w-text_w)/2:"
        "y=(h-text_h)/2:"
        "box=1:"
        "boxcolor=black@0.45:"
        "boxborderw=40"
    )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x111827:s=1280x720",
        "-vf",
        filter_text,
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(output_file),
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return output_file
