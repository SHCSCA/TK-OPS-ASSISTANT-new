from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()


class ProductModel(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    image_url = Column(String(512), nullable=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_engine(db_path: str = "sqlite:///tkops_desktop.db"):
    return create_engine(db_path, echo=False, future=True)


def create_session(engine=None):
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
