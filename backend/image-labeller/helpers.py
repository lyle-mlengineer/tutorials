from fastapi import Request


async def get_next_image(request: Request):
    image_name: str = "example.jpeg"
    image_url: str = request.url_for("static", path=f"img/{image_name}").__str__()
    return image_name, image_url

async def get_image_tags() -> list[str]:
    return ["tag1", "tag2", "tag3"]