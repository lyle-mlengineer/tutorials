from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from image_router import router as router_image


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(router_image)

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello from serverless FastAPI on Modal!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/files/upload", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def upload_files(
    request: Request,
    ):
    return templates.TemplateResponse(
        name="upload.html", 
        request=request,
        context={
            "datasets": "ds"
        }
    )