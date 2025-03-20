import json
import os

import redis
from pydantic import BaseModel
from tubectrl import YouTube
from tubectrl.models import Video
from abc import ABC, abstractmethod
import itertools

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Text, String, create_engine, Engine, select
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.exc import NoResultFound


class BaseConfig:
    DEBUG: bool = True
    REDIS_HOST: str = os.environ.get('REDIS_HOST', "localhost")
    REDIS_PORT: int = os.environ.get('REDIS_PORT', 6379)
    REDIS_DB: int = os.environ.get('REDIS_DB', 0)
    REDIS_VIDEOS_QUEUE: str = os.environ.get('REDIS_VIDEOS_QUEUE', "videos")
    REDIS_TIMESTAMPS_QUEUE: str = os.environ.get('REDIS_TIMESTAMPS_QUEUE', "timestamps")

    POSTGRES_USER = os.environ.get('POSTGRES_USER', "lyle")
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', "lyle")
    POSTGRES_DB = os.environ.get('POSTGRES_DB', "lyle")
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', "localhost")
    # DATABASE_URL = f"sqlite:///{DATABASE_FILE_NAME}"
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    YOUTUBE_CREDENTIALS_PATH: str = os.environ.get('YOUTUBE_CREDENTIALS_PATH', "")

    DATA_DIR: str = os.environ.get('DATA_DIR', ".")
    CLIENT_SECRET_FILE: str = os.environ.get('CLIENT_SECRET_FILE', "")


class VideoDescription(BaseModel):
    video_id: str
    description: str


class BaseRepository(ABC):
    @abstractmethod
    def save(self, video_description: VideoDescription) -> None:
        pass

    @abstractmethod
    def video_in_repository(self, video_id: str) -> bool:
        pass

class FileRepository(BaseRepository):
    def __init__(self, data_dir: str = BaseConfig.DATA_DIR):
        super().__init__()
        self._data_dir: str = data_dir
        self._raw_dir: str = os.path.join(self._data_dir, "raw")

    def save(self, video_description: VideoDescription) -> None:
        raw_file: str = os.path.join(self._raw_dir, f"{video_description.video_id}.txt")
        with open(raw_file, "w") as f:
            f.write(video_description.description)

    def video_in_repository(self, video_id) -> bool:
        return super().video_in_repository(video_id)


Base = declarative_base()

class VideoTimestampsDataset(BaseModel):
    video_id: str
    description: str = ''
    timestamps: dict = {}

class VideoTimestampsDatasetDbModel(Base):
    __tablename__ = "video_timestamps_dataset"

    video_id = Column(String, primary_key=True)
    description = Column(Text, nullable=True)
    timestamps = Column(JSON, nullable=True)

class SQLRepository(BaseRepository):
    def __init__(self, session):
        super().__init__()
        self._session = session

    def save(self, video_timestamps: VideoTimestampsDataset) -> None:
        dataset: VideoTimestampsDatasetDbModel = VideoTimestampsDatasetDbModel(**video_timestamps.model_dump())
        self._session.add(dataset)
        self._session.commit()

    def video_in_repository(self, video_id: str) -> bool:
        statement = select(VideoTimestampsDatasetDbModel).where(VideoTimestampsDatasetDbModel.video_id == video_id)
        try:
            self._session.scalars(statement).one()
        except NoResultFound:
            return False
        return True


class RedisQueueService:
    def __init__(self, repository: BaseRepository,
                 client_secret_file: str = BaseConfig.CLIENT_SECRET_FILE, 
                 redis_host: str = BaseConfig.REDIS_HOST, 
                 redis_port: int = BaseConfig.REDIS_PORT, 
                 redis_db: int = BaseConfig.REDIS_DB, 
                 redis_queue: str = BaseConfig.REDIS_VIDEOS_QUEUE):
        self.youtube = self._get_youtube(client_secret_file=client_secret_file)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.redis_queue = redis_queue
        self.repository = repository

    def _get_youtube(self, client_secret_file: str = None, credentials_path: str = BaseConfig.YOUTUBE_CREDENTIALS_PATH) -> YouTube:
        youtube: YouTube = None
        if credentials_path:
            print('youtube from credentails')
            youtube = YouTube()
            youtube.authenticate_from_credentials(credentials_path=credentials_path)
        else:
            print('youtube from path')
            youtube = YouTube(client_secret_file=client_secret_file)
            youtube.authenticate(client_secret_file)
        return youtube

    def _filter_video_ids(self, video_ids: list[str]) -> list[str]:
        video_ids: list[str] = list(itertools.filterfalse(self.repository.video_in_repository, video_ids))
        return video_ids
    
    def _find_videos(self, video_ids: list[str]) -> list[Video]:
        return self.youtube.find_videos_by_ids(video_ids=video_ids)
    
    def _get_video_description(self, data: tuple[str, Video]) -> str:
        video_id, video = data
        description: str = video.snippet.description
        return VideoDescription(video_id=video_id, description=description)
    
    def _save_video_description(self, video_description: VideoDescription) -> None:
        self.repository.save(video_description)

    def _enqueue_videos(self, video_ids: list[str]):
        try:
            r = redis.Redis(host=BaseConfig.REDIS_HOST, port=BaseConfig.REDIS_PORT, db=BaseConfig.REDIS_DB)
            video_ids: dict[str, list[str]] = {"video_ids": video_ids}
            r.lpush(BaseConfig.REDIS_TIMESTAMPS_QUEUE, json.dumps(video_ids))
        except ConnectionError as e:
            print(e)

    def run(self):
        try:
            while True:
                # Blocking pop to wait for new messages
                metadata = self.redis.brpop(self.redis_queue)
                video_ids: dict[str, list[str]] = json.loads(metadata[1].decode("utf-8"))
                video_ids: list[str] = video_ids["video_ids"]
                video_ids = self._filter_video_ids(video_ids)
                print(video_ids)
                if video_ids:
                    videos: list[Video] = self._find_videos(video_ids=video_ids)
                    video_descriptions: list[VideoDescription] = list(
                        map(self._get_video_description, zip(video_ids, videos))
                    )
                    for video_description in video_descriptions:
                        self._save_video_description(video_description)
                    self._enqueue_videos(video_ids)
        except KeyboardInterrupt:
            print("Shutting down")


def create_sql_repository() -> SQLRepository:
    connect_args = {"check_same_thread": False}
    # engine: Engine = create_engine(BaseConfig.DATABASE_URL, connect_args=connect_args)
    engine: Engine = create_engine(BaseConfig.DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return SQLRepository(session=Session())

if __name__ == "__main__":
    # repository = FileRepository()
    repository = create_sql_repository()
    service = RedisQueueService(repository=repository)
    service.run()
