import io
from fastapi import FastAPI, Response, status, HTTPException, Security
import os
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form
from typing import Annotated
from time import sleep
from fastapi.security.api_key import APIKeyHeader
import random


SIZES: list[int] = [300, 400, 500]
COLORS: list[str] = ["red", "green", "blue"]
FORMATS: list[str] = ["JPEG", "PNG"]

API_KEY_NAME: str = "X-API-Key"
os.environ["GENERATION_API_KEY"] = "1234"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def index():
    return {"message": "Hello from serverless FastAPI on Modal!"}

@app.get('/health')
def health():
    return {"status": "ok"}

@app.get("/generate-image")
def generate_image(
    api_key_header: str = Security(api_key_header)
):
    if api_key_header != os.getenv("GENERATION_API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API key")
    # Simulate advanced processing
    sleep_time = random.randint(1, 5)
    sleep(sleep_time)

    # 1. Create a dummy image using Pillow
    size = random.choice(SIZES)
    color = random.choice(COLORS)
    format = random.choice(FORMATS)

    img = Image.new("RGB", (size, size), color=color)
    
    # 2. Save the image to an in-memory BytesIO buffer
    buffer = io.BytesIO()
    img.save(buffer, format=format.upper())
    
    # 3. Extract the raw bytes from the buffer
    image_bytes = buffer.getvalue()
    
    # 4. Return the bytes with the correct media type
    return Response(content=image_bytes, media_type=f"image/{format.lower()}")
