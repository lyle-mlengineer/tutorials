from __future__ import annotations
from pydantic import BaseModel
from db import Video, Dataset, VideoExtraction, Playlist
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
    
class VideoExtractionCreate(BaseModel):
    video_id: str
    dataset_id: str
    id: str
    timestamps: dict
    created_at: datetime

    @classmethod
    def from_video_extraction(cls, video_extraction: VideoExtraction) -> VideoExrtractionCreate:
        return VideoExrtractionCreate(
            id=video_extraction.id,
            video_id=video_extraction.video_id,
            dataset_id=video_extraction.dataset_id,
            timestamps=video_extraction.timestamps,
            created_at=video_extraction.created_at,
        )
    
class VideoExtractionRead(BaseModel):
    id: str
    video_id: str
    dataset_id: str
    timestamps: dict
    created_at: datetime

    @classmethod
    def from_video_extraction(cls, video_extraction: VideoExtraction) -> VideoExtractionRead:
        return VideoExtractionRead(
            id=video_extraction.id,
            video_id=video_extraction.video_id,
            dataset_id=video_extraction.dataset_id,
            timestamps=video_extraction.timestamps,
            created_at=video_extraction.created_at,
        )

class VideoCreate(BaseModel):
    id: str
    title: str
    description: str

    @classmethod
    def from_video(cls, video: Video) -> VideoCreate:
        return VideoCreate(
            id=video.id,
            title=video.title,
            description=video.description
        )
    
class VideoRead(BaseModel):
    id: str
    title: str
    description: str

    @classmethod
    def from_video(cls, video: Video) -> VideoRead:
        return VideoRead(
            id=video.id,
            title=video.title,
            description=video.description
        )
    
class PlaylistCreate(BaseModel):
    id: str
    title: str
    description: str

    @classmethod
    def from_playlist(cls, playlist: Playlist) -> PlaylistCreate:
        return PlaylistCreate(
            id=playlist.id,
            title=playlist.title,
            description=playlist.description
        )
    
class PlaylistRead(BaseModel):
    id: str
    title: str
    description: str

    @classmethod
    def from_playlist(cls, playlist: Playlist) -> PlaylistRead:
        return PlaylistRead(
            id=playlist.id,
            title=playlist.title,
            description=playlist.description
        )
    
class Timestamp(BaseModel):
    timestamp: str
    title: str

class Timestamps(BaseModel):
    timestamps: list[Timestamp]


class ExtractionResponse(BaseModel):
    video_id: str
    title: str
    timestamps: list[Timestamp]
    thumbnail_url: str