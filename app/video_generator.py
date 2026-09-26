import shutil
import subprocess
from pathlib import Path

from voice_generator import create_voice


WIDTH = 1080
HEIGHT = 1920
FPS = 30


def escape_text(text):
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace(",", "\\,")
        .replace("%", "\\%")
        .replace("\n", " ")
    )


def get_duration(audio_file):
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
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
        "-f", "lavfi",
        "-i",
        (
            "sine=frequency=110:"
            f"sample_rate=44100:"
            f"duration={duration}"
        ),
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
    # Voice
    # -------------------------

    voice_file = create_voice(content, out_dir)
    duration = get_duration(voice_file)

    # -------------------------
    # Background music
    # -------------------------

    music_file = create_music(
        out_dir,
        duration
    )

    output_file = out_dir / "video.mp4"

    title = escape_text(
        content["title"][:85]
    )

    script = escape_text(
        content["script"][:260]
    )

    # -------------------------
    # Animated background
    # -------------------------

    background = (
        "color=c=0x08111f:"
        f"s={WIDTH}x{HEIGHT}:"
        f"r={FPS}"
    )

    # Moving light effect
    moving_light = (
        "drawbox="
        "x='120+180*sin(t*0.8)':"
        "y='180+250*cos(t*0.6)':"
        "w=520:"
        "h=520:"
        "color=0x2563eb@0.16:"
        "t=fill"
    )

    moving_light_2 = (
        "drawbox="
        "x='500+200*cos(t*0.7)':"
        "y='1000+250*sin(t*0.5)':"
        "w=600:"
        "h=600:"
        "color=0x7c3aed@0.13:"
        "t=fill"
    )

    # -------------------------
    # Title
    # -------------------------

    title_layer = (
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"text='{title}':"
        "fontcolor=white:"
        "fontsize=62:"
        "line_spacing=12:"
        "x=(w-text_w)/2:"
        "y=230:"
        "box=1:"
        "boxcolor=black@0.45:"
        "boxborderw=32"
    )

    # -------------------------
    # Captions
    # -------------------------

    caption_layer = (
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        f"text='{script}':"
        "fontcolor=white:"
        "fontsize=48:"
        "line_spacing=20:"
        "x=65:"
        "y=(h-text_h)/2:"
        "box=1:"
        "boxcolor=black@0.52:"
        "boxborderw=38"
    )

    # -------------------------
    # Caption indicator
    # -------------------------

    caption_bar = (
        "drawbox="
        "x=70:"
        "y=h-330:"
        "w=940:"
        "h=8:"
        "color=white@0.65:"
        "t=fill"
    )

    # -------------------------
    # Branding
    # -------------------------

    branding = (
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        "text='AI Viral Content':"
        "fontcolor=white@0.8:"
        "fontsize=34:"
        "x=(w-text_w)/2:"
        "y=h-120"
    )

    video_filter = ",".join([
        moving_light,
        moving_light_2,
        title_layer,
        caption_layer,
        caption_bar,
        branding,
    ])

    # -------------------------
    # Mix voice + music
    # -------------------------

    command = [
        "ffmpeg",
        "-y",

        "-f", "lavfi",
        "-i", background,

        "-i", str(voice_file),

        "-i", str(music_file),

        "-vf", video_filter,

        "-filter_complex",
        (
            "[1:a]volume=1.0[voice];"
            "[2:a]volume=0.10[music];"
            "[voice][music]"
            "amix=inputs=2:"
            "duration=first:"
            "dropout_transition=2"
            "[audio]"
        ),

        "-map", "0:v:0",
        "-map", "[audio]",

        "-t", str(duration),

        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "24",

        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "128k",

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
