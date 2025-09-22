from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from config import DATABASE_URL
import os



# Создаём движок
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Нужно только для SQLite
)

# Создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Инициализация БД
def init_db():
    Base.metadata.create_all(bind=engine)