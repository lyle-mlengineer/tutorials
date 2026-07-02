from pydantic import BaseModel


class PreloadAudioResponse(BaseModel):
    audio_url: str
    audio_id: str