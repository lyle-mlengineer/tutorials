from pydantic import BaseModel


class VideoExtractionRequest(BaseModel):
    url: str

class PlaylistExtractionRequest(BaseModel):
    url: str

class ChannelExtractionRequest(BaseModel):
    id: str

class FindVideoResponse(BaseModel):
    thumbnail_url: str