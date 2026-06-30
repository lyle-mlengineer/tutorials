from sqlalchemy.orm import Session
from models import DatasetCreate, DatasetRead, ExtractionResponse, VideoRead, VideoCreate
from db import Dataset
import uuid
from extraction_utils import extract_video_timestamps, find_video_parse_video, parse_video_id, preprocess_video
from schemas import FindVideoResponse
from tubectrl import YouTube
from db import VideoExtraction, Video as VideoInDb


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
    
class VideoService:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, video: VideoCreate) -> VideoRead:
        db_video = VideoInDb(
            id=video.id,
            title=video.title,
            description=video.description
        )
        self.db.add(db_video)
        self.db.commit()
        self.db.refresh(db_video)
        return VideoRead.from_video(db_video)
    
    async def create_from_url(self, video_url: str, youtube: YouTube) -> VideoRead:
        video: VideoCreate = preprocess_video(video_url, youtube)
        return await self.create(video)
    
    async def get(self, id: str) -> VideoRead:
        video: VideoInDb = self.db.query(VideoInDb).filter(VideoInDb.id == id).first()
        if not video:
            return None
        return VideoRead.from_video(video)
    
    async def get_by_id(self, id: str) -> VideoRead:
        video: VideoInDb = self.db.query(VideoInDb).filter(VideoInDb.id == id).first()
        if not video:
            return None
        return VideoRead.from_video(video)
    
    async def get_all(self) -> list[VideoRead]:
        videos: list[VideoInDb] = self.db.query(VideoInDb).all()
        return [VideoRead.from_video(video) for video in videos if video]
    
    async def delete(self, id: str):
        video: VideoInDb = self.db.query(VideoInDb).filter(VideoInDb.id == id).first()
        if not video:
            return None
        self.db.delete(video)
        self.db.commit()
    

class TimestampsExtractionService:
    def __init__(self, db: Session, youtube: YouTube, video_service: VideoService):
        self.db = db
        self.youtube = youtube
        self.video_service = video_service

    async def extract_video_timestamps(self, video_url: str, dataset_id: str):
        video_id: str = parse_video_id(video_url)
        video: VideoInDb = await self.video_service.get_by_id(video_id)
        if not video:
            video = await self.video_service.create_from_url(video_url, self.youtube)
        video_extraction: VideoExtraction = await self.get_timestamps_by_video_id(video_id)
        if video_extraction:
            return video_extraction
        extraction_response: ExtractionResponse = await extract_video_timestamps(video_url, self.youtube)
        video_extraction: VideoExtraction = VideoExtraction(
            id=extraction_response.video_id,
            video_id=extraction_response.video_id,
            dataset_id=dataset_id,
            timestamps={
                "timestamps": [timestamp.model_dump() for timestamp in extraction_response.timestamps]
            },
        )
        self.db.add(video_extraction)
        self.db.commit()
        return video_extraction

    async def get_timestamps(self, dataset_id: str):
        pass

    async def get_timestamps_by_video_id(self, video_id: str):
        video_extraction: VideoExtraction = self.db.query(VideoExtraction).filter(VideoExtraction.video_id == video_id).first()
        return video_extraction

    async def find_video(self, video_url: str, dataset_id: str) -> FindVideoResponse:
        await self.extract_video_timestamps(video_url, dataset_id)
        return await find_video_parse_video(video_url, self.youtube)