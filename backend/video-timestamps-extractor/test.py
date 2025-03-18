from tubectrl import YouTube


def parse_video_id(url: str) -> str:
    video_id: str = url.split("=")[1].split("&")[0]
    return video_id


print(parse_video_id("https://www.youtube.com/watch?v=5GxQ1rLTwaU&t=1617s"))
