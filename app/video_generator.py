import re
import shutil
import subprocess
from pathlib import Path

from voice_generator import create_voice


WIDTH = 1080
HEIGHT = 1920
FPS = 30


def run_command(command, description):
    print("\n" + "=" * 70)
    print(f"RUNNING: {description}")
    print("=" * 70)
    print("COMMAND:")
    print(" ".join(str(x) for x in command))
    print()

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"{description} failed with exit code "
            f"{result.returncode}"
        )

    return result


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

    value = result.stdout.strip()

    try:
        duration = float(value)
    except ValueError:
        duration = 1.0

    return max(duration, 1.0)


def create_music(out_dir, duration):
    """
    Generate simple copyright-safe background music.
    This is generated locally by FFmpeg.
    """

    music_file = Path(out_dir) / "background_music.wav"

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        (
            "sine="
            "frequency=110:"
            "sample_rate=44100:"
            f"duration={duration}"
        ),
        "-filter:a",
        "volume=0.035",
        "-c:a",
        "pcm_s16le",
        str(music_file),
    ]

    run_command(
        command,
        "Generate copyright-safe background music",
    )

    return music_file


def remove_emoji(text):
    """
    Remove emoji/symbol characters that may become tofu boxes
    in FFmpeg drawtext on Ubuntu.
    """

    if not text:
        return ""

    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001FAFF"
        "\U00002700-\U000027BF"
        "\U00002600-\U000026FF"
        "\U0001F1E6-\U0001F1FF"
        "]",
        flags=re.UNICODE,
    )

    return emoji_pattern.sub("", text)


def remove_source_text(script, content):
    """
    The AI script sometimes repeats the original English news
    title/source topic.

    Removing that repeated English source line from the visual
    caption allows the Bengali/Hindi font to render cleanly.

    IMPORTANT:
    This does NOT change the original script used by Edge-TTS.
    It only changes the on-screen caption file.
    """

    if not script:
        return ""

    cleaned = script

    candidates = [
        content.get("title", ""),
        content.get("source_topic", ""),
    ]

    for item in candidates:
        if item:
            cleaned = cleaned.replace(item, "")

    cleaned = remove_emoji(cleaned)

    # Remove excessive blank lines.
    cleaned = re.sub(
        r"\n[ \t]*\n[ \t]*\n+",
        "\n\n",
        cleaned,
    )

    cleaned = cleaned.strip()

    return cleaned


def wrap_text(text, width):
    """
    Simple wrapping for title so long titles do not run outside
    the 1080x1920 frame.
    """

    if not text:
        return ""

    words = text.split()
    lines = []
    current = ""

    for word in words:
        if not current:
            current = word
            continue

        candidate = current + " " + word

        if len(candidate) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return "\n".join(lines)


def contains_bengali(text):
    return bool(
        re.search(
            r"[\u0980-\u09FF]",
            text or "",
        )
    )


def contains_devanagari(text):
    return bool(
        re.search(
            r"[\u0900-\u097F]",
            text or "",
        )
    )


def get_script_font(language):
    if language == "bn":
        return (
            "/usr/share/fonts/truetype/noto/"
            "NotoSansBengali-Regular.ttf"
        )

    if language == "hi":
        return (
            "/usr/share/fonts/truetype/noto/"
            "NotoSansDevanagari-Regular.ttf"
        )

    return (
        "/usr/share/fonts/truetype/noto/"
        "NotoSans-Regular.ttf"
    )


def get_title_font(title, language):
    """
    Titles in the current project are mostly English source titles.
    Use the normal Noto Sans font for Latin text so English letters
    do not become square boxes.

    If a future title is actually Bengali/Hindi, use its language
    font.
    """

    if contains_bengali(title):
        return (
            "/usr/share/fonts/truetype/noto/"
            "NotoSansBengali-Regular.ttf"
        )

    if contains_devanagari(title):
        return (
            "/usr/share/fonts/truetype/noto/"
            "NotoSansDevanagari-Regular.ttf"
        )

    return (
        "/usr/share/fonts/truetype/noto/"
        "NotoSans-Regular.ttf"
    )


