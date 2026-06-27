from sqlalchemy.orm import Session
from db import GeneratedImage
from schemas import ImageGenerationResponse
from helpers import generate_image, save_image_bytes
import uuid
from fastapi import Request


class ImageGenerationService:
    def __init__(self, session: Session):
        self.session = session

    async def generate_image(self) -> ImageGenerationResponse:
        image_bytes, format = await generate_image()
        image_id: str = str(uuid.uuid4())
        image_name: str = await save_image_bytes(image_bytes, image_id)
        image: GeneratedImage = GeneratedImage(id=image_id, format=format.lower())
        self.session.add(image)
        self.session.commit()
        return image_bytes, format