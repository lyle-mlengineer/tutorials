import itertools
import json
import os
from abc import ABC, abstractmethod
from typing import Iterator

import redis
from pydantic import BaseModel
from sqlalchemy import Column, Engine, String, Text, create_engine, select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import declarative_base, sessionmaker
from tubectrl import YouTube
from tubectrl.models import PlaylistItem


class BaseConfig:
    DEBUG: bool = True
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.environ.get("REDIS_PORT", 6379)
    REDIS_DB: int = os.environ.get("REDIS_DB", 0)
    REDIS_PLAYLIST_QUEUE: str = os.environ.get("REDIS_PLAYLIST_QUEUE", "playlists")
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
    CLIENT_SECRET_FILE: str = os.environ.get(
        "CLIENT_SECRET_FILE", "/home/lyle/Downloads/youtube_secrets.json"
    )


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
    description: str = ""
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
        dataset: VideoTimestampsDatasetDbModel = VideoTimestampsDatasetDbModel(
            **video_timestamps.model_dump()
        )
        self._session.add(dataset)
        self._session.commit()

    def video_in_repository(self, video_id: str) -> bool:
        statement = select(VideoTimestampsDatasetDbModel).where(
            VideoTimestampsDatasetDbModel.video_id == video_id
        )
        try:
            self._session.scalars(statement).one()
        except NoResultFound:
            return False
        return True


class RedisQueueService:
    def __init__(
        self,
        repository: BaseRepository,
        client_secret_file: str = BaseConfig.CLIENT_SECRET_FILE,
        redis_host: str = BaseConfig.REDIS_HOST,
        redis_port: int = BaseConfig.REDIS_PORT,
        redis_db: int = BaseConfig.REDIS_DB,
        redis_queue: str = BaseConfig.REDIS_PLAYLIST_QUEUE,
    ):
        self.youtube = self._get_youtube(client_secret_file=client_secret_file)
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
        self.redis_queue = redis_queue
        self.repository = repository

    def _get_youtube(
        self,
        client_secret_file: str = None,
        credentials_path: str = BaseConfig.YOUTUBE_CREDENTIALS_PATH,
    ) -> YouTube:
        youtube: YouTube = None
        if credentials_path:
            print("youtube from credentails")
            youtube = YouTube()
            youtube.authenticate_from_credentials(credentials_path=credentials_path)
        else:
            print("youtube from path")
            youtube = YouTube(client_secret_file=client_secret_file)
            youtube.authenticate(client_secret_file)
        return youtube

    def _process_playlist(self, playlist_id: str) -> None:
        try:
            iterator: Iterator = self.youtube.get_playlist_items_iterator(
                playlist_id=playlist_id
            )
            for playlist_items in iterator:
                video_descriptions: list[VideoDescription] = list(
                    map(self._get_video_description, playlist_items)
                )
                for video_description in video_descriptions:
                    if not self.repository.video_in_repository(
                        video_description.video_id
                    ):
                        self._save_video_description(video_description)
                self._enqueue_videos(
                    [
                        video_description.video_id
                        for video_description in video_descriptions
                    ]
                )
        except:
            self.redis.hset(name="quota", key="quota_exceeded", value="true")

    def _get_video_description(self, playlist_item: PlaylistItem) -> VideoDescription:
        description: str = playlist_item.snippet.description
        video_id: str = playlist_item.snippet.resourceId.videoId
        return VideoDescription(video_id=video_id, description=description)

    def _save_video_description(self, video_description: VideoDescription) -> None:
        self.repository.save(video_description)

    def _enqueue_videos(self, video_ids: list[str]):
        try:
            r = redis.Redis(
                host=BaseConfig.REDIS_HOST,
                port=BaseConfig.REDIS_PORT,
                db=BaseConfig.REDIS_DB,
            )
            video_ids: dict[str, list[str]] = {"video_ids": video_ids}
            r.lpush(BaseConfig.REDIS_TIMESTAMPS_QUEUE, json.dumps(video_ids))
        except ConnectionError as e:
            print(e)

    def run(self):
        self.redis.hset(name="quota", key="quota_exceeded", value="false")
        try:
            while True:
                # Blocking pop to wait for new messages
                metadata = self.redis.brpop(self.redis_queue)
                playlist_id: dict[str, str] = json.loads(metadata[1].decode("utf-8"))
                print(playlist_id)
                playlist_id: str = playlist_id["playlist_id"]
                print(playlist_id)
                self._process_playlist(playlist_id=playlist_id)
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
