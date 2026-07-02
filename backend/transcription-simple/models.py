from __future__ import annotations
from pydantic import BaseModel
from db import AudioFile, AudioFileTranscription


class AudioFileCreate(BaseModel):
    id: str
    format: str = "wav"
    fileid: str | None = None
    transcribed: bool = False

class AudioFileRead(BaseModel):
    id: str
    format: str
    fileid: str | None
    transcribed: bool = False

    @classmethod
    def from_orm(cls, audio_file: AudioFile) -> AudioFileRead:
        return cls(
            id=audio_file.id,
            format=audio_file.format,
            fileid=audio_file.fileid,
            transcribed=audio_file.transcribed
        )
    
class AudioFileTranscriptionCreate(BaseModel):
    id: str
    audio_file_id: str
    transcription_text: str | None = None
    machine_transcription_text: str | None = None
    metadata: dict | None = {}

class AudioFileTranscriptionRead(BaseModel):
    id: str
    audio_file_id: str
    transcription_text: str | None
    machine_transcription_text: str | None
    metadata: dict | None

    @classmethod
    def from_orm(cls, transcription: AudioFileTranscription) -> AudioFileTranscriptionRead:
        return cls(
            id=transcription.id,
            audio_file_id=transcription.audio_file_id,
            transcription_text=transcription.transcription_text,
            machine_transcription_text=transcription.machine_transcription_text,
            metadata=transcription.metadata
        )