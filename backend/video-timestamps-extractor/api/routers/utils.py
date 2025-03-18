import json
import os
import re

from tubectrl.models import Video

from .extensions import youtube
from .models import (Timestamp, VideoDescription, VideoTimestamps,
                     VideoTimestampsDataset, VideoUrl, VideoUrls)


def get_video_description(video: Video) -> str:
    return video.snippet.description


def get_youtube_video(video_id: str) -> VideoDescription:
    video: Video = youtube.find_video_by_id(video_id=video_id)
    description: str = get_video_description(video=video)
    vid_desc: VideoDescription = VideoDescription(
        video_id=video_id, description=description
    )
    return vid_desc


def save_video_description(video_description: VideoDescription) -> None:
    DATADIR: str = "./data"
    RAW_DIR: str = os.path.join(DATADIR, "raw")
    raw_file: str = os.path.join(RAW_DIR, f"{video_description.video_id}.txt")
    with open(raw_file, "w") as f:
        f.write(video_description.description)


def get_video_description_from_file(video_id: str) -> VideoDescription:
    DATADIR: str = "./data"
    RAW_DIR: str = os.path.join(DATADIR, "raw")
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


def get_video_details(video_id: str) -> VideoDescription:
    video_description: VideoDescription = None
    if os.path.exists(f"./data/{video_id}.txt"):
        video_description = get_video_description_from_file(video_id=video_id)
    else:
        video_description: VideoDescription = get_youtube_video(video_id=video_id)
        save_video_description(video_description=video_description)
    return video_description


def save_video_timestamps(video_timestamps: VideoTimestampsDataset) -> None:
    DATADIR: str = "./data"
    PROCESSED_DIR: str = os.path.join(DATADIR, "processed")
    processed_file: str = os.path.join(
        PROCESSED_DIR, f"{video_timestamps.video_id}.json"
    )
    with open(processed_file, "w") as f:
        json.dump(video_timestamps.model_dump(), f, indent=4)


def parse_video_id(url: str) -> str:
    try:
        video_id: str = url.split("=")[1].split("&")[0]
    except:
        video_id: str = url
    return video_id


def extract_timestamps(video_url: VideoUrl) -> VideoTimestamps:
    video_id: str = parse_video_id(url=video_url.video_url)
    DATADIR: str = "./data"
    PROCESSED_DIR: str = os.path.join(DATADIR, "processed")
    processed_file: str = os.path.join(PROCESSED_DIR, f"{video_id}.json")
    if os.path.exists(processed_file):
        with open(processed_file, "r") as f:
            video_timestamps: VideoTimestamps = VideoTimestamps(**json.load(f))
        return video_timestamps
    video_details: VideoDescription = get_video_details(video_id=video_id)
    text = video_details.description
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
    return VideoTimestamps(timestamps=timestamps, video_id=video_id)


def process_videos(video_urls: VideoUrls) -> list[VideoTimestamps]:
    all_video_timestamps: list[VideoTimestamps] = []
    for video_url in video_urls.urls:
        try:
            video_timestamps = extract_timestamps(video_url=video_url)
        except Exception as e:
            print(e)
            continue
        all_video_timestamps.append(video_timestamps)
    return all_video_timestamps
