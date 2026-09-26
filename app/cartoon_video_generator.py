from pathlib import Path
import subprocess
from PIL import Image

from cartoon_story_generator import get_daily_story

BASE_DIR = Path(__file__).resolve().parent.parent

CHARACTER_IMAGE = (
    BASE_DIR
    / "app"
    / "ChatGPT Image Sep 26, 2026, 01_39_48 PM.png"
)

OUTPUT_DIR = BASE_DIR / "data" / "generated" / "cartoon_daily"

WIDTH = 1080
HEIGHT = 1920
FPS = 30


def check_character():
    if not CHARACTER_IMAGE.exists():
        raise FileNotFoundError(
            f"Character image not found: {CHARACTER_IMAGE}"
        )

    image = Image.open(CHARACTER_IMAGE)

    print("Funny Boy character loaded.")
    print("Character image size:", image.size)

    return image


def create_video(story):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "funny_boy_daily.mp4"

    title_file = OUTPUT_DIR / "title.txt"
    story_file = OUTPUT_DIR / "story.txt"

    title_file.write_text(
        story["title"],
        encoding="utf-8"
    )

    story_text = (
        story["story_bn"]
        + "\n\n"
        + story["story_hi"]
    )

    story_file.write_text(
        story_text,
        encoding="utf-8"
    )

    # Character image is converted into a vertical 9:16 background.
    image_filter = (
        f"scale={WIDTH}:{HEIGHT}:"
        "force_original_aspect_ratio=decrease,"
        f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:"
        "color=0x08111f,"
        "zoompan="
        f"z='min(zoom+0.0008,1.08)':"
        f"d={FPS * 20}:"
        f"s={WIDTH}x{HEIGHT}:"
        f"fps={FPS},"
        "drawtext="
        f"fontfile=/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf:"
        f"textfile='{title_file}':"
        "fontcolor=white:"
        "fontsize=52:"
        "x=(w-text_w)/2:"
        "y=130:"
        "box=1:"
        "boxcolor=black@0.55:"
        "boxborderw=25,"
        "drawtext="
        f"fontfile=/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf:"
        f"textfile='{story_file}':"
        "fontcolor=white:"
        "fontsize=38:"
        "line_spacing=16:"
        "x=55:"
        "y=1450:"
        "box=1:"
        "boxcolor=black@0.65:"
        "boxborderw=30"
    )

    command = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        str(CHARACTER_IMAGE),
        "-vf",
        image_filter,
        "-t",
        "20",
        "-r",
        str(FPS),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "24",
        "-pix_fmt",
        "yuv420p",
        str(output_file),
    ]

    print("Creating Funny Boy cartoon video...")

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Cartoon video generation failed.")

    print("Cartoon video created:")
    print(output_file)

    return output_file


def main():
    print("=" * 60)
    print("FUNNY BOY DAILY CARTOON GENERATOR")
    print("=" * 60)

    check_character()

    story = get_daily_story()

    print("Today's story:")
    print(story["title"])

    create_video(story)

    print("=" * 60)
    print("FUNNY BOY CARTOON SUCCESS")
    print("=" * 60)


if __name__ == "__main__":
    main()
