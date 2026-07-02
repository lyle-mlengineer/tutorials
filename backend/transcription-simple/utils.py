from audio_service import AudioFileService
from db import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from extensions import get_google_drive
from oryks_google_drive import GoogleDrive


def get_audio_service(db: Annotated[Session, Depends(get_db)], drive: Annotated[GoogleDrive, Depends(get_google_drive)]) -> AudioFileService:
    return AudioFileService(db, drive)