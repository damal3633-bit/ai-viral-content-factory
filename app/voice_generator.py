import asyncio
from pathlib import Path

import edge_tts


VOICE_MAP = {
    "bn": "bn-IN-TanishaaNeural",
    "hi": "hi-IN-MadhurNeural",
}


async def _generate_voice(text, voice, output_file):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="+5%",
        volume="+0%",
    )

    await communicate.save(str(output_file))


def create_voice(content, out_dir):
    language = content.get("language", "bn")
    text = content["script"]

    voice = VOICE_MAP.get(language, VOICE_MAP["bn"])

    output_file = Path(out_dir) / "voice.mp3"

    asyncio.run(
        _generate_voice(
            text,
            voice,
            output_file,
        )
    )

    return output_file
