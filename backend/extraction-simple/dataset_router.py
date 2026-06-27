from fastapi import status, Depends, HTTPException, APIRouter
from services import DatasetService
from models import DatasetCreate
from utils import get_dataset_service


router = APIRouter(
    tags=["Dataset Operations"],
)

@router.post("/dataset", status_code=status.HTTP_201_CREATED)
async def create_dataset(
    create_request: DatasetCreate, 
    dataset_service: DatasetService = Depends(get_dataset_service)):
    return await dataset_service.create_dataset(create_request)

@router.get("/datasets")
async def get_datasets(dataset_service: DatasetService = Depends(get_dataset_service)):
    return await dataset_service.get_datasets()

@router.get("/dataset/{id}")
async def get_dataset(id: str, dataset_service: DatasetService = Depends(get_dataset_service)):
    return await dataset_service.get_dataset(id)

@router.get("/dataset/name/{name}")
async def get_dataset_by_name(name: str, dataset_service: DatasetService = Depends(get_dataset_service)):
    return await dataset_service.get_dataset_by_name(name)