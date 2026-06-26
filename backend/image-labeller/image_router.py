from fastapi import APIRouter, UploadFile, Request
from services import ImageService
from fastapi import Depends
from typing import Annotated
from db import get_db
from sqlalchemy.orm import Session
from schemas import NextImageResponse, ImageRead
from helpers import get_image_service

router = APIRouter(
    tags=["Image Operations"],
)

@router.post("/upload")
async def upload(file: UploadFile, image_service: ImageService = Depends(get_image_service)):
    return await image_service.upload(file)

@router.get("/get_next_image")
async def get_next_image(request: Request, image_service: ImageService = Depends(get_image_service)):
    image: ImageRead = await image_service.get_next_image()
    image_path: str = f"{image.id}.{image.extension}"
    image_url: str = request.url_for("data", path=image_path).__str__()
    return NextImageResponse(**image.model_dump(), image_url=image_url)

@router.get("/get_image")
async def get_image(id: str, image_service: ImageService = Depends(get_image_service)):
    return await image_service.get_image(id)

@router.delete("/delete_image")
async def delete_image(id: str, image_service: ImageService = Depends(get_image_service)):
    return await image_service.delete_image(id)

@router.get("/list_images")
async def list_images(image_service: ImageService = Depends(get_image_service)):
    return await image_service.list_images()