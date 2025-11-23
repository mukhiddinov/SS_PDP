import os
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)

Base = declarative_base()

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    degree = Column(Integer, nullable=False)
    class_name = Column(String, unique=True, nullable=False)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    class_name = Column(String)

class Spreadsheet(Base):
    __tablename__ = 'spreadsheets'
    id = Column(Integer, primary_key=True)
    degree = Column(Integer, unique=True, nullable=False)
    url = Column(String, nullable=False)
    sheet_name = Column(String)

class ScheduleCache(Base):
    __tablename__ = 'schedule_cache'
    id = Column(Integer, primary_key=True)
    class_name = Column(String, unique=True, nullable=False)
    data = Column(JSON)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 🟢 YANGI QO‘SHILGAN FUNKSIYA — MUAMMONI 100% HAL QILADI
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
