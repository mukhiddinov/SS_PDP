# schedule_updater.py

import requests
import json
from datetime import datetime, timedelta # timedelta import qilindi
from urllib.parse import urlparse, parse_qs
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio # Asinxron vazifalar uchun

# --- Importlar ---
from models import SessionLocal, User, Group, Spreadsheet, ScheduleCache 
# Bot instansiyasini main.py dan import qilish (telegram xabari yuborish uchun)
try:
    # Bu Botning Application obyektiga kirishni ta'minlaydi
    from main import application 
except ImportError:
    application = None # Agar main.py ishga tushmagan bo'lsa

# --- Global Sozlamalar ---
API_URL = "http://127.0.0.1:8000/schedule/" 
scheduler = BackgroundScheduler()

LESSON_TIMES = [
    {"para": 1, "start": "09:00"},
    {"para": 2, "start": "10:30"},
    {"para": 3, "start": "12:00"},
    {"para": 4, "start": "13:30"},
    {"para": 5, "start": "15:00"},
    {"para": 6, "start": "16:30"},
    {"para": 7, "start": "18:00"},
]
REMINDER_OFFSET_MINUTES = 4 # Eslatmani 10 daqiqa oldin yuborish

# --- Yangi Asinxron Eslatma Funksiyasi ---

async def send_lesson_reminder(class_name: str, para_number: int):
    """Berilgan guruhga, berilgan para uchun eslatmani yuboradi."""
    if not application:
        print("Bot Application obyekti topilmadi. Eslatma yuborilmadi.")
        return

    db_session = SessionLocal()
    try:
        # Keshdan bugungi jadvalni olish
        cache_entry = db_session.query(ScheduleCache).filter(ScheduleCache.class_name == class_name).first()
        
        if not cache_entry or not cache_entry.data:
            return

        schedule_data = cache_entry.data
        
        # Para bo'yicha ma'lumotni topish (API dan kelgan ma'lumotda 'para' String bo'lishi mumkin)
        lesson = next((item for item in schedule_data if item.get('para') == str(para_number)), None)
        
        if not lesson or lesson.get('subject') in ['Bo\'sh', 'Bo\'sh kun']: 
            return # Dars bo'sh bo'lsa yoki topilmasa

        # Eslatma matnini formatlash
        reminder_text = (
            f"🔔 **ESLATMA (10 daqiqadan so'ng): {class_name}**\n\n"
            f"🔸 **{lesson.get('para', 'N/A')}**-juft: **{lesson.get('time', 'N/A')}**\n"
            f"📚 Fan: **{lesson.get('subject', 'N/A')}**\n"
            f"🚪 Xona: {lesson.get('room', 'N/A')}\n"
            f"👤 O'qituvchi: {lesson.get('teacher', 'N/A')}"
        )

        # Shu guruhni tanlagan barcha foydalanuvchilarni topish
        user_chat_ids = db_session.query(User.chat_id).filter(User.class_name == class_name).all()
        
        for chat_id_tuple in user_chat_ids:
            chat_id = chat_id_tuple[0]
            try:
                # Eslatmani yuborish
                await application.bot.send_message(
                    chat_id=chat_id, 
                    text=reminder_text, 
                    parse_mode='Markdown'
                )
            except Exception as e:
                print(f"Eslatma yuborishda xato ({chat_id}): {e}")

    finally:
        db_session.close()

# --- Kunlik Eslatma Ishlarini Jadvalga Qo'shish Funksiyasi ---

