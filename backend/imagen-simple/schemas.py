from __future__ import annotations

from pydantic import BaseModel
from db import GeneratedImage
from datetime import datetime


class ImageGenerationResponse(BaseModel):
    id: str
    format: str
    date_created: datetime

    @classmethod
    def from_generated_image(cls, generated_image: GeneratedImage) -> ImageGenerationResponse:
        return cls(id=generated_image.id, format=generated_image.format, date_created=generated_image.date_created)