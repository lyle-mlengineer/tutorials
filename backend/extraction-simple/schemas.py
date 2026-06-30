from pydantic import BaseModel


class VideoExtractionRequest(BaseModel):
    url: str
    dataset: str

class PlaylistExtractionRequest(BaseModel):
    url: str
    dataset: str

class ChannelExtractionRequest(BaseModel):
    id: str
    dataset: str

class FindVideoResponse(BaseModel):
    thumbnail_url: str
    title: str

class TimestampsExtractionResponse(BaseModel):
    start: int
    end: int