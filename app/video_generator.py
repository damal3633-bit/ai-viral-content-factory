import shutil
import subprocess
from pathlib import Path

from voice_generator import create_voice


WIDTH = 1080
HEIGHT = 1920
FPS = 30


def _escape_drawtext(text):
    return (
        text.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("%", "\\%")
        .replace("\n", " ")
    )


def _get_duration(audio_file):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(audio_file),
    ]

    result = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return float(result.stdout.strip())


def create_video(content, out_dir):
    """
    Creates a vertical animated Shorts/Reels video
    with Bengali/Hindi AI voice and animated text.
    """

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed.")

    if not shutil.which("ffprobe"):
        raise RuntimeError("FFprobe is not installed.")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Generate voice
    # -------------------------
    voice_file = create_voice(content, out_dir)

    duration = _get_duration(voice_file)

    output_file = out_dir / "video.mp4"

    # -------------------------
    # Text
    # -------------------------
    title = _escape_drawtext(content["title"][:90])
    script = _escape_drawtext(content["script"][:260])

    # -------------------------
    # Animated background
    # -------------------------
    background = (
        "color=c=0x0b1020:"
        f"s={WIDTH}x{HEIGHT}:"
        f"r={FPS}"
    )

    # -------------------------
    # Animated zoom / movement
    # -------------------------
    zoom = (
        "scale="
        f"{WIDTH}*1.08:"
        f"{HEIGHT}*1.08,"
        "crop="
        f"{WIDTH}:{HEIGHT}:"
        f"(in_w-{WIDTH})/2+"
        "20*sin(t*0.7):"
        f"(in_h-{HEIGHT})/2+"
        "20*cos(t*0.7)"
    )

    # -------------------------
    # Main title
    # -------------------------
    title_text = (
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"text='{title}':"
        "fontcolor=white:"
        "fontsize=62:"
        "line_spacing=15:"
        "x=(w-text_w)/2:"
        "y=260:"
        "box=1:"
        "boxcolor=black@0.45:"
        "boxborderw=30"
    )

    # -------------------------
    # Script captions
    # -------------------------
    caption_text = (
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"text='{script}':"
        "fontcolor=white:"
        "fontsize=48:"
        "line_spacing=18:"
        "x=65:"
        "y=(h-text_h)/2:"
        "box=1:"
        "boxcolor=black@0.48:"
        "boxborderw=35"
    )

    # -------------------------
    # Bottom branding
    # -------------------------
    branding = (
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        "text='AI Viral Content':"
        "fontcolor=white@0.85:"
        "fontsize=34:"
        "x=(w-text_w)/2:"
        "y=h-120"
    )

    video_filter = ",".join([
        zoom,
        title_text,
        caption_text,
        branding,
    ])

    command = [
        "ffmpeg",
        "-y",

        "-f",
        "lavfi",

        "-i",
        background,

        "-i",
        str(voice_file),

        "-vf",
        video_filter,

        "-map",
        "0:v:0",

        "-map",
        "1:a:0",

        "-t",
        str(duration),

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "24",

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
