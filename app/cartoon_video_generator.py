
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
CHARACTER_IMAGE = BASE_DIR / "app" / "ChatGPT Image Sep 26, 2026, 01_39_48 PM.png"

OUTPUT_DIR = BASE_DIR / "data" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def check_character():
    if not CHARACTER_IMAGE.exists():
        raise FileNotFoundError(
            f"Character image not found: {CHARACTER_IMAGE}"
        )

    image = Image.open(CHARACTER_IMAGE)
    print("Funny Boy character loaded successfully.")
    print(f"Image size: {image.size}")
    return image


def main():
    print("=" * 60)
    print("AI VIRAL CARTOON VIDEO GENERATOR")
    print("=" * 60)

    check_character()

    print("Character setup complete.")
    print("Ready for daily story generation.")


if __name__ == "__main__":
    main()
