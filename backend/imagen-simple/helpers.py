from PIL import Image
import io
import random
import aiofiles
import os


SIZES: list[int] = [300, 400, 500]
COLORS: list[str] = ["red", "green", "blue"]
FORMATS: list[str] = ["JPEG", "PNG"]

async def generate_image() -> bytes:
    size = random.choice(SIZES)
    color = random.choice(COLORS)
    format = random.choice(FORMATS)

    # 1. Create a dummy image using Pillow
    img = Image.new("RGB", (size, size), color=color)
    
    # 2. Save the image to an in-memory BytesIO buffer
    buffer = io.BytesIO()
    img.save(buffer, format=format.upper())
    
    # 3. Extract the raw bytes from the buffer
    image_bytes = buffer.getvalue()
    
    # 4. Return the bytes with the correct media type
    return image_bytes, format

async def save_image_bytes(image_bytes: bytes, image_id: str, format: str = "JPEG") -> None:
    file_name: str = f"{image_id}.{format.lower()}"
    filename: str = os.path.join("data", file_name)
    async with aiofiles.open(filename, "wb") as f:
        await f.write(image_bytes)
    return filename

