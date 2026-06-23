import io
from fastapi import FastAPI, Response
from PIL import Image

app = FastAPI()

@app.get('/')
def index():
    return {"message": "Hello from serverless FastAPI on Modal!"}

@app.get("/generate-image")
def generate_image():
    # 1. Create a dummy image using Pillow
    img = Image.new("RGB", (300, 300), color="blue")
    
    # 2. Save the image to an in-memory BytesIO buffer
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    
    # 3. Extract the raw bytes from the buffer
    image_bytes = buffer.getvalue()
    
    # 4. Return the bytes with the correct media type
    return Response(content=image_bytes, media_type="image/jpeg")
