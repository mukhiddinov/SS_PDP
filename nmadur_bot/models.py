import os
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL ni environment variable dan olish
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable topilmadi!")

engine = create_engine(DATABASE_URL)
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

# Agar kerak bo'lsa, container birinchi ishga tushganda jadval yaratish:
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
