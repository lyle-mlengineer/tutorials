from pydantic import BaseModel


class FileWriteRequest(BaseModel):
    name: str
    content: str

class FileWriteResponse(BaseModel):
    file_path: str

class FileReadResponse(BaseModel):
    file_path: str

class FileReadResponse(BaseModel):
    content: str