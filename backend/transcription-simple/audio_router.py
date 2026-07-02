from fastapi import Depends, FastAPI, Request, status, APIRouter
from audio_service import AudioFileService
from utils import get_audio_service

router = APIRouter(
    tags=["Audio Operations"],
)

@router.get("/audio/unlabelled", status_code=status.HTTP_200_OK)
async def get_unlabelled_audio(audio_service: AudioFileService = Depends(get_audio_service)):
    audio_file = audio_service.get_unlabelled_audio_file()
    if audio_file:
        return {"audio_id": audio_file.id, "file_id": audio_file.fileid}
    else:
        return {"message": "No unlabelled audio files available."}
    
@router.get("/audio/preload", status_code=status.HTTP_200_OK)
async def preload_audio(request: Request, audio_service: AudioFileService = Depends(get_audio_service)):
    preload_response = audio_service.preload_audio(request)
    if preload_response:
        return preload_response
    else:
        return {"message": "No unlabelled audio files available for preloading."}