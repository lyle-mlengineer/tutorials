import json
import os

import redis
from pydantic import BaseModel
from tubectrl import YouTube
from tubectrl.models import Video

REDIS_HOST: str = "localhost"
REDIS_PORT: int = 6379
REDIS_DB: int = 0
REDIS_VIDEOS_QUEUE: str = "videos"
REDIS_TIMESTAMPS_QUEUE: str = "timestamps"

DATADIR: str = "./dataset"
RAW_DIR: str = os.path.join(DATADIR, "raw")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
client_secret_file: str = "/home/lyle/Downloads/youtube.json"
youtube = YouTube()
youtube.authenticate(client_secret_file)


class VideoDescription(BaseModel):
    video_id: str
    description: str


def get_video_description(data: tuple[str, Video]) -> str:
    video_id, video = data
    description: str = video.snippet.description
    return VideoDescription(video_id=video_id, description=description)


def load_videos():
    with open("videos.json", "r") as f:
        videos = json.load(f)
    videos = list(map(lambda video: Video(**video), videos))
    return videos


def filter_video_ids(video_ids: list[str]) -> list[str]:
    return video_ids


def save_video_description(video_description: VideoDescription) -> None:
    raw_file: str = os.path.join(RAW_DIR, f"{video_description.video_id}.txt")
    with open(raw_file, "w") as f:
        f.write(video_description.description)


def write_ids(video_ids: list[str]):
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        video_ids: dict[str, list[str]] = {"video_ids": video_ids}
        r.lpush(REDIS_TIMESTAMPS_QUEUE, json.dumps(video_ids))
    except ConnectionError as e:
        print(e)


while True:
    # Blocking pop to wait for new messages
    metadata = r.brpop(REDIS_VIDEOS_QUEUE)
    video_ids: dict[str, list[str]] = json.loads(metadata[1].decode("utf-8"))
    video_ids: list[str] = video_ids["video_ids"]
    video_ids = list(filter(filter_video_ids, video_ids))
    # videos: list[Video] = youtube.find_videos_by_ids(video_ids=video_ids)
    videos: list[Video] = load_videos()
    video_descriptions: list[VideoDescription] = list(
        map(get_video_description, zip(video_ids, videos))
    )
    for video_description in video_descriptions:
        save_video_description(video_description)
    write_ids(video_ids)
