from fastapi import APIRouter, Request
from schemas import VideoExtractionRequest, PlaylistExtractionRequest, ChannelExtractionRequest


router = APIRouter(
    tags=["Extraction Operations"],
)

@router.post("/extraction/video")
async def extract_video_timestamps(extraction_request: VideoExtractionRequest):
    return extraction_request

@router.post("/extraction/playlist")
async def extract_playlist_timestamps(extraction_request: PlaylistExtractionRequest):
    return extraction_request

@router.post("/extraction/channel")
async def extract_channel_timestamps(extraction_request: ChannelExtractionRequest):
    return extraction_request