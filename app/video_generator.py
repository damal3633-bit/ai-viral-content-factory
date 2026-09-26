import shutil
import subprocess
from pathlib import Path

from voice_generator import create_voice


WIDTH = 1080
HEIGHT = 1920
FPS = 30


def get_duration(audio_file):
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

    return max(float(result.stdout.strip()), 1.0)


def create_music(out_dir, duration):
    music_file = Path(out_dir) / "background_music.wav"

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"sine=frequency=110:sample_rate=44100:duration={duration}",
        "-filter:a",
        "volume=0.035",
        "-c:a",
        "pcm_s16le",
        str(music_file),
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return music_file


def create_video(content, out_dir):

    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed.")

    if not shutil.which("ffprobe"):
        raise RuntimeError("FFprobe is not installed.")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Generate voice
    # -------------------------

    voice_file = create_voice(
        content,
        out_dir
    )

    duration = get_duration(
        voice_file
    )

    # -------------------------
    # Generate background music
    # -------------------------

    music_file = create_music(
        out_dir,
        duration
    )

    # -------------------------
    # Save text into files
    # This avoids FFmpeg escaping problems
    # with Bengali/Hindi/quotes/commas.
    # -------------------------

    title_file = out_dir / "title.txt"
    script_file = out_dir / "script.txt"

    title_file.write_text(
        content["title"][:100],
        encoding="utf-8"
    )

    script_file.write_text(
        content["script"][:500],
        encoding="utf-8"
    )

    output_file = out_dir / "video.mp4"

    # -------------------------
    # Font
    # -------------------------

    language = content.get(
        "language",
        "bn"
    )

    if language == "bn":
        font_file = (
            "/usr/share/fonts/truetype/noto/"
            "NotoSansBengali-Regular.ttf"
        )
    else:
        font_file = (
            "/usr/share/fonts/truetype/noto/"
            "NotoSansDevanagari-Regular.ttf"
        )

    # -------------------------
    # Video filters
    # -------------------------

    video_filter = (
        "[0:v]"
        "drawbox="
        "x=120+180*sin(t*0.8):"
        "y=180+250*cos(t*0.6):"
        "w=520:"
        "h=520:"
        "color=0x2563eb@0.16:"
        "t=fill,"
        
        "drawbox="
        "x=500+200*cos(t*0.7):"
        "y=1000+250*sin(t*0.5):"
        "w=600:"
        "h=600:"
        "color=0x7c3aed@0.13:"
        "t=fill,"

        "drawtext="
        f"fontfile={font_file}:"
        f"textfile={title_file}:"
        "fontcolor=white:"
        "fontsize=62:"
        "line_spacing=12:"
        "x=(w-text_w)/2:"
        "y=230:"
        "box=1:"
        "boxcolor=black@0.45:"
        "boxborderw=32,"

        "drawtext="
        f"fontfile={font_file}:"
        f"textfile={script_file}:"
        "fontcolor=white:"
        "fontsize=48:"
        "line_spacing=20:"
        "x=65:"
        "y=(h-text_h)/2:"
        "box=1:"
        "boxcolor=black@0.52:"
        "boxborderw=38,"

        "drawbox="
        "x=70:"
        "y=h-330:"
        "w=940:"
        "h=8:"
        "color=white@0.65:"
        "t=fill,"

        "drawtext="
        f"fontfile={font_file}:"
        "text='AI Viral Content':"
        "fontcolor=white@0.8:"
        "fontsize=34:"
        "x=(w-text_w)/2:"
        "y=h-120"
        "[v];"

        "[1:a]"
        "volume=1.0"
        "[voice];"

        "[2:a]"
        "volume=0.10"
        "[music];"

        "[voice][music]"
        "amix="
        "inputs=2:"
        "duration=first:"
        "dropout_transition=2"
        "[a]"
    )

    # -------------------------
    # FFmpeg
    # -------------------------

    command = [
        "ffmpeg",
        "-y",

        "-f",
        "lavfi",

        "-i",
        f"color=c=0x08111f:s={WIDTH}x{HEIGHT}:r={FPS}",

        "-i",
        str(voice_file),

        "-i",
        str(music_file),

        "-filter_complex",
        video_filter,

        "-map",
        "[v]",

        "-map",
        "[a]",

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

    # Don't hide FFmpeg error anymore.
    subprocess.run(
        command,
        check=True
    )

    return output_file
