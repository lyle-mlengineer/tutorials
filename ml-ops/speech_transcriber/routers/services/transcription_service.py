from fastapi import UploadFile, HTTPException, Request
import os
import uuid
import aiofiles
from core.config import settings as config
from routers.schemas import TranscriptionResponse
from fastapi import Request


class TranscriptionService:
    def __init__(self, model_name: str = "openai/whisper-large"):
        self.model_name = model_name
        self.model = None

    async def save_file(self, file: UploadFile, request: Request) -> str:
        # Generate a secure, unique filename to prevent path traversal and overwrites
        file_extension = os.path.splitext(file.filename)[1]
        secure_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(config.DATA_DIR, secure_filename)
        file_url: str = request.url_for("data", path=secure_filename).__str__()

        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                content = await file.read()  # Read file content
                await out_file.write(content)  # Write to disk
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
        finally:
            # Ensure the temporary file is closed
            await file.close()
        return file_url

    async def transcribe(self, file: UploadFile, request: Request) -> TranscriptionResponse:
        file_url = await self.save_file(file, request)
        # self.load_model()
        # result = self.model(audio_file_path)
        # return result["text"]
        return TranscriptionResponse(transcription="Sample transcription", audio_url=file_url)