from fastapi import APIRouter, Request, Depends
from schemas import VideoExtractionRequest, PlaylistExtractionRequest, ChannelExtractionRequest
from utils import get_timestamps_extraction_service
from services import TimestampsExtractionService


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

@router.post("/extraction/find-video")
async def find_video(
    extraction_request: VideoExtractionRequest,
    timestamps_extraction_service: TimestampsExtractionService = Depends(get_timestamps_extraction_service)
    ):
    return await timestamps_extraction_service.find_video(extraction_request.url)