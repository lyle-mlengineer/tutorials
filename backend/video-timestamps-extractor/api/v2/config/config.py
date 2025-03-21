import os


class BaseConfig:
    DEBUG: bool = True
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.environ.get("REDIS_PORT", 6379)
    REDIS_DB: int = os.environ.get("REDIS_DB", 0)
    REDIS_VIDEOS_QUEUE: str = os.environ.get("REDIS_VIDEOS_QUEUE", "videos")
    REDIS_TIMESTAMPS_QUEUE: str = os.environ.get("REDIS_TIMESTAMPS_QUEUE", "timestamps")
    REDIS_PLAYLIST_QUEUE: str = os.environ.get("REDIS_TIMESTAMPS_QUEUE", "playlists")

    POSTGRES_USER = os.environ.get("POSTGRES_USER", "lyle")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "lyle")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "lyle")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    # DATABASE_URL = f"sqlite:///{DATABASE_FILE_NAME}"
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
