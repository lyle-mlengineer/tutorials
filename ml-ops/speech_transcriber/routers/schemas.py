from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    transcription: str
    audio_token_count: int = 0
    text_token_count: int = 0
    audio_url: str = ""