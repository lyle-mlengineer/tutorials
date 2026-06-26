from fastapi import Request
from db import Base, engine
from services import ImageService
from fastapi import Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas import NextImageResponse, ImageRead
from typing import Annotated

async def get_image_tags() -> list[str]:
    return ["tag1", "tag2", "tag3"]

def create_all():
    Base.metadata.create_all(bind=engine)

def get_image_service(db: Annotated[Session, Depends(get_db)]):
    return ImageService(db)

async def get_next_image(request: Request, image_service: ImageService = Depends(get_image_service)):
    image: ImageRead = await image_service.get_next_image()
    image_path: str = f"{image.id}.{image.extension}"
    image_url: str = request.url_for("data", path=image_path).__str__()
    return image.id, image_url