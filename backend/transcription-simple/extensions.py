from oryks_google_drive import GoogleDrive
from fastapi import HTTPException


def get_google_drive():
    drive = GoogleDrive()
    try:
        drive.authenticate_from_credentials("/home/lyle/.drive/credentials.json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to authenticate Google Drive: {e}")
    return drive