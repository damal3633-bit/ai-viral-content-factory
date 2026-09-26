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
    print("RUNNING:", description)
    print("=" * 70)

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
            f"{description} failed with exit code {result.returncode}"
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

    try:
        duration = float(result.stdout.strip())
    except ValueError:
        duration = 1.0

    return max(duration, 1.0)


def create_music(out_dir, duration):
    music_file = Path(out_dir) / "background_music.wav"

    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        (
            f"sine=frequency=110:"
            f"sample_rate=44100:"
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
        "Generate background music",
    )

    return music_file


def remove_emoji(text):
    if not text:
        return ""

    pattern = re.compile(
        "["
        "\U0001F300-\U0001FAFF"
        "\U00002700-\U000027BF"
        "\U00002600-\U000026FF"
        "\U0001F1E6-\U0001F1FF"
        "]",
        flags=re.UNICODE,
    )

    return pattern.sub("", str(text))


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


def get_normal_font():
    return (
        "/usr/share/fonts/truetype/noto/"
        "NotoSans-Regular.ttf"
    )


def get_bengali_font():
    return (
        "/usr/share/fonts/truetype/noto/"
        "NotoSansBengali-Regular.ttf"
    )


def get_devanagari_font():
    return (
        "/usr/share/fonts/truetype/noto/"
        "NotoSansDevanagari-Regular.ttf"
    )


def get_title_font(text):
    if contains_bengali(text):
        return get_bengali_font()

    if contains_devanagari(text):
        return get_devanagari_font()

    return get_normal_font()


def get_script_font(text):
    # Bengali
    if contains_bengali(text):
        return get_bengali_font()

    # Real Devanagari Hindi
    if contains_devanagari(text):
        return get_devanagari_font()

    # Roman Hindi / English
    return get_normal_font()


def wrap_text(text, max_chars):
    """
    Wrap text so that long lines do not go outside
    the 1080x1920 screen.
    """

    if not text:
        return ""

    text = str(text).replace("\r\n", "\n")

    paragraphs = text.split("\n")

    final_lines = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            final_lines.append("")
            continue

        words = paragraph.split()

        current = ""

        for word in words:

            if not current:
                current = word
                continue

            candidate = current + " " + word

            if len(candidate) <= max_chars:
                current = candidate
            else:
                final_lines.append(current)
                current = word

        if current:
            final_lines.append(current)

    return "\n".join(final_lines)


