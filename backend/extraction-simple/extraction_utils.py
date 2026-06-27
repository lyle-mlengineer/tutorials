from tubectrl import YouTube
from tubectrl.models import Video
from schemas import FindVideoResponse

def parse_video_id(url: str) -> str:
    video_id: str
    try:
        video_id: str = url.split("=")[1].split("&")[0]
    except IndexError:
        video_id = url
    return video_id

def find_video(video_id: str, youtube: YouTube) -> Video:
    video: Video = youtube.find_video_by_id(video_id=video_id)
    return video

def parse_video_thumbnails(video: Video) -> str:
    for resolution in ["default", "high", "medium", "standard"]:
        for thumbnail in video.snippet.thumbnails:
            if thumbnail.resolution == resolution:
                thumbnail_url: str = thumbnail.url
                print(f"Thumbnail URL for resolution {resolution}: {thumbnail_url}")
                return thumbnail_url


async def extract_video_timestamps(video_url: str):
    video_id: str = parse_video_id(video_url)
    print(video_id)

async def find_video_parse_video(video_url: str, youtube: YouTube) -> FindVideoResponse:
    video_id: str = parse_video_id(video_url)
    video: Video = find_video(video_id, youtube)
    thumbnail: str = parse_video_thumbnails(video)
    return FindVideoResponse(thumbnail_url=thumbnail)