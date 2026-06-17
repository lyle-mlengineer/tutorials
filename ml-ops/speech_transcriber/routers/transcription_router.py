from fastapi import APIRouter, Depends, Request
from fastapi import File, UploadFile, HTTPException
from routers.services.transcription_service import TranscriptionService
from routers.schemas import TranscriptionResponse
from routers.services.utils import get_transcription_service


router = APIRouter(
    tags=["Transcription Operations"],
)


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
            file: UploadFile, 
            request: Request,
            transcription_service: TranscriptionService = Depends(get_transcription_service)
            ) -> TranscriptionResponse:
    if file.content_type not in {"audio/mp3", "audio/wav"}:
            raise HTTPException(status_code=415, detail="Unsupported file type.")
    if file.size > 10 * 1024 * 1024:  # 10 MB limit
            raise HTTPException(status_code=413, detail="File too large.")
    return await transcription_service.transcribe(file, request)