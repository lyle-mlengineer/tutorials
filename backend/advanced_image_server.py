import io
from fastapi import FastAPI, Response
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form
from typing import Annotated
from time import sleep


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

@app.post("/generate-image")
def generate_image(
    size: Annotated[int, Form()] = 300,
    color: Annotated[str, Form()] = "blue",
    format: Annotated[str, Form()] = "JPEG",
):
    # Simulate advanced processing
    sleep(3)
    
    # 1. Create a dummy image using Pillow
    img = Image.new("RGB", (size, size), color=color)
    
    # 2. Save the image to an in-memory BytesIO buffer
    buffer = io.BytesIO()
    img.save(buffer, format=format.upper())
    
    # 3. Extract the raw bytes from the buffer
    image_bytes = buffer.getvalue()
    
    # 4. Return the bytes with the correct media type
    return Response(content=image_bytes, media_type=f"image/{format.lower()}")
