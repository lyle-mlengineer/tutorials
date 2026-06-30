from sqlalchemy import String, create_engine, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB


POSTGRES_USER: str = "lyle"
POSTGRES_PASSWORD: str = "lyle"
POSTGRES_DB: str = "extractions"
POSTGRES_HOST: str = "0.0.0.0"
POSTGRES_PORT: int = 5432

db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass

class Dataset(Base):
    __tablename__ = "datasets"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

class Video(Base):
    __tablename__ = "videos"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    # dataset_id: Mapped[str] = mapped_column(String(255), ForeignKey("dataset.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

class Playlist(Base):
    __tablename__ = "playlists"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    # dataset_id: Mapped[str] = mapped_column(String(255), ForeignKey("dataset.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

class Channel(Base):
    __tablename__ = "channels"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    # dataset_id: Mapped[str] = mapped_column(String(255), ForeignKey("dataset.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

class VideoExtraction(Base):
    __tablename__ = "video_extractions"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    video_id: Mapped[str] = mapped_column(String(255), ForeignKey("videos.id"))
    dataset_id: Mapped[str] = mapped_column(String(255), ForeignKey("datasets.id"))
    # Defaulting to an empty dict prevents None errors
    timestamps: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}") 

    __table_args__ = (
        # JSONB performance requires a GIN index
        Index("ix_video_extractions_timestamps", "timestamps", postgresql_using="gin"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))