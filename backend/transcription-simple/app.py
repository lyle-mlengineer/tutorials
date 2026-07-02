from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app_helpers import get_tags, get_speakers, get_accents, setup_logging
from audio_router import router as router_audio
from audio_service import AudioFileService
from utils import get_audio_service
from schemas import PreloadAudioResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
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

app.include_router(router_audio, prefix="/api")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return {"message": "Hello from serverless FastAPI on Modal!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/audio/transcribe", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def transcribe_audio(request: Request, audio_service: AudioFileService = Depends(get_audio_service)):
    tags = await get_tags()
    speakers = await get_speakers()
    accents = await get_accents()
    audio: PreloadAudioResponse | None = audio_service.preload_audio(request)
    if audio:
        audio_id = audio.audio_id
        audio_url = audio.audio_url
    else:
        audio_id = None
        audio_url = None
    return templates.TemplateResponse(
        name="transcribe_audio.html", 
        request=request,
        context={
            "tags": tags,
            "speakers": speakers,
            "accents": accents,
            "audio_id": audio_id,
            "audio_url": audio_url
        }
    )