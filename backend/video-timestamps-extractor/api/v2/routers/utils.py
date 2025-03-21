import json

import redis
from fastapi import HTTPException, status
from redis.exceptions import ConnectionError

from ..config.config import BaseConfig
from .models import PlaylistUrl, VideoUrl, VideoUrls

REDIS_HOST = BaseConfig.REDIS_HOST
REDIS_PORT = BaseConfig.REDIS_PORT
REDIS_DB = BaseConfig.REDIS_DB
REDIS_VIDEOS_QUEUE = BaseConfig.REDIS_VIDEOS_QUEUE
REDIS_PLAYLIST_QUEUE = BaseConfig.REDIS_PLAYLIST_QUEUE


def parse_video_id(url: VideoUrl) -> str:
    video_id: str
    try:
        video_id: str = url.url.split("=")[1].split("&")[0]
    except IndexError:
        video_id = url
    return video_id


def write_videos_to_redis_queue(video_urls: VideoUrls) -> None:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    quota_exceeded: str = r.hget(name="quota", key="quota_exceeded").decode("utf-8")
    if quota_exceeded == "true":
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You have exhausted your daily youtube quota",
        )
    print(quota_exceeded)
    video_ids: list[str] = list(map(parse_video_id, video_urls.urls))
    try:
        video_ids: dict[str, list[str]] = {"video_ids": video_ids}
        r.lpush(REDIS_VIDEOS_QUEUE, json.dumps(video_ids))
    except ConnectionError as e:
        print(e)


def write_playlist_to_redis_queue(playlist_url: PlaylistUrl) -> None:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    quota_exceeded: str = r.hget(name="quota", key="quota_exceeded").decode("utf-8")
    if quota_exceeded == "true":
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="You have exhausted your daily youtube quota",
        )
    print(quota_exceeded)
    try:
        r.lpush(REDIS_PLAYLIST_QUEUE, json.dumps({"playlist_id": playlist_url.url}))
    except ConnectionError as e:
        print(e)
