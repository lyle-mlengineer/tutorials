from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import modal
import logging
from contextlib import asynccontextmanager
import transformers


GPU = "T4"
DEVICE: str = "cuda"
CACHE_VOLUME_NAME = "hf-cache"
OUTPUT_VOLUME_NAME = "outputs"
SECRET_NAME = "ssflow"
CACHE_DIR = "/cache"
OUTPUT_DIR = "/output"
DATA_DIR = "/data"

APP_NAME = "fastapi-modal-app"
MODEL_NAME = "openai/whisper-medium"
LANGUAGE: str = "sw"
TASK: str = "transcribe"

def init_function():
    logging.info("Initializing the remote container...")
    feature_extractor = transformers.WhisperFeatureExtractor.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME,
    )
    tokenizer = transformers.WhisperTokenizer.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME,
    )
    model = transformers.WhisperForConditionalGeneration.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME,
    )

    # Create a processor that combines the feature extractor and tokenizer
    processor = transformers.WhisperProcessor(
        feature_extractor=feature_extractor,
        tokenizer=tokenizer,
    )

cache_volume = modal.Volume.from_name(CACHE_VOLUME_NAME, create_if_missing=True)
output_volume = modal.Volume.from_name(OUTPUT_VOLUME_NAME, create_if_missing=True)

# 1. Configure the remote container image
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_requirements("requirements.txt")
    .run_function(init_function, gpu=GPU)
    .add_local_dir("data/", remote_path="/data", copy=True)
    .add_local_dir("model_config/", "/root/model_config", copy=True)
    .add_local_python_source("core", copy=True)
    .add_local_python_source("routers", copy=True)
    .env({
        "MODEL_CONFIG_DIR": "/root/model_config",

    })
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting application...")
    # init_app(app)
    feature_extractor = transformers.WhisperFeatureExtractor.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME,
    )
    tokenizer = transformers.WhisperTokenizer.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME,
    )
    model = transformers.WhisperForConditionalGeneration.from_pretrained(
        pretrained_model_name_or_path=MODEL_NAME,
    )

    # Create a processor that combines the feature extractor and tokenizer
    processor = transformers.WhisperProcessor(
        feature_extractor=feature_extractor,
        tokenizer=tokenizer,
    )
    app.state.model = model
    app.state.processor = processor
    yield
    logging.info("Shutting down application...")
    del app.state.model
    del app.state.processor

app = modal.App(
    APP_NAME, 
    image=image,
    volumes={CACHE_DIR: cache_volume, OUTPUT_DIR: output_volume},  
    secrets=[modal.Secret.from_name(SECRET_NAME)]
)

# 2. Build your FastAPI application locally inside a wrapper function
@app.function(image=image)
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def fastapi_wrapper():
    import logging
    from core.logging import setup_logging
    from core.config import Settings
    from routers.transcription_router import router as transcription_router

    setup_logging()

    settings: Settings = Settings()

    logging.info(f"App name: {settings.APP_NAME}")
    logging.info(f"App version: {settings.APP_VERSION}")

    web_app = FastAPI(
        title=settings.APP_NAME, 
        version=settings.APP_VERSION, 
        description=settings.APP_DESCRIPTION, 
        summary=settings.APP_SUMMARY,
        lifespan=lifespan
    )
    
    # Configure middleware or routers
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    web_app.mount(
        "/data", 
        StaticFiles(directory="/data"), 
        name="data"
    )

    web_app.include_router(transcription_router, prefix="/api/v1/audio")

    @web_app.get(
            "/", 
            summary="Root Endpoint", 
            description="A simple endpoint to verify the server is running.", 
            tags=["Home"])
    def home():
        return {"message": "Hello from serverless FastAPI on Modal!"}

    return web_app
