def parse_video_id(url: str) -> str:
    try:
        video_id: str = url.split("=")[1].split("&")[0]
    except IndexError:
        video_id: str = url
    return video_id
