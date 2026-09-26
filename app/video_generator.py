import shutil
import subprocess
from pathlib import Path


def create_video(content, out_dir):
    """
    Creates a simple 9:16 MP4 video using FFmpeg.
    This is an MVP test video and does not copy third-party videos.
    """

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed on this runner.")

    output = out_dir / "video.mp4"

    text = content["script"]

    # Clean characters that can interfere with FFmpeg drawtext.
    text = (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace(",", "\\,")
        .replace("\n", " ")
    )

    # Keep the first part readable in the MVP video.
    text = text[:220]

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x111827:s=1080x1920:r=30",
        "-t",
        "15",
        "-vf",
        (
            "drawtext="
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            f"text='{text}':"
            "fontcolor=white:"
            "fontsize=54:"
            "line_spacing=18:"
            "x=70:"
            "y=(h-text_h)/2:"
            "box=1:"
            "boxcolor=black@0.35:"
            "boxborderw=35"
        ),
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output),
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return output
