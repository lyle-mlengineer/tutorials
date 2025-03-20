from pydantic import BaseModel


class VideoUrl(BaseModel):
    url: str


class VideoUrls(BaseModel):
    urls: list[VideoUrl]


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
