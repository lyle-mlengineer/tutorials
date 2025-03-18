import json
import os
import re

import redis
from pydantic import BaseModel
from tubectrl import YouTube
from tubectrl.models import Video

REDIS_HOST: str = "localhost"
REDIS_PORT: int = 6379
REDIS_DB: int = 0
REDIS_TIMESTAMPS_QUEUE: str = "timestamps"

DATADIR: str = "./dataset"
PROCESSED_DIR: str = os.path.join(DATADIR, "processed")
RAW_DIR: str = os.path.join(DATADIR, "raw")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


class VideoDescription(BaseModel):
    video_id: str
    description: str


class Timestamp(BaseModel):
    title: str
    timestamp: str


class VideoTimestamps(BaseModel):
    video_id: str
    timestamps: list[Timestamp]


class VideoTimestampsDataset(VideoTimestamps):
    description: str


def get_video_description_from_file(video_id: str) -> VideoDescription:
    raw_file: str = os.path.join(RAW_DIR, f"{video_id}.txt")
    with open(raw_file, "r") as f:
        description: str = f.read()
    return VideoDescription(video_id=video_id, description=description)


def post_process_title(title: str) -> str:
    title: str = re.sub(r"-", "", title)
    title = title.strip()
    return title


def get_timestamp_and_title(match_group: tuple) -> Timestamp:
    title: str = match_group[2]
    title = post_process_title(title=title)
    timestamp: str = match_group[0] + match_group[1]
    return Timestamp(title=title, timestamp=timestamp)


def save_video_timestamps(video_timestamps: VideoTimestampsDataset) -> None:
    processed_file: str = os.path.join(
        PROCESSED_DIR, f"{video_timestamps.video_id}.json"
    )
    with open(processed_file, "w") as f:
        json.dump(video_timestamps.model_dump(), f, indent=4)


def extract_timestamps(video_id: str) -> None:
    video_description: VideoDescription = get_video_description_from_file(
        video_id=video_id
    )
    text = video_description.description
    timestamps: list[Timestamp] = []
    pattern = r"(\d+:)+(\d+)(.+)"
    pattern_compiled = re.compile(pattern)
    matches = re.finditer(pattern_compiled, text)
    for match in matches:
        timestamp: Timestamp = get_timestamp_and_title(match.groups())
        timestamps.append(timestamp)
    save_video_timestamps(
        video_timestamps=VideoTimestampsDataset(
            timestamps=timestamps, video_id=video_id, description=text
        )
    )


while True:
    # Blocking pop to wait for new messages
    metadata = r.brpop(REDIS_TIMESTAMPS_QUEUE)
    video_ids: dict[str, list[str]] = json.loads(metadata[1].decode("utf-8"))
    video_ids: list[str] = video_ids["video_ids"]
    for video_id in video_ids:
        extract_timestamps(video_id=video_id)
