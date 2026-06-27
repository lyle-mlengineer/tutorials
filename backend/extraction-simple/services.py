from sqlalchemy.orm import Session
from models import DatasetCreate, DatasetRead
from db import Dataset
import uuid
from extraction_utils import extract_video_timestamps, find_video_parse_video
from schemas import FindVideoResponse
from tubectrl import YouTube


class DatasetService:
    def __init__(self, db: Session):
        self.db = db

    async def create_dataset(self, dataset: DatasetCreate) -> DatasetRead:
        id: str = str(uuid.uuid4())
        db_dataset = Dataset(
            id=id,
            name=dataset.name,
            description=dataset.description
        )
        self.db.add(db_dataset)
        self.db.commit()
        self.db.refresh(db_dataset)
        return DatasetRead.from_dataset(db_dataset)
    
    async def get_datasets(self) -> list[DatasetRead]:
        datasets: list[Dataset] = self.db.query(Dataset).all()
        return [DatasetRead.from_dataset(dataset) for dataset in datasets if dataset]
    
    async def get_dataset(self, id: str) -> DatasetRead:
        dataset: Dataset = self.db.query(Dataset).filter(Dataset.id == id).first()
        if not dataset:
            return None
        return DatasetRead.from_dataset(dataset)
    
    async def get_dataset_by_name(self, name: str) -> DatasetRead:
        dataset: Dataset = self.db.query(Dataset).filter(Dataset.name == name).first()
        if not dataset:
            return None
        return DatasetRead.from_dataset(dataset)
    

class TimestampsExtractionService:
    def __init__(self, db: Session, youtube: YouTube):
        self.db = db
        self.youtube = youtube

    async def extract_video_timestamps(self, video_url: str):
        await extract_video_timestamps(video_url)

    async def get_timestamps(self, dataset_id: str):
        pass

    async def get_timestamps_by_video_id(self, video_id: str):
        pass

    async def find_video(self, video_url: str) -> FindVideoResponse:
        return await find_video_parse_video(video_url, self.youtube)