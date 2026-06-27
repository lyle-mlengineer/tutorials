from services import ImageGenerationService
from db import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Annotated

def get_image_generation_service(db: Annotated[Session, Depends(get_db)]):
    return ImageGenerationService(db)