from fastapi import Request
from db import Base, engine
from services import ImageService, TagService, ImageLabellingService
from fastapi import Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas import NextImageResponse, ImageRead
from typing import Annotated

async def get_image_tags(tag_service: TagService) -> list[str]:
    return [tag.name for tag in tag_service.get_tags()]

def create_all():
    Base.metadata.create_all(bind=engine)

def get_image_service(db: Annotated[Session, Depends(get_db)]):
    return ImageService(db)

async def get_next_image(request: Request, image_service: ImageService = Depends(get_image_service)):
    image: ImageRead = await image_service.get_next_image()
    image_path: str = f"{image.id}.{image.extension}"
    image_url: str = request.url_for("data", path=image_path).__str__()
    return image.id, image_url

def get_tag_service(db: Annotated[Session, Depends(get_db)]):
    return TagService(db)

def get_image_labelling_service(db: Annotated[Session, Depends(get_db)]):
    return ImageLabellingService(db, get_image_service(db), get_tag_service(db))