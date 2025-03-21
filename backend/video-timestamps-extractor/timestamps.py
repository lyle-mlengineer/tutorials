import json
import os
import re
from abc import ABC, abstractmethod

import redis
from pydantic import BaseModel
from sqlalchemy import Column, Engine, String, Text, create_engine, select
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import declarative_base, sessionmaker


class BaseConfig:
    DEBUG: bool = True
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.environ.get("REDIS_PORT", 6379)
    REDIS_DB: int = os.environ.get("REDIS_DB", 0)
    REDIS_VIDEOS_QUEUE: str = os.environ.get("REDIS_VIDEOS_QUEUE", "videos")
    REDIS_TIMESTAMPS_QUEUE: str = os.environ.get("REDIS_TIMESTAMPS_QUEUE", "timestamps")

    POSTGRES_USER = os.environ.get("POSTGRES_USER", "lyle")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "lyle")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "lyle")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    # DATABASE_URL = f"sqlite:///{DATABASE_FILE_NAME}"
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    YOUTUBE_CREDENTIALS_PATH: str = os.environ.get("YOUTUBE_CREDENTIALS_PATH", "")

    DATA_DIR: str = os.environ.get("DATA_DIR", ".")
    CLIENT_SECRET_FILE: str = os.environ.get("CLIENT_SECRET_FILE", "")


class VideoDescription(BaseModel):
    video_id: str
    description: str


class Timestamp(BaseModel):
    title: str
    timestamp: str


class VideoTimestamps(BaseModel):
    video_id: str
    timestamps: list[Timestamp]


class VideoTimestampsDataset(VideoTimestamps):
    description: str


class BaseRepository(ABC):
    @abstractmethod
    def save(self, video_timestamps: VideoTimestampsDataset) -> None:
        pass

    @abstractmethod
    def get(self, video_id: str) -> VideoDescription:
        pass


class FileRepository(BaseRepository):
    def __init__(self, data_dir: str = BaseConfig.DATA_DIR):
        super().__init__()
        self._data_dir: str = data_dir
        self._raw_dir: str = os.path.join(self._data_dir, "raw")
        self._processed_dir: str = os.path.join(self._data_dir, "processed")

    def save(self, video_timestamps: VideoTimestampsDataset) -> None:
        processed_file: str = os.path.join(
            self._processed_dir, f"{video_timestamps.video_id}.json"
        )
        with open(processed_file, "w") as f:
            json.dump(video_timestamps.model_dump(), f, indent=4)

    def get(self, video_id: str) -> VideoDescription:
        raw_file: str = os.path.join(self._raw_dir, f"{video_id}.txt")
        with open(raw_file, "r") as f:
            description: str = f.read()
        return VideoDescription(video_id=video_id, description=description)


Base = declarative_base()


class VideoTimestampsDataset(BaseModel):
    video_id: str
    description: str = ""
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
        statement = select(VideoTimestampsDatasetDbModel).where(
            VideoTimestampsDatasetDbModel.video_id == video_id
        )
        return self._session.scalars(statement).one()

    def save(self, video_timestamps: VideoTimestampsDataset) -> None:
        video_model: VideoTimestampsDatasetDbModel = self.get(
            video_id=video_timestamps.video_id
        )
        video_model.timestamps = {
            "timestamps": [
                timestamp.model_dump() for timestamp in video_timestamps.timestamps
            ]
        }
        self._session.add(video_model)
        self._session.commit()


class RedisQueueService:
    def __init__(
        self,
        repository: BaseRepository,
        redis_host: str = BaseConfig.REDIS_HOST,
        redis_port: int = BaseConfig.REDIS_PORT,
        redis_db: int = BaseConfig.REDIS_DB,
        timestamps_queue: str = BaseConfig.REDIS_TIMESTAMPS_QUEUE,
    ):
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.timestamps_queue = timestamps_queue
        self.repository = repository

    def _get_video_description_from_file(self, video_id: str) -> VideoDescription:
        return self.repository.get(video_id)

    @staticmethod
    def post_process_title(title: str) -> str:
        title: str = re.sub(r"-", "", title)
        title = title.strip()
        return title

    @staticmethod
    def get_timestamp_and_title(match_group: tuple) -> Timestamp:
        title: str = match_group[2]
        title = RedisQueueService.post_process_title(title=title)
        timestamp: str = match_group[0] + match_group[1]
        return Timestamp(title=title, timestamp=timestamp)

    def _save_video_timestamps(self, video_timestamps: VideoTimestampsDataset) -> None:
        self.repository.save(video_timestamps)

    def _extract_timestamps(self, video_id: str) -> None:
        video_description: VideoDescription = self._get_video_description_from_file(
            video_id=video_id
        )
        text = video_description.description
        timestamps: list[Timestamp] = []
        pattern = r"(\d+:)+(\d+)(.+)"
        pattern_compiled = re.compile(pattern)
        matches = re.finditer(pattern_compiled, text)
        for match in matches:
            timestamp: Timestamp = RedisQueueService.get_timestamp_and_title(
                match.groups()
            )
            timestamps.append(timestamp)
        self._save_video_timestamps(
            video_timestamps=VideoTimestampsDataset(
                timestamps=timestamps, video_id=video_id, description=text
            )
        )

    def run(self):
        try:
            while True:
                # Blocking pop to wait for new messages
                metadata = self.redis.brpop(self.timestamps_queue)
                video_ids: dict[str, list[str]] = json.loads(
                    metadata[1].decode("utf-8")
                )
                video_ids: list[str] = video_ids["video_ids"]
                print(video_ids)
                for video_id in video_ids:
                    self._extract_timestamps(video_id=video_id)
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
    redis_queue_service = RedisQueueService(repository=repository)
    redis_queue_service.run()
