import shutil
import subprocess
from pathlib import Path

from voice_generator import create_voice


def _escape_drawtext(text):
    return (
        text.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("%", "\\%")
        .replace("\n", " ")
    )


def create_video(content, out_dir):
    """
    Creates a vertical 9:16 MP4 with generated Bengali/Hindi voice.
    """

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed.")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Generate Bengali/Hindi voice
    voice_file = create_voice(content, out_dir)

    output_file = out_dir / "video.mp4"

    text = _escape_drawtext(content["script"][:220])

    video_filter = (
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"text='{text}':"
        "fontcolor=white:"
        "fontsize=54:"
        "line_spacing=18:"
        "x=70:"
        "y=(h-text_h)/2:"
        "box=1:"
        "boxcolor=black@0.40:"
        "boxborderw=35"
    )

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x111827:s=1080x1920:r=30",
        "-i",
        str(voice_file),
        "-vf",
        video_filter,
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        str(output_file),
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return output_file
