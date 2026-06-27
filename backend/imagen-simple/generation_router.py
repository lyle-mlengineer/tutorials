from fastapi import APIRouter, Request, status, Response
from services import ImageGenerationService
from fastapi import Depends
from utils import get_image_generation_service
import time
import random

router = APIRouter(
    tags=["Image Generation"],
)

@router.post("/images/generate", status_code=status.HTTP_201_CREATED)
async def generate_image(
    request: Request,
    image_generation_service: ImageGenerationService = Depends(get_image_generation_service)):
    wait_time = random.randint(1, 5)
    time.sleep(wait_time)
    image_bytes, format = await image_generation_service.generate_image()
    return Response(content=image_bytes, media_type=f"image/{format.lower()}")