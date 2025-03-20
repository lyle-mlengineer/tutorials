from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Text, String, create_engine, Engine, select
from sqlalchemy.dialects.sqlite import JSON
from abc import ABC, abstractmethod
from .models import VideoTimestampsDataset, VideoDescription, Timestamp, VideoUrl, VideoUrls
from pydantic import BaseModel
from fastapi import HTTPException, status
from .utils import parse_video_id, write_videos_to_redis_queue
from sqlalchemy.exc import NoResultFound, OperationalError
import time
from ..config.config import BaseConfig
from fastapi import HTTPException, status
import time
from sqlalchemy.exc import OperationalError

DATABASE_URL = BaseConfig.DATABASE_URL

class BaseRepository(ABC):
    @abstractmethod
    def get(self, video_id: str) -> VideoTimestampsDataset:
        pass

Base = declarative_base()

class VideoTimestampsDataset(BaseModel):
    video_id: str
    description: str = ''
    timestamps: list = [Timestamp]

class VideoTimestampsDatasetDbModel(Base):
    __tablename__ = "video_timestamps_dataset"

    video_id = Column(String, primary_key=True)
    description = Column(Text, nullable=True)
    timestamps = Column(JSON, nullable=True)


class SQLRepository(BaseRepository):
    def __init__(self, session):
        super().__init__()
        self._session = session

    def get(self, video_id: str) -> VideoTimestampsDatasetDbModel:
        success = False
        for _ in range(3):
            try:
                statement = select(VideoTimestampsDatasetDbModel).where(VideoTimestampsDatasetDbModel.video_id == video_id)
                result = self._session.scalars(statement).one()
                success = True
                break
            except OperationalError:
                print('Operational error')
                time.sleep(0.5)
        if success:
            return result
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="We are having an internal issue, try again in 1 minute.")
    

def get_repository() -> BaseRepository:
    connect_args = {"check_same_thread": False}
    # engine: Engine = create_engine(DATABASE_URL, connect_args=connect_args)
    engine: Engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return SQLRepository(session=Session())

def parse_db_model(db_model: VideoTimestampsDatasetDbModel) -> VideoTimestampsDataset:
    timestamps: list[Timestamp] = [Timestamp(**timestamp) for timestamp in db_model.timestamps['timestamps']]
    return VideoTimestampsDataset(video_id=db_model.video_id, description=db_model.description, timestamps=timestamps)


def poll_database(video_id: str, repository: BaseRepository) -> VideoTimestampsDataset:
    sleep_time: int = 1
    while True:
        if sleep_time > 5:
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="We are having an issue. Try again in 1 minute.")
        try:
            result: VideoTimestampsDatasetDbModel = repository.get(video_id=video_id)
            break
        except NoResultFound:
            time.sleep(0.5)
            sleep_time += 1
    return parse_db_model(db_model=result)


def get_video_timestamps(video_url: VideoUrl, repository: BaseRepository = get_repository()) -> VideoTimestampsDataset:
    video_id: str = parse_video_id(url=video_url)
    try:
        result: VideoTimestampsDatasetDbModel = repository.get(video_id=video_id)
        return parse_db_model(db_model=result)
    except NoResultFound:
        write_videos_to_redis_queue(video_urls=VideoUrls(urls=[video_url]))
    return poll_database(video_id=video_id, repository=repository)
