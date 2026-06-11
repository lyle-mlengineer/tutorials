from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "fastapi-modal-app"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "A serverless FastAPI application running on Modal."
    APP_SUMMARY: str = ""

    OUTPUT_DIR: str = "/output"
    DATA_DIR: str = "/data"