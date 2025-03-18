import json

import redis
from pydantic import BaseModel
from redis.exceptions import ConnectionError
from tubectrl import YouTube
from tubectrl.models import Video

from utils import parse_video_id

client_secret_file: str = "/home/lyle/Downloads/youtube.json"
youtube = YouTube()
# youtube.authenticate(client_secret_file)

urls: list[str] = [
    "https://www.youtube.com/watch?v=YDn2NJXJyQc",
    "https://www.youtube.com/watch?v=5oh5A1s7x8I",
    "https://www.youtube.com/watch?v=oBCGqylIbU8",
    "https://www.youtube.com/watch?v=WqBILPra47g&pp=ygUabGF0ZXN0IG1vdmllIHRyYWlsZXJzIDIwMjU%3D",
    "https://www.youtube.com/watch?v=B69-CbvsbvI&pp=ygUabGF0ZXN0IG1vdmllIHRyYWlsZXJzIDIwMjU%3D",
]


def save_videos(videos: list[Video]):
    with open("videos.json", "w") as f:
        videos = list(map(lambda video: video.model_dump(), videos))
        json.dump(videos, f)


def load_videos():
    with open("videos.json", "r") as f:
        videos = json.load(f)
    videos = list(map(lambda video: Video(**video), videos))
    return videos


class VideoDescription(BaseModel):
    video_id: str
    description: str


def get_video_description(data: tuple[str, Video]) -> str:
    video_id, video = data
    description: str = video.snippet.description
    return VideoDescription(video_id=video_id, description=description)


def write_ids(video_ids: list[str]):
    try:
        r = redis.Redis(host="localhost", port=6379, db=0)
        video_ids: dict[str, list[str]] = {"video_ids": video_ids}
        r.lpush("videos", json.dumps(video_ids))
    except ConnectionError as e:
        print(e)


video_ids: list[str] = list(map(parse_video_id, urls))
# videos: list[Video] = youtube.find_videos_by_ids(video_ids=video_ids)
# save_videos(videos)
write_ids(video_ids)
# videos: list[Video] = load_videos()
# video_descriptions: list[VideoDescription] = list(map(get_video_description, zip(video_ids,videos)))
# print(video_descriptions[0])
