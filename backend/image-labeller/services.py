from schemas import ImageLabelRequest, ImageLabelResponse, ImageRead
from sqlalchemy.orm import Session
from fastapi import Request, UploadFile, HTTPException
import os
import uuid
import aiofiles
from db import Image, ImageLabel, Tag, ImageLabelTag


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
    

class TagService:
    def __init__(self, session: Session):
        self.session = session

    def get_tags(self) -> list[Tag]:
        return self.session.query(Tag).all()
    
    def get_tag(self, id: str) -> Tag | None:
        return self.session.query(Tag).filter(Tag.id == id).first()
    
    def get_tag_by_name(self, name: str) -> Tag | None:
        return self.session.query(Tag).filter(Tag.name == name).first()
    
    def create_tag(self, name: str) -> Tag:
        tag: Tag | None = self.get_tag_by_name(name)
        if tag is not None:
            return tag
        id: str = str(uuid.uuid4())
        tag = Tag(name=name, id=id)
        self.session.add(tag)
        self.session.commit()
        return tag
    
    def delete_tag(self, id: str):
        tag: Tag | None = self.get_tag(id)
        if tag is None:
            return
        self.session.delete(tag)
        self.session.commit()

    def get_image_label_tag(self, image_label_id: str, tag_id: str):
        return self.session.query(ImageLabelTag).filter(ImageLabelTag.image_label_id == image_label_id, ImageLabelTag.tag_id == tag_id).first()

    def create_image_label_tag(self, image_label_id: str, tag_id: str):
        image_label_tag: ImageLabelTag | None = self.get_image_label_tag(image_label_id, tag_id)
        if image_label_tag is not None:
            return image_label_tag
        image_label_tag = ImageLabelTag(image_label_id=image_label_id, tag_id=tag_id)
        self.session.add(image_label_tag)
        self.session.commit()
        return image_label_tag


class ImageLabellingService:
    def __init__(self, session: Session, image_service: ImageService, tag_service: TagService):
            self.session = session
            self.image_service = image_service
            self.tag_service = tag_service
    
    async def label_image(self, image_id: str, label_request: ImageLabelRequest) -> ImageLabelResponse:
        image: Image = await self.image_service.get_image(image_id)
        if image is None:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # self.session.begin()
        tag_ids: list[str] = []
        for tag_name in label_request.tags:
            tag: Tag = self.tag_service.create_tag(tag_name)
            tag_ids.append(tag.id)
        id: str = str(uuid.uuid4())
        image_label: ImageLabel = ImageLabel(
            image_id=image_id, gender=label_request.gender, description=label_request.description, id=id)
        
        image_label_tags: list[ImageLabelTag] = []
        for tag_id in tag_ids:
            image_label_tag: ImageLabelTag = self.tag_service.create_image_label_tag(id, tag_id)
            image_label_tags.append(image_label_tag)
        self.session.add(image_label)
        self.session.commit()
        
        return ImageLabelResponse.from_image_label(image_label)
    
    def get_image_label(self, id: str) -> ImageLabelResponse:
        image_label: ImageLabel = self.session.query(ImageLabel).filter(ImageLabel.id == id).first()
        if image_label is None:
            raise HTTPException(status_code=404, detail="Image label not found")
        return ImageLabelResponse.from_image_label(image_label)
    
    def get_image_label_image_id(self, image_id: str):
        image_label: ImageLabel = self.session.query(ImageLabel).filter(ImageLabel.image_id == image_id).first()
        return image_label
    
    def get_image_labels(self):
        image_labels: list[ImageLabel] = self.session.query(ImageLabel).all()
        return [ImageLabelResponse.from_image_label(image_label) for image_label in image_labels]
    

class DeduplicationService:
     pass

class HarmfulContentDetectionService:
     pass