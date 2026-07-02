import os
from modal import config
from oryks_google_drive import GoogleDrive
import logging
from fastapi import HTTPException

DATA_DIR = "data"
MAX_PRELOAD: int = 5

def preload_audio_helper(audio_id: str, file_id: str, drive: GoogleDrive):
    preloaded_audio_count: int = count_preloaded_audios()
    if preloaded_audio_count > MAX_PRELOAD:
        raise HTTPException(status_code=400, detail=f"Preloaded audio limit reached. Current count: {preloaded_audio_count}, Limit: {MAX_PRELOAD}")
    prelaoaded_audios = get_preloaded_audio_names()
    if audio_id in prelaoaded_audios:
        logging.info(f"Audio with ID {audio_id} is already preloaded.")
        return
    logging.info(f"Preloading audio with ID {audio_id}")
    try:
        download_audio_from_google_drive(audio_id, file_id, DATA_DIR, drive)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preload audio: {e}")
    else:
        logging.info(f"Successfully preloaded audio with ID {audio_id}")

def count_preloaded_audios():
    audio_dir = DATA_DIR
    count = 0
    for root, dirs, files in os.walk(audio_dir):
        for file in files:
            if file.endswith(".wav"):
                count += 1
    return count

def get_preloaded_audio_names():
    audio_dir = DATA_DIR
    audio_names = []
    for root, dirs, files in os.walk(audio_dir):
        for file in files:
            if file.endswith(".wav"):
                audio_names.append(file.split(".")[0])
    return audio_names


def download_audio_from_google_drive(audio_id: str, file_id: str, destination_path: str, drive: GoogleDrive):
    """Download an audio file from Google Drive to the specified destination path."""
    logging.info(f"Downloading audio file with ID {file_id} from Google Drive")
    try:
        destination_path: str = os.path.join(DATA_DIR, f"{audio_id}.wav")
        drive.download_file(file_id=file_id, file_path=destination_path)
    except Exception as e:
        logging.error(f"Failed to download file from Google Drive: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download file from Google Drive")
        # raise RuntimeError(f"Failed to download file from Google Drive: {e}")
    

def delete_local_audio_file(audio_id: str):
    os.remove(os.path.join(DATA_DIR, f"{audio_id}.wav"))