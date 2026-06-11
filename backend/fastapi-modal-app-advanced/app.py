from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import modal
from pydantic import BaseModel
import logging


GPU = "T4"
DEVICE: str = "cuda"
CACHE_VOLUME_NAME = "hf-cache"
OUTPUT_VOLUME_NAME = "outputs"
SECRET_NAME = "ssflow"
CACHE_DIR = "/cache"
OUTPUT_DIR = "/output"
DATA_DIR = "/data"

APP_NAME = "fastapi-modal-app"

def init_function():
    logging.info("Initializing the remote container...")
    # Perform any necessary setup here, such as downloading models or initializing resources

cache_volume = modal.Volume.from_name(CACHE_VOLUME_NAME, create_if_missing=True)
output_volume = modal.Volume.from_name(OUTPUT_VOLUME_NAME, create_if_missing=True)

# 1. Configure the remote container image
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_requirements("requirements.txt")
    .run_function(init_function, gpu=GPU)
    .add_local_file("/home/lyle/.drive/credentials.json", "/root/.drive/credentials.json", copy=True)
    .add_local_dir("model_config/", "/root/model_config", copy=True)
    .add_local_dir("data/", remote_path="/data", copy=True)
    .add_local_python_source("core", copy=True)
    .add_local_python_source("routers", copy=True)
    .env({
        "MODEL_CONFIG_DIR": "/root/model_config",
        "GOOGLE_DRIVE_CREDENTIALS": "/root/.drive/credentials.json",
    })
)

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
    from routers.file_router import router as file_router

    setup_logging()

    settings: Settings = Settings()

    logging.info(f"App name: {settings.APP_NAME}")
    logging.info(f"App version: {settings.APP_VERSION}")

    web_app = FastAPI(
        title=settings.APP_NAME, 
        version=settings.APP_VERSION, 
        description=settings.APP_DESCRIPTION, 
        summary=settings.APP_SUMMARY)
    
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

    web_app.include_router(file_router, prefix="/files")

    @web_app.get(
            "/", 
            summary="Root Endpoint", 
            description="A simple endpoint to verify the server is running.", 
            tags=["Home"])
    def home():
        return {"message": "Hello from serverless FastAPI on Modal!"}

    return web_app
