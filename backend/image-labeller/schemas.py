from __future__ import annotations

from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from db import Image, ImageLabel

class ImageRead(BaseModel):
    id: str
    extension: str
    date_created: datetime
    labelled: bool

    @classmethod
    def from_image(cls, image: Image) -> ImageRead:
        return cls(id=image.id, date_created=image.date_created, labelled=image.labelled, extension=image.extension)
    

class NextImageResponse(ImageRead):
    image_url: str


class ImageLabelRequest(BaseModel):
    tags: list[str] = []
    description: str
    gender: Literal["male", "female"]

class ImageLabelResponse(BaseModel):
    id: str
    image_id: str
    gender: Literal["male", "female"]
    description: str
    tags: list[str]

    @classmethod
    def from_image_label(cls, image_label: ImageLabel) -> ImageLabelResponse:
        return cls(
            id=image_label.id, 
            image_id=image_label.image_id, 
            gender=image_label.gender, 
            description=image_label.description, 
            tags=[tag.tag.name for tag in image_label.image_label_tags]
        )
