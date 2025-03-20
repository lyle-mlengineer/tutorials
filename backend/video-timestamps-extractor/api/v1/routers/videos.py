from fastapi import APIRouter

from .models import VideoTimestamps, VideoUrls
from .utils import process_videos

video_router = APIRouter(prefix="/videos", tags=["Video"])


@video_router.post("/")
async def get_video_details(video_urls: VideoUrls) -> list[VideoTimestamps]:
    return process_videos(video_urls=video_urls)