def start_daily_notifications():
    """Barcha guruhlar uchun kunlik eslatma ishlarini dinamik ravishda qo'shadi."""
    print("🔔 Kunlik eslatmalar jadvalga qo'shilmoqda...")
    
    db_session = SessionLocal()
    try:
        # Barcha unikal guruh nomlarini olish
        all_class_names = [r[0] for r in db_session.query(Group.class_name).distinct().all()]
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Avvalgi kun uchun qo'shilgan eslatma ishlarini o'chirish
        for job in scheduler.get_jobs():
            if job.id.startswith('reminder_'):
                scheduler.remove_job(job.id)
        
        for lesson in LESSON_TIMES:
            # Dars boshlanish vaqtidan 10 daqiqa oldingi vaqtni hisoblash
            start_time = datetime.strptime(lesson['start'], "%H:%M")
            reminder_time = start_time - timedelta(minutes=REMINDER_OFFSET_MINUTES)
            
            reminder_hour = reminder_time.hour
            reminder_minute = reminder_time.minute
            
            for class_name in all_class_names:
                # Har bir dars uchun alohida ish qo'shish
                job_id = f"reminder_{class_name}_{lesson['para']}_{today}"

                scheduler.add_job(
                    send_lesson_reminder, 
                    'cron', 
                    hour=reminder_hour, 
                    minute=reminder_minute,
                    args=[class_name, lesson['para']],
                    id=job_id,
                    misfire_grace_time=60, # 60 sekund kechiksa ham ishga tushirsin
                    max_instances=1 # Bir vaqtda faqat bitta instansiya ishlasin
                )
                print(f" -> {class_name} ({lesson['para']}-para) uchun eslatma soat {reminder_hour:02d}:{reminder_minute:02d} ga qo'shildi.")

    except Exception as e:
        print(f"Kunlik eslatmalarni qo'shishda xato: {e}")
        
    finally:
        db_session.close()


# --- Asosiy Kesh Yangilash Funksiyasi (o'zgarishsiz qoldi) ---

def fetch_and_update_cache(session, class_name):
    """Berilgan class_name uchun jadvalni API orqali oladi va keshni yangilaydi."""
    
    # 1. Class_name orqali degree ni topish
    group = session.query(Group).filter(Group.class_name == class_name).first()
    if not group:
        print(f"Guruh topilmadi: {class_name}")
        return

    # 2. Degree orqali Spreadsheet URL va SHEET_NAME ni topish
    spreadsheet_info = session.query(Spreadsheet).filter(Spreadsheet.degree == group.degree).first()
    if not spreadsheet_info:
        print(f"Spreadsheet ma'lumoti topilmadi: {group.degree}-kurs")
        return

    # 3. URL dan ID ni ajratib olish va SHEET_NAME ni DB dan olish
    try:
        url_parts = spreadsheet_info.url.split('/')
        spreadsheet_id = url_parts[5]
        
        sheet_name = spreadsheet_info.sheet_name
        
        if not sheet_name:
            print(f"⚠️ {group.degree}-kurs uchun DB da sheet_name bo'sh.")
            return

    except IndexError:
        print(f"Noto'g'ri URL formati (ID ajratishda xato): {spreadsheet_info.url}")
        return

    # 4. Current day (hafta kuni) ni olish
    day_name = datetime.now().strftime('%A') 

    # 5. Request body shakllantirish
    payload = {
        "spreadsheet_id": spreadsheet_id,
        "sheet_name": sheet_name, 
        "class_name": class_name,
        "day_name": day_name
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status() 
        schedule_data = response.json() 

        # 6. Keshni yangilash
        cache_entry = session.query(ScheduleCache).filter(ScheduleCache.class_name == class_name).first()
        if cache_entry:
            cache_entry.data = schedule_data
        else:
            cache_entry = ScheduleCache(class_name=class_name, data=schedule_data)
            session.add(cache_entry)
            
        session.commit()
        print(f"Kesh muvaffaqiyatli yangilandi: {class_name} uchun {day_name}")

    except requests.exceptions.RequestException as e:
        print(f"API so'rovida xato (Kesh yangilanmadi): {e}")
        session.rollback()


# --- Barcha Keshni Yangilash Funksiyasi (Scheduler uchun) ---

def refresh_all_cache():
    """Barcha mavjud guruhlar uchun keshni yangilaydi."""
    db_session = SessionLocal() 
    try:
        all_class_names = [r[0] for r in db_session.query(Group.class_name).distinct().all()]
        
        for class_name in all_class_names:
            fetch_and_update_cache(db_session, class_name) 

    finally:
        db_session.close()


# --- Scheduler (Vaqtni rejalashtirish) Funksiyasi ---

def start_scheduler():
    """Keshni yangilash jadvalini (Scheduler) ishga tushirish."""
    
    # Har kuni ertalab soat 7:00 da keshni yangilaydi
    scheduler.add_job(refresh_all_cache, 'cron', hour=7, minute=0) 
    
    # Har kuni ertalab 7:01 da kunlik eslatmalarni jadvalga qo'shadi
    scheduler.add_job(start_daily_notifications, 'cron', hour=7, minute=1)
    
    scheduler.start()
    print("✅ Scheduler (Keshni yangilash mexanizmi) ishga tushirildi.")
