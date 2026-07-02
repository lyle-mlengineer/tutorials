from sqlalchemy.orm import Session
from oryks_google_drive import GoogleDrive
from db import AudioFile, AudioFileTranscription
from models import AudioFileRead
from schemas import PreloadAudioResponse
from fastapi import HTTPException, Request
from audi_service_utils import preload_audio_helper
import logging


class AudioFileService:
    def __init__(self, session: Session, drive: GoogleDrive):
        self.session = session
        self.drive = drive

    def get_unlabelled_audio_file(self) -> AudioFile | None:
        audio_file = self.session.query(AudioFile).filter_by(transcribed=False).order_by(AudioFile.id).limit(1).first()
        if audio_file:
            return AudioFileRead.from_orm(audio_file)
        return None
    
    def preload_audio(self, request: Request) -> PreloadAudioResponse | None:
        audio: AudioFileRead | None = self.get_unlabelled_audio_file()
        if audio:
            try:
                logging.info(f"Preloading audio with ID {audio.id} and file ID {audio.fileid}")
                preload_audio_helper(audio.id, audio.fileid, self.drive)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to preload audio: {e}")
            logging.info(f"Successfully preloaded audio with ID {audio.id}")
            file_name: str = f"{audio.id}.wav"
            return PreloadAudioResponse(
                audio_url=request.url_for("data", path=f"{file_name}").__str__(),
                audio_id=audio.id
            )
        return None