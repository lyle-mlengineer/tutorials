import aiofiles
from fastapi import UploadFile
import os
import uuid


class ImageService:
    async def upload_image(self, file: UploadFile):
        image_extension: str = os.path.splitext(file.filename)[1]
        file_Name: str = f"{uuid.uuid4()}.{image_extension}"
        file_path: str = os.path.join("data", file_Name)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file.file.read())
        return file_Name