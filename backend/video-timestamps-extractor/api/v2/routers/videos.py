from fastapi import APIRouter, status

from .database import get_video_timestamps
from .models import VideoTimestampsDataset, VideoUrl, VideoUrls
from .utils import write_videos_to_redis_queue

video_router = APIRouter(prefix="/videos", tags=["Video"])


@video_router.post("/queue", status_code=status.HTTP_202_ACCEPTED)
async def queue_videos_for_extraction(video_urls: VideoUrls) -> None:
    write_videos_to_redis_queue(video_urls=video_urls)


@video_router.post("/get", response_model=VideoTimestampsDataset)
def get_timestamps(video_url: VideoUrl):
    return get_video_timestamps(video_url=video_url)
