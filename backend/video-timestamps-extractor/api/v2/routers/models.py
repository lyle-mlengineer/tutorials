from pydantic import BaseModel


class Url(BaseModel):
    url: str


class VideoUrl(Url):
    pass


class PlaylistUrl(Url):
    pass


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
