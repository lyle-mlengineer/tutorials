from tubectrl import YouTube
from tubectrl.models import Video
from schemas import FindVideoResponse
from db import Video as VideoInDb
from models import ExtractionResponse, Timestamp, Timestamps, VideoCreate
import re
import os
import json


def parse_video_id(url: str) -> str:
    video_id: str
    try:
        video_id: str = url.split("=")[1].split("&")[0]
    except IndexError:
        video_id = url
    return video_id

def preprocess_video(video_url: str, youtube: YouTube) -> VideoCreate:
    video_id: str = parse_video_id(video_url)
    video: Video = find_video(video_id, youtube)
    title: str = video.snippet.title
    description: str = get_video_description(video=video)
    return VideoCreate(id=video_id, title=title, description=description)

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

def get_video_description(video: Video) -> str:
    description: str = video.snippet.description
    return description

def post_process_title(title: str) -> str:
    title: str = re.sub(r"-", "", title)
    title = title.strip()
    return title


def get_timestamp_and_title(match_group: tuple) -> Timestamp:
    title: str = match_group[2]
    title = post_process_title(title=title)
    timestamp: str = match_group[0] + match_group[1]
    return Timestamp(title=title, timestamp=timestamp)


def extract_timestamps(description: str) -> list[Timestamp]:
    timestamps: list[Timestamp] = []
    pattern = r"(\d+:)+(\d+)(.+)"
    pattern_compiled = re.compile(pattern)
    matches = re.finditer(pattern_compiled, description)
    for match in matches:
        timestamp: Timestamp = get_timestamp_and_title(match.groups())
        timestamps.append(timestamp)
    return timestamps

def save_extraction_response(extraction_response: ExtractionResponse):
    file_name: str = os.path.join("data", f"{extraction_response.video_id}.json")
    with open(file_name, "w") as file:
        json.dump(extraction_response.model_dump(), file, indent=4)


def load_extraction_response(video_id: str) -> ExtractionResponse:
    file_name: str = os.path.join("data", f"{video_id}.json")
    with open(file_name, "r") as file:
        extraction_response: ExtractionResponse = ExtractionResponse(**json.load(file))
    return extraction_response

def format_extraction_response(extraction_response: ExtractionResponse) -> str:
    response: str = ""
    response += "{\n"
    response += '  "videoId": "' + extraction_response.video_id + '",\n'
    response += '  "title": "' + extraction_response.title + '",\n'
    response += '  "timestamps": [\n'
    for timestamp in extraction_response.timestamps:
        response += "    {\n"
        response += '      "title": "' + timestamp.title + '",\n'
        response += '      "timestamp": "' + timestamp.timestamp + '"\n'
        response += "    },\n"
    response += "  ]\n"
    response += "}"
    return response

async def extract_video_timestamps(video_url: str, youtube: YouTube):
    video_id: str = parse_video_id(video_url)
    video: Video = find_video(video_id=video_id, youtube=youtube)
    # print(video)
    description: str = get_video_description(video=video)
    timestamps: list[Timestamps] = extract_timestamps(description=description)
    for resolution in ["default", "high", "medium", "standard"]:
        for thumbnail in video.snippet.thumbnails:
            if thumbnail.resolution == resolution:
                thumbnail_url: str = thumbnail.url
                print(f"Thumbnail URL for resolution {resolution}: {thumbnail_url}")
                break
    extraction_response = ExtractionResponse(
        video_id=video_id,
        title=video.snippet.title,
        timestamps=timestamps,
        thumbnail_url=thumbnail_url,
    )
    save_extraction_response(extraction_response=extraction_response)
    # formatted_response = format_extraction_response(extraction_response)
    return extraction_response

async def find_video_parse_video(video_url: str, youtube: YouTube) -> FindVideoResponse:
    video_id: str = parse_video_id(video_url)
    video: Video = find_video(video_id, youtube)
    thumbnail: str = parse_video_thumbnails(video)
    return FindVideoResponse(thumbnail_url=thumbnail, title=video.snippet.title)