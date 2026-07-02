import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )

async def get_tags() -> list[dict[str, str]]:
    return [
        {"id": "1", "name": "transcription"},
        {"id": "2", "name": "speech-to-text"},
        {"id": "3", "name": "audio-processing"},
        {"id": "4", "name": "fastapi"},
        {"id": "5", "name": "modal"}
    ]

async def get_speakers() -> list[dict[str, str]]:
    return [
        {"id": "1", "name": "Speaker 1"},
        {"id": "2", "name": "Speaker 2"},
        {"id": "3", "name": "Speaker 3"},
        {"id": "4", "name": "Speaker 4"},
        {"id": "5", "name": "Speaker 5"}
    ]

async def get_accents() -> list[dict[str, str]]:
    return [
        {"id": "1", "name": "English"},
        {"id": "2", "name": "Spanish"},
        {"id": "3", "name": "French"},
        {"id": "4", "name": "German"},
        {"id": "5", "name": "Chinese"}
    ]