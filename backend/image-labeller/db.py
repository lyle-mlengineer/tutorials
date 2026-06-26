from sqlalchemy import String, create_engine, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column


POSTGRES_USER: str = "lyle"
POSTGRES_PASSWORD: str = "lyle"
POSTGRES_DB: str = "faces"
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

class Image(Base):
    __tablename__ = "images"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    date_created: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    labelled: Mapped[bool] = mapped_column(Boolean, default=False)
    extension: Mapped[str] = mapped_column(String(255), default="jpg")

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    image_label_tags: Mapped[list['ImageLabelTag']] = relationship("ImageLabelTag", back_populates="tag")

class ImageLabel(Base):
    __tablename__ = "image_labels"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    image_id: Mapped[str] = mapped_column(String(255))
    gender: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    image_label_tags: Mapped[list['ImageLabelTag']] = relationship("ImageLabelTag", back_populates="image_label")

class ImageLabelTag(Base):
    __tablename__ = "image_label_tags"
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    image_label_id: Mapped[str] = mapped_column(String(255), ForeignKey("image_labels.id"))
    tag_id: Mapped[str] = mapped_column(String(255), ForeignKey("tags.id"))

    image_label: Mapped['ImageLabel'] = relationship("ImageLabel", back_populates="image_label_tags")
    tag: Mapped['Tag'] = relationship("Tag", back_populates="image_label_tags")