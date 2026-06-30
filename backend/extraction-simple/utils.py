from db import get_db, engine, Base
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated
from services import DatasetService, TimestampsExtractionService, VideoService
from models import DatasetRead
from extensions import youtube


def get_dataset_service(db: Annotated[Session, Depends(get_db)]):
    return DatasetService(db)

def create_all():
    Base.metadata.create_all(bind=engine)


async def get_datasets(dataset_service: DatasetService = Depends(get_dataset_service)):
    datasets: list[DatasetRead] = await dataset_service.get_datasets()
    return [
        {
            "id": dataset.id,
            "name": dataset.name,
        } for dataset in datasets
    ]

def get_video_service(db: Annotated[Session, Depends(get_db)]):
    return VideoService(db)

def get_timestamps_extraction_service(db: Annotated[Session, Depends(get_db)], video_service: VideoService = Depends(get_video_service)):
    return TimestampsExtractionService(db, youtube, video_service)