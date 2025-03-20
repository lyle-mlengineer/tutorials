import json

import redis
from redis.exceptions import ConnectionError

from .models import VideoUrl, VideoUrls
from ..config.config import BaseConfig

REDIS_HOST = BaseConfig.REDIS_HOST
REDIS_PORT = BaseConfig.REDIS_PORT
REDIS_DB = BaseConfig.REDIS_DB
REDIS_VIDEOS_QUEUE = BaseConfig.REDIS_VIDEOS_QUEUE


def parse_video_id(url: VideoUrl) -> str:
    video_id: str
    try:
        video_id: str = url.url.split("=")[1].split("&")[0]
    except IndexError:
        video_id = url
    return video_id


def write_videos_to_redis_queue(video_urls: VideoUrls) -> None:
    video_ids: list[str] = list(map(parse_video_id, video_urls.urls))
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        video_ids: dict[str, list[str]] = {"video_ids": video_ids}
        r.lpush(REDIS_VIDEOS_QUEUE, json.dumps(video_ids))
    except ConnectionError as e:
        print(e)
