from fastapi import APIRouter, status, UploadFile, File, HTTPException
from services import ImageService


router = APIRouter(
    tags=["Image Operations"],
)

image_service = ImageService()

@router.post("/files/upload", response_model=str, status_code=status.HTTP_201_CREATED)
async def upload_image_endpoint(file: UploadFile = File(...)):
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(status_code=415, detail="Unsupported file type.")
    if file.size > 5 * 1024 * 1024:  # 5 MB limit
        raise HTTPException(status_code=413, detail="File too large.")
    return await image_service.upload_image(file)