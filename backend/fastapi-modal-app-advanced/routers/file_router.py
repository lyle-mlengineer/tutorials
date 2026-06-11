from fastapi import APIRouter
from routers.utils import FileReadResponse, write_file, read_file, write_data
from routers.schemas import FileWriteResponse, FileReadResponse, FileWriteRequest

router = APIRouter(
    tags=["File Operations"],
)

@router.get("/read-file", response_model=FileReadResponse)
def read_file_endpoint(file_name: str):
    """
    Endpoint to read content from a file in the output volume."""
    return read_file(file_name)

@router.post("/write-file", response_model=FileWriteResponse)
def write_file_endpoint(request: FileWriteRequest):
    """
    Endpoint to write content to a file in the output volume."""
    return write_file(request.name, request.content)

@router.post("/write-data", response_model=FileWriteResponse)
def write_data_endpoint(request: FileWriteRequest):
    """
    Endpoint to write data to a file in the output volume."""
    return write_data(request.name, request.content)