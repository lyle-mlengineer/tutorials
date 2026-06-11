from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import modal
from pydantic import BaseModel

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GPU = "T4"
DEVICE: str = "cuda"
CACHE_DIR = "/cache"
OUTPUT_DIR = "/output"

APP_NAME = "fastapi-modal-app"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "A serverless FastAPI application running on Modal."
APP_SUMMARY = ""

logger.info(f"App name: {APP_NAME}")
logger.info(f"App version: {APP_VERSION}")

def init_function():
    logger.info("Initializing the remote container...")
    # Perform any necessary setup here, such as downloading models or initializing resources

cache_volume = modal.Volume.from_name("hf-cache", create_if_missing=True)
output_volume = modal.Volume.from_name("outputs", create_if_missing=True)

# 1. Configure the remote container image
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install_from_requirements("requirements.txt")
    .run_function(init_function, gpu=GPU)
    .add_local_file("/home/lyle/.drive/credentials.json", "/root/.drive/credentials.json", copy=True)
    .add_local_dir("config/", "/root/config", copy=True)
    .env({
        "CONFIG_DIR": "/root/config",
        "GOOGLE_DRIVE_CREDENTIALS": "/root/.drive/credentials.json",
    })
)

app = modal.App(
    APP_NAME, 
    image=image,
    volumes={CACHE_DIR: cache_volume, OUTPUT_DIR: output_volume},  
    secrets=[modal.Secret.from_name("ssflow")]
)

class APIRequest(BaseModel):
    input_data: str

class APIResponse(BaseModel):
    output_data: str

# 2. Build your FastAPI application locally inside a wrapper function
@app.function(image=image)
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def fastapi_wrapper():
    web_app = FastAPI(
        title=APP_NAME, 
        version=APP_VERSION, 
        description=APP_DESCRIPTION, 
        summary=APP_SUMMARY)
    
    # Configure middleware or routers
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @web_app.get("/")
    def read_root():
        return {"message": "Hello from serverless FastAPI on Modal!"}
    
    @web_app.post("/process", response_model=APIResponse)
    def process_data(request: APIRequest):
        """
        Simulate some processing logic here. In a real application, this could involve calling a machine learning model or 
        interacting with other external services."""
        # Simulate some processing
        output_data = f"Processed: {request.input_data}"
        return APIResponse(output_data=output_data)
        
    return web_app
