# models.py

from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL ulanish manzili. O'zingiznikiga o'zgartirishni unutmang.
DATABASE_URL = "postgresql://student_schedule_user:2725@localhost:5432/student_schedule_db" 

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Group(Base):
    """Guruhlar haqidagi ma'lumotlar jadvali."""
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    degree = Column(Integer, nullable=False)  # Kurs (1, 2, 3, 4)
    class_name = Column(String, unique=True, nullable=False) # Guruh nomi (Masalan: "22-302 SW")

class User(Base):
    """Bot foydalanuvchilarining tanlangan guruhlarini saqlash."""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    class_name = Column(String) # Tanlangan guruh nomi

class Spreadsheet(Base):
    """Har bir kurs uchun Google Sheets manzilini va varaq nomini saqlash."""
    __tablename__ = 'spreadsheets'
    id = Column(Integer, primary_key=True)
    degree = Column(Integer, unique=True, nullable=False)
    url = Column(String, nullable=False) # Google Sheets URL
    sheet_name = Column(String) # Jadval varag'ining nomi (Masalan: "Time Table 4th course")

class ScheduleCache(Base):
    """Jadvalni har kuni API dan olib saqlash uchun kesh jadvali."""
    __tablename__ = 'schedule_cache'
    id = Column(Integer, primary_key=True)
    class_name = Column(String, unique=True, nullable=False)
    data = Column(JSON) # Jadval JSON formatida saqlanadi (API dan olingan)

# Ma'lumotlar bazasini yaratish (faqat birinchi marta ishga tushirganda kerak)
# Base.metadata.create_all(engine) 

# SessionMaker obyektini yaratish
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
