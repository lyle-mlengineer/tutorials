from schemas import ImageLabelRequest, ImageLabelResponse, ImageRead
from sqlalchemy.orm import Session
from fastapi import Request, UploadFile, HTTPException
import os
import uuid
import aiofiles
from db import Image


class ImageService:
    def __init__(self, session: Session):
        self.session = session

    async def upload(self, file: UploadFile) -> ImageRead:
        try:
            self.session.begin()
            file_path = await self.save_file(file)
            id: str = file_path.split("/")[-1].split(".")[0]
            extension: str = file_path.split("/")[-1].split(".")[1]
            image_in_db: Image = Image(id=id, extension=extension)
            self.session.add(image_in_db)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
        else:
            image_in_db = self.session.query(Image).filter(Image.id == id).first()
            return ImageRead.from_image(image_in_db)
        
    async def get_next_image(self) -> ImageRead | None:
        try:
            image_in_db: Image = self.session.query(Image).filter(Image.labelled == False).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting next image: {e}")
        else:
            if image_in_db is None:
                return None
            return ImageRead.from_image(image_in_db)
        
    async def get_image(self, id: str) -> ImageRead:
        try:
            image_in_db: Image = self.session.query(Image).filter(Image.id == id).first()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting image: {e}")
        else:
            if image_in_db is None:
                return None
            return ImageRead.from_image(image_in_db)
        
    async def delete_image(self, id: str):
        try:
            self.session.begin()
            await self.delete_file(id)
            image_in_db: Image = self.session.query(Image).filter(Image.id == id).first()
            self.session.delete(image_in_db)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting image: {e}")
        
    async def list_images(self) -> list[ImageRead]:
        try:
            images_in_db: list[Image] = self.session.query(Image).all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing images: {e}")
        else:
            return [ImageRead.from_image(image) for image in images_in_db]


    async def save_file(self, file: UploadFile) -> str:
        # Generate a secure, unique filename to prevent path traversal and overwrites
        file_extension = os.path.splitext(file.filename)[1]
        secure_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join("data", secure_filename)

        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                content = await file.read()  # Read file content
                await out_file.write(content)  # Write to disk
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
        finally:
            # Ensure the temporary file is closed
            await file.close()
        return file_path
    
    async def delete_file(self, id: str) -> str:
        id = f"{id}.jpeg"
        file_path = os.path.join("data", id)
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")
        return file_path


class ImageLabellingService:
    def __init__(self):
            pass
    
    def label_image(self, label_request: ImageLabelRequest) -> ImageLabelResponse:
        return "label"
    
    def get_next_image(self) -> str:
        return "example.jpeg"
    

class DeduplicationService:
     pass

class HarmfulContentDetectionService:
     pass