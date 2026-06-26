from pydantic import BaseModel
from typing import Literal


class ImageLabelRequest(BaseModel):
    tags: list[str] = []
    description: str
    gender: Literal["male", "female"]

class ImageLabelResponse(BaseModel):
    id: str
