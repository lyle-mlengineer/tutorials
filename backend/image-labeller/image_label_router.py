from fastapi import APIRouter, UploadFile, Request, status
from services import ImageLabellingService
from fastapi import Depends
from typing import Annotated
from db import get_db
from sqlalchemy.orm import Session
from schemas import NextImageResponse, ImageRead, ImageLabelRequest, ImageLabelResponse
from helpers import get_image_labelling_service

router = APIRouter(
    tags=["Image Labelling"],
)

@router.post("/images/label/{image_id}", response_model=ImageLabelResponse, status_code=status.HTTP_201_CREATED)
async def label_image(
    image_id: str, 
    label_request: ImageLabelRequest, 
    image_labelling_service: ImageLabellingService = Depends(get_image_labelling_service)):
    image_label = await image_labelling_service.label_image(image_id, label_request) 
    return image_label