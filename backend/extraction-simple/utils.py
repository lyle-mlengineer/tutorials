from db import get_db, engine, Base
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated
from services import DatasetService
from models import DatasetRead


def get_dataset_service(db: Annotated[Session, Depends(get_db)]):
    return DatasetService(db)

def create_all():
    Base.metadata.create_all(bind=engine)


async def get_datasets(dataset_service: DatasetService = Depends(get_dataset_service)):
    datasets: list[DatasetRead] = await dataset_service.get_datasets()
    return [dataset.name for dataset in datasets if dataset]