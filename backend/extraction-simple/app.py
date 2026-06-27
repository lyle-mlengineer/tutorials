from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from extraction_router import router as router_extraction
from dataset_router import router as router_dataset
from utils import create_all
from services import DatasetService
from utils import get_dataset_service, get_datasets


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    yield

app: FastAPI = FastAPI(
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(
    "/static", 
    StaticFiles(directory="static"), 
    name="static"
    )
app.mount(
    "/data", 
    StaticFiles(directory="data"), 
    name="data"
)

app.include_router(router_extraction)
app.include_router(router_dataset)

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello from serverless FastAPI on Modal!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/timestamps/extract", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def extract_timestamps(
    request: Request,
    dataset_service: DatasetService = Depends(get_dataset_service)
    ):
    datasets = await get_datasets(dataset_service)
    return templates.TemplateResponse(
        name="extract_timestamps.html", 
        request=request,
        context={
            "datasets": datasets
        }
    )