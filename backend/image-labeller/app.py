from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from helpers import get_next_image, get_image_tags
from schemas import ImageLabelRequest, ImageLabelResponse
from image_router import router as router_image
from contextlib import asynccontextmanager
from helpers import create_all



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

templates = Jinja2Templates(directory="templates")

app.include_router(router_image)

@app.get("/")
async def root():
    return {"message": "Hello from serverless FastAPI on Modal!"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/images/label", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def label_image(request: Request):
    image_name, image_url = await get_next_image(request)
    return templates.TemplateResponse(
        name="label_image.html", 
        request=request,
        context={
            "image_id": image_name,
            "image_src": image_url,
            "tags": await get_image_tags()
        }
    )

@app.post("/images/label/{image_id}", response_model=ImageLabelResponse, status_code=status.HTTP_201_CREATED)
async def label_image(image_id: str, label_request: ImageLabelRequest):
    print(label_request)
    return ImageLabelResponse(id=image_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)