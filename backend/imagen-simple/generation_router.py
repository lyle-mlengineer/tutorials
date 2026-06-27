from fastapi import APIRouter, Request, status, Response, Security, HTTPException
from services import ImageGenerationService
from fastapi import Depends
from utils import get_image_generation_service
import time
import random
from fastapi.security.api_key import APIKeyHeader
import os

router = APIRouter(
    tags=["Image Generation"],
)

API_KEY_NAME: str = "X-API-Key"
os.environ["GENERATION_API_KEY"] = "1234"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

@router.post("/images/generate", status_code=status.HTTP_201_CREATED)
async def generate_image(
    request: Request,
    api_key_header: str = Security(api_key_header),
    image_generation_service: ImageGenerationService = Depends(get_image_generation_service)):
    if api_key_header != os.getenv("GENERATION_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API key")
    wait_time = random.randint(1, 5)
    time.sleep(wait_time)
    image_bytes, format = await image_generation_service.generate_image()
    return Response(content=image_bytes, media_type=f"image/{format.lower()}")