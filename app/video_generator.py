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
        return max(float(result.stdout.strip()), 1.0)
    except ValueError:
        return 1.0


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

    run_command(command, "Generate background music")
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
    return bool(re.search(r"[\u0980-\u09FF]", text or ""))


def contains_devanagari(text):
    return bool(re.search(r"[\u0900-\u097F]", text or ""))


def normal_font():
    return "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def bengali_font():
    return "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf"


def devanagari_font():
    return "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"


def wrap_text(text, max_chars):
    if not text:
        return ""

    lines = []

    for paragraph in str(text).replace("\r\n", "\n").split("\n"):
        paragraph = paragraph.strip()

        if not paragraph:
            if lines and lines[-1] != "":
                lines.append("")
            continue

        words = paragraph.split()
        current = ""

        for word in words:
            if not current:
                current = word
            elif len(current) + 1 + len(word) <= max_chars:
                current += " " + word
            else:
                lines.append(current)
                current = word

        if current:
            lines.append(current)

    return "\n".join(lines)


def clean_script(script, content, language):
    text = remove_emoji(str(script or ""))

    title = str(content.get("title", "")).strip()
    source_topic = str(content.get("source_topic", "")).strip()

    # Remove repeated source title/topic from the visual caption.
    for value in (title, source_topic):
        if value:
            text = text.replace(value, "")

    # Bengali visual text should not contain English/number
    # characters because they can create font boxes/squares.
    if language == "bn":
        text = re.sub(r"[A-Za-z0-9]+", "", text)

    # Remove URLs.
    text = re.sub(
        r"https?://\S+",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Clean spaces and repeated blank lines.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(
        r"\n[ \t]*\n[ \t]*\n+",
        "\n\n",
        text,
    )

    text = re.sub(
        r"[ \t]+([,.;!?।])",
        r"\1",
        text,
    )

    return text.strip()


def create_video(content, out_dir):
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed.")

    if not shutil.which("ffprobe"):
        raise RuntimeError("FFprobe is not installed.")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    language = content.get("language", "bn")

    print("\n" + "#" * 70)
    print("START VIDEO GENERATION")
    print("#" * 70)

    # ---------------------------------------------------------
    # 1. VOICE
    # ---------------------------------------------------------
    print("\n[1/5] Generating voice...")

    voice_file = create_voice(content, out_dir)

    if not voice_file.exists():
        raise RuntimeError("Voice file was not created.")

    duration = get_duration(voice_file)

    print(f"Voice duration: {duration:.2f} seconds")

    # ---------------------------------------------------------
    # 2. BACKGROUND MUSIC
    # ---------------------------------------------------------
    print("\n[2/5] Generating background music...")

    music_file = create_music(
        out_dir,
        duration,
    )

    # ---------------------------------------------------------
    # 3. VISUAL TEXT
    # ---------------------------------------------------------
    print("\n[3/5] Preparing visual text...")

    title = remove_emoji(
        str(content.get("title", "AI Viral Content"))
    )

    title = wrap_text(
        title,
        30,
    )

    script = clean_script(
        content.get("script", ""),
        content,
        language,
    )

    if not script:
        if language == "bn":
            script = (
                "এই বিষয়টি নিয়ে বর্তমানে "
                "আলোচনা চলছে।"
            )
        else:
            script = (
                "Is topic par abhi "
                "charcha chal rahi hai."
            )

    # Prevent excessively large captions.
    script = script[:450]

    # Bengali
    if contains_bengali(script):
        script = wrap_text(
            script,
            30,
        )

    # Devanagari Hindi
    elif contains_devanagari(script):
        script = wrap_text(
            script,
            30,
        )

    # Roman Hindi / English
    else:
        script = wrap_text(
            script,
            36,
        )

    title_file = out_dir / "title.txt"
    script_file = out_dir / "script.txt"

    title_file.write_text(
        title,
        encoding="utf-8",
    )

    script_file.write_text(
        script,
        encoding="utf-8",
    )

    # ---------------------------------------------------------
    # 4. FONT SELECTION
    # ---------------------------------------------------------
    title_font = normal_font()

    if contains_bengali(title):
        title_font = bengali_font()

    elif contains_devanagari(title):
        title_font = devanagari_font()

    script_font = normal_font()

    if contains_bengali(script):
        script_font = bengali_font()

    elif contains_devanagari(script):
        script_font = devanagari_font()

    for font in (
        title_font,
        script_font,
        normal_font(),
    ):
        if not Path(font).exists():
            raise RuntimeError(
                f"Font not found: {font}"
            )

    print("Title font:", title_font)
    print("Script font:", script_font)

    # ---------------------------------------------------------
    # 5. VIDEO RENDER
    # ---------------------------------------------------------
    print("\n[4/5] Rendering animated video...")

    output_file = out_dir / "video.mp4"

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

        "drawbox="
        "x=40+120*sin(t*1.2):"
        "y=650+180*cos(t*0.9):"
        "w=1000:"
        "h=5:"
        "color=white@0.10:"
        "t=fill,"

        "drawtext="
        f"fontfile={title_font}:"
        f"textfile={title_file}:"
        "fontcolor=white:"
        "fontsize=48:"
        "line_spacing=7:"
        "x=(w-text_w)/2:"
        "y=130:"
        "box=1:"
        "boxcolor=black@0.55:"
        "boxborderw=24,"

        "drawtext="
        f"fontfile={script_font}:"
        f"textfile={script_file}:"
        "fontcolor=white:"
        "fontsize=40:"
        "line_spacing=18:"
        "x=65:"
        "y=500:"
        "box=1:"
        "boxcolor=black@0.58:"
        "boxborderw=30,"

        "drawbox="
        "x=70:"
        "y=h-330:"
        "w=940:"
        "h=8:"
        "color=white@0.65:"
        "t=fill,"

        "drawtext="
        f"fontfile={normal_font()}:"
        "text='AI Viral Content':"
        "fontcolor=white@0.85:"
        "fontsize=34:"
        "x=(w-text_w)/2:"
        "y=h-120"
        "[v];"

        "[1:a]volume=1.0[voice];"

        "[2:a]volume=0.10[music];"

        "[voice][music]"
        "amix=inputs=2:"
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
        f"color=c=0x08111f:"
        f"s={WIDTH}x{HEIGHT}:"
        f"r={FPS}",

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

    # ---------------------------------------------------------
    # VERIFY
    # ---------------------------------------------------------
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
        "\nFINAL VIDEO SUCCESS:",
        output_file,
    )

    return output_file
