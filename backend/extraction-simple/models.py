from __future__ import annotations
from pydantic import BaseModel
from db import Video, Dataset, VideoExtraction
from datetime import datetime


class DatasetCreate(BaseModel):
    name: str
    description: str

class DatasetRead(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime

    @classmethod
    def from_dataset(cls, dataset: Dataset) -> DatasetRead:
        return DatasetRead(
            id=dataset.id,
            name=dataset.name,
            description=dataset.description,
            created_at=dataset.created_at,
        )