from fastapi import UploadFile, HTTPException, Request
import os
import uuid
import aiofiles
from core.config import settings as config
from routers.schemas import TranscriptionResponse
from fastapi import Request
import librosa


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
        return file_path, file_url
    async def _transcribe(self, audio_path: str, processor, model) -> str:
        """Transcribe audio file."""
        model_sample_rate = processor.feature_extractor.sampling_rate

        # load audio file
        audio_data, sample_rate = librosa.load(audio_path, sr=model_sample_rate)

        input_features = processor(
            audio_data,
            sampling_rate=sample_rate,
            return_tensors="pt",
        ).input_features

        # generate tokens -> decode to text
        predicted_ids = model.generate(input_features, language="sw", task="transcribe")
        transcription = processor.batch_decode(
            predicted_ids, skip_special_tokens=True
        )[0]
        return transcription

    async def transcribe(self, file: UploadFile, request: Request, model, processor) -> TranscriptionResponse:
        file_path, file_url = await self.save_file(file, request)
        
        transcription_text = await self._transcribe(file_path, processor, model)
        return TranscriptionResponse(transcription=transcription_text, audio_url=file_url)