def create_video(content, out_dir):
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "FFmpeg is not installed."
        )

    if not shutil.which("ffprobe"):
        raise RuntimeError(
            "FFprobe is not installed."
        )

    out_dir = Path(out_dir)
    out_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\n" + "#" * 70)
    print("START VIDEO GENERATION")
    print("#" * 70)

    language = content.get(
        "language",
        "bn",
    )

    # -------------------------------------------------
    # 1. Generate Edge-TTS voice
    # -------------------------------------------------

    print("\n[1/5] Generating voice...")

    voice_file = create_voice(
        content,
        out_dir,
    )

    print(
        f"Voice created: {voice_file}"
    )

    duration = get_duration(
        voice_file
    )

    print(
        f"Voice duration: {duration:.2f} seconds"
    )

    # -------------------------------------------------
    # 2. Generate background music
    # -------------------------------------------------

    print("\n[2/5] Generating background music...")

    music_file = create_music(
        out_dir,
        duration,
    )

    print(
        f"Music created: {music_file}"
    )

    # -------------------------------------------------
    # 3. Prepare text files
    # -------------------------------------------------

    print("\n[3/5] Preparing Unicode text files...")

    original_title = str(
        content.get(
            "title",
            "AI Viral Content",
        )
    )

    original_script = str(
        content.get(
            "script",
            "",
        )
    )

    title_text = remove_emoji(
        original_title
    )

    # Keep title inside screen.
    title_text = wrap_text(
        title_text,
        34,
    )

    # For captions, remove the repeated English source
    # title/topic and keep the actual Bengali/Hindi text.
    script_text = remove_source_text(
        original_script,
        content,
    )

    # Fallback if the cleaning removed too much.
    if not script_text:
        script_text = remove_emoji(
            original_script
        )

    # Limit visual caption size.
    script_text = script_text[:900]

    title_file = (
        out_dir / "title.txt"
    )

    script_file = (
        out_dir / "script.txt"
    )

    title_file.write_text(
        title_text,
        encoding="utf-8",
    )

    script_file.write_text(
        script_text,
        encoding="utf-8",
    )

    print(
        f"Title file: {title_file}"
    )

    print(
        f"Script file: {script_file}"
    )

    # -------------------------------------------------
    # 4. Select fonts
    # -------------------------------------------------

    title_font = get_title_font(
        title_text,
        language,
    )

    script_font = get_script_font(
        language,
    )

    print(
        f"Language: {language}"
    )

    print(
        f"Title font: {title_font}"
    )

    print(
        f"Script font: {script_font}"
    )

    if not Path(title_font).exists():
        raise RuntimeError(
            f"Title font not found: {title_font}"
        )

    if not Path(script_font).exists():
        raise RuntimeError(
            f"Script font not found: {script_font}"
        )

    # -------------------------------------------------
    # 5. Build animated FFmpeg video
    # -------------------------------------------------

    print("\n[4/5] Rendering animated video...")

    output_file = (
        out_dir / "video.mp4"
    )

    video_filter = (
        "[0:v]"

        # Moving blue light
        "drawbox="
        "x=120+180*sin(t*0.8):"
        "y=180+250*cos(t*0.6):"
        "w=520:"
        "h=520:"
        "color=0x2563eb@0.16:"
        "t=fill,"

        # Moving purple light
        "drawbox="
        "x=500+200*cos(t*0.7):"
        "y=1000+250*sin(t*0.5):"
        "w=600:"
        "h=600:"
        "color=0x7c3aed@0.13:"
        "t=fill,"

        # Moving highlight
        "drawbox="
        "x=40+120*sin(t*1.2):"
        "y=650+180*cos(t*0.9):"
        "w=1000:"
        "h=5:"
        "color=white@0.10:"
        "t=fill,"

        # Title
        "drawtext="
        f"fontfile={title_font}:"
        f"textfile={title_file}:"
        "fontcolor=white:"
        "fontsize=60:"
        "line_spacing=10:"
        "x=(w-text_w)/2:"
        "y=190:"
        "box=1:"
        "boxcolor=black@0.50:"
        "boxborderw=30:"

        # Main Bengali/Hindi caption
        "drawtext="
        f"fontfile={script_font}:"
        f"textfile={script_file}:"
        "fontcolor=white:"
        "fontsize=48:"
        "line_spacing=20:"
        "x=65:"
        "y=(h-text_h)/2:"
        "box=1:"
        "boxcolor=black@0.55:"
        "boxborderw=38:"

        # Bottom separator
        "drawbox="
        "x=70:"
        "y=h-330:"
        "w=940:"
        "h=8:"
        "color=white@0.65:"
        "t=fill,"

        # Footer
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/noto/"
        "NotoSans-Regular.ttf:"
        "text='AI Viral Content':"
        "fontcolor=white@0.85:"
        "fontsize=34:"
        "x=(w-text_w)/2:"
        "y=h-120"
        "[v];"

        # Voice
        "[1:a]"
        "volume=1.0"
        "[voice];"

        # Music
        "[2:a]"
        "volume=0.10"
        "[music];"

        # Mix voice + music
        "[voice][music]"
        "amix="
        "inputs=2:"
        "duration=first:"
        "dropout_transition=2"
        "[a]"
    )

    command = [
        "ffmpeg",
        "-y",

        "-f",
        "lavfi",
        "-i",
        (
            f"color=c=0x08111f:"
            f"s={WIDTH}x{HEIGHT}:"
            f"r={FPS}"
        ),

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

    run_command(
        command,
        "Render final 1080x1920 video",
    )

    # -------------------------------------------------
    # Verify final video
    # -------------------------------------------------

    print("\n[5/5] Verifying final video...")

    verify_command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,codec_name",
        "-of",
        "default=noprint_wrappers=1",
        str(output_file),
    ]

    verify = subprocess.run(
        verify_command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    print(verify.stdout)

    if (
        "width=1080" not in verify.stdout
        or "height=1920" not in verify.stdout
    ):
        raise RuntimeError(
            "Final video is NOT 1080x1920."
        )

    print(
        f"\nSUCCESS: {output_file}"
    )

    return output_file
