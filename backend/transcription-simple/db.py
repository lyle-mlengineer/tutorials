from sqlalchemy import String, create_engine, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB


POSTGRES_USER: str = "lyle"
POSTGRES_PASSWORD: str = "lyle"
POSTGRES_DB: str = "imagen_simple"
POSTGRES_HOST: str = "0.0.0.0"
POSTGRES_PORT: int = 5432

db_url = "postgresql://neondb_owner:npg_E1xp0DSXVZQm@ep-floral-bush-adoorv67-pooler.c-2.us-east-1.aws.neon.tech/transcriptions?sslmode=require&channel_binding=require"

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

class AudioFile(Base):
    __tablename__ = "audio_files"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    format: Mapped[str] = mapped_column(String(255), default="wav")
    fileid: Mapped[str] = mapped_column(String(255), nullable=True)
    transcribed: Mapped[bool] = mapped_column(Boolean, default=False)

    transcriptions: Mapped[list["AudioFileTranscription"]] = relationship("AudioFileTranscription", back_populates="audio_file")

class AudioFileTranscription(Base):
    __tablename__ = "audio_file_transcriptions"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    audio_file_id: Mapped[str] = mapped_column(String(255), ForeignKey("audio_files.id"))
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    transcription_text: Mapped[str] = mapped_column(Text, nullable=True)
    machine_transcription_text: Mapped[str] = mapped_column(Text, nullable=True)

    # Defaulting to an empty dict prevents None errors
    transcription_metadata: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}") 
    audio_file: Mapped["AudioFile"] = relationship("AudioFile", back_populates="transcriptions")

    __table_args__ = (
        # JSONB performance requires a GIN index
        Index("ix_audio_file_transcriptions_transcription_metadata", "transcription_metadata", postgresql_using="gin"),
    )