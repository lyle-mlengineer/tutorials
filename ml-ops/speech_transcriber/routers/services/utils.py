from routers.services.transcription_service import TranscriptionService

async def get_transcription_service() -> TranscriptionService:
    return TranscriptionService()