def clean_visual_script(script, content):
    if not script:
        return ""

    text = str(script)

    # Remove emoji
    text = remove_emoji(text)

    # Remove URLs
    text = re.sub(
        r"https?://\S+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove the exact title only when it appears
    # as a complete standalone line.
    title = str(
        content.get("title", "")
    ).strip()

    if title:
        title_pattern = (
            r"(?m)^[ \t]*"
            + re.escape(title)
            + r"[ \t]*$"
        )

        text = re.sub(
            title_pattern,
            "",
            text,
        )

    # Remove excessive blank lines
    text = re.sub(
        r"\n[ \t]*\n[ \t]*\n+",
        "\n\n",
        text,
    )

    # Remove spaces before punctuation
    text = re.sub(
        r"\s+([,.;!?।])",
        r"\1",
        text,
    )

    return text.strip()


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

    # ==================================================
    # 1. VOICE
    # ==================================================

    print("\n[1/5] Generating voice...")

    voice_file = create_voice(
        content,
        out_dir,
    )

    if not voice_file.exists():
        raise RuntimeError(
            "Voice file was not created."
        )

    duration = get_duration(
        voice_file
    )

    print(
        f"Voice duration: {duration:.2f} seconds"
    )

    # ==================================================
    # 2. MUSIC
    # ==================================================

    print("\n[2/5] Generating background music...")

    music_file = create_music(
        out_dir,
        duration,
    )

    if not music_file.exists():
        raise RuntimeError(
            "Music file was not created."
        )

    # ==================================================
    # 3. PREPARE TEXT
    # ==================================================

    print("\n[3/5] Preparing text...")

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

    # -------------------------------
    # TITLE
    # -------------------------------

    title_text = remove_emoji(
        original_title
    )

    title_text = wrap_text(
        title_text,
        32,
    )

    # -------------------------------
    # SCRIPT
    # -------------------------------

    script_text = clean_visual_script(
        original_script,
        content,
    )

    if not script_text:
        script_text = remove_emoji(
            original_script
        )

    # Language-specific wrapping
    if contains_bengali(script_text):
        script_text = wrap_text(
            script_text,
            28,
        )

    elif contains_devanagari(script_text):
        script_text = wrap_text(
            script_text,
            28,
        )

    else:
        script_text = wrap_text(
            script_text,
            38,
        )

    # Prevent an extremely large caption box.
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
        "Title:",
        title_text,
    )

    print(
        "Script:",
        script_text,
    )

    # ==================================================
    # 4. FONTS
    # ==================================================

    title_font = get_title_font(
        title_text
    )

    script_font = get_script_font(
        script_text
    )

    normal_font = get_normal_font()

    print(
        "Language:",
        language,
    )

    print(
        "Title font:",
        title_font,
    )

    print(
        "Script font:",
        script_font,
    )

    for font in [
        title_font,
        script_font,
        normal_font,
    ]:

        if not Path(font).exists():
            raise RuntimeError(
                f"Font not found: {font}"
            )

    # ==================================================
    # 5. RENDER VIDEO
    # ==================================================

    print("\n[4/5] Rendering animated video...")

    output_file = (
        out_dir / "video.mp4"
    )

    video_filter = (

        "[0:v]"

        # ----------------------------------------------
        # BLUE MOVING LIGHT
        # ----------------------------------------------

        "drawbox="
        "x=120+180*sin(t*0.8):"
        "y=180+250*cos(t*0.6):"
        "w=520:"
        "h=520:"
        "color=0x2563eb@0.16:"
        "t=fill,"

        # ----------------------------------------------
        # PURPLE MOVING LIGHT
        # ----------------------------------------------

        "drawbox="
        "x=500+200*cos(t*0.7):"
        "y=1000+250*sin(t*0.5):"
        "w=600:"
        "h=600:"
        "color=0x7c3aed@0.13:"
        "t=fill,"

        # ----------------------------------------------
        # MOVING HIGHLIGHT
        # ----------------------------------------------

        "drawbox="
        "x=40+120*sin(t*1.2):"
        "y=650+180*cos(t*0.9):"
        "w=1000:"
        "h=5:"
        "color=white@0.10:"
        "t=fill,"

        # ----------------------------------------------
        # TITLE
        # ----------------------------------------------

        "drawtext="
        f"fontfile={title_font}:"
        f"textfile={title_file}:"
        "fontcolor=white:"
        "fontsize=50:"
        "line_spacing=8:"
        "x=(w-text_w)/2:"
        "y=190:"
        "box=1:"
        "boxcolor=black@0.52:"
        "boxborderw=26,"

        # ----------------------------------------------
        # MAIN SCRIPT
        # ----------------------------------------------

        "drawtext="
        f"fontfile={script_font}:"
        f"textfile={script_file}:"
        "fontcolor=white:"
        "fontsize=42:"
        "line_spacing=18:"
        "x=70:"
        "y=(h-text_h)/2:"
        "box=1:"
        "boxcolor=black@0.55:"
        "boxborderw=32,"

        # ----------------------------------------------
        # BOTTOM LINE
        # ----------------------------------------------

        "drawbox="
        "x=70:"
        "y=h-330:"
        "w=940:"
        "h=8:"
        "color=white@0.65:"
        "t=fill,"

        # ----------------------------------------------
        # FOOTER
        # ----------------------------------------------

        "drawtext="
        f"fontfile={normal_font}:"
        "text='AI Viral Content':"
        "fontcolor=white@0.85:"
        "fontsize=34:"
        "x=(w-text_w)/2:"
        "y=h-120"

        "[v];"

        # ----------------------------------------------
        # VOICE
        # ----------------------------------------------

        "[1:a]"
        "volume=1.0"
        "[voice];"

        # ----------------------------------------------
        # MUSIC
        # ----------------------------------------------

        "[2:a]"
        "volume=0.10"
        "[music];"

        # ----------------------------------------------
        # MIX
        # ----------------------------------------------

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

        # 9:16 background
        "-f",
        "lavfi",

        "-i",
        (
            f"color=c=0x08111f:"
            f"s={WIDTH}x{HEIGHT}:"
            f"r={FPS}"
        ),

        # Voice
        "-i",
        str(voice_file),

        # Music
        "-i",
        str(music_file),

        # Filters
        "-filter_complex",
        video_filter,

        # Video
        "-map",
        "[v]",

        # Audio
        "-map",
        "[a]",

        # Duration
        "-t",
        str(duration),

        # Video codec
        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "24",

        "-pix_fmt",
        "yuv420p",

        # Audio codec
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

    # ==================================================
    # VERIFY
    # ==================================================

    print("\n[5/5] Verifying final video...")

    if not output_file.exists():
        raise RuntimeError(
            "Video file was not created."
        )

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
            "Final video is not 1080x1920."
        )

    print("\n" + "=" * 70)
    print("FINAL VIDEO CREATED SUCCESSFULLY")
    print("=" * 70)

    print(
        "Output:",
        output_file,
    )

    return output_file
