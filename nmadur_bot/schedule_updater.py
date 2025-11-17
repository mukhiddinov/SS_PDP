# schedule_updater_async.py

import os
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp  # requests o‘rniga async HTTP client

from models import SessionLocal, User, Group, Spreadsheet, ScheduleCache

try:
    from main import application
except ImportError:
    application = None

API_URL = "https://ss-pdp-api.onrender.com/schedule/"  # GET so'rov

scheduler = AsyncIOScheduler()

LESSON_TIMES = [
    {"para": 1, "start": "09:00"},
    {"para": 2, "start": "10:30"},
    {"para": 3, "start": "12:00"},
    {"para": 4, "start": "13:30"},
    {"para": 5, "start": "15:00"},
    {"para": 6, "start": "16:30"},
    {"para": 7, "start": "18:00"},
]
REMINDER_OFFSET_MINUTES = 4


async def fetch_and_update_cache(class_name: str):
    async with asyncio.Lock():  # DB va cache update blokirovka
        db_session = SessionLocal()
        try:
            group = db_session.query(Group).filter(Group.class_name == class_name).first()
            if not group:
                print(f"Guruh topilmadi: {class_name}")
                return

            spreadsheet_info = db_session.query(Spreadsheet).filter(Spreadsheet.degree == group.degree).first()
            if not spreadsheet_info:
                print(f"Spreadsheet ma'lumoti topilmadi: {group.degree}-kurs")
                return

            try:
                url_parts = spreadsheet_info.url.split('/')
                spreadsheet_id = url_parts[5]
                sheet_name = spreadsheet_info.sheet_name or ""
            except IndexError:
                print(f"Noto'g'ri URL formati: {spreadsheet_info.url}")
                return

            day_name = datetime.now().strftime('%A')
            payload = {
                "spreadsheet_id": str(spreadsheet_id),
                "sheet_name": str(sheet_name),
                "class_name": str(class_name),
                "day_name": str(day_name)
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, params=payload) as resp:
                    if resp.status != 200:
                        print(f"API so'rovi xato: {resp.status}")
                        return
                    schedule_data = await resp.json()

            cache_entry = db_session.query(ScheduleCache).filter(ScheduleCache.class_name == class_name).first()
            if cache_entry:
                cache_entry.data = schedule_data
            else:
                cache_entry = ScheduleCache(class_name=class_name, data=schedule_data)
                db_session.add(cache_entry)

            db_session.commit()
            print(f"Kesh yangilandi: {class_name} uchun {day_name}")

        except Exception as e:
            print(f"Kesh yangilashda xato: {e}")
            db_session.rollback()
        finally:
            db_session.close()


async def send_lesson_reminder(class_name: str, para_number: int):
    if not application:
        print("Bot Application topilmadi.")
        return

    db_session = SessionLocal()
    try:
        cache_entry = db_session.query(ScheduleCache).filter(ScheduleCache.class_name == class_name).first()
        if not cache_entry or not cache_entry.data:
            return

        lesson = next((l for l in cache_entry.data if str(l.get('para')) == str(para_number)), None)
        if not lesson or lesson.get('subject') in ['Bo\'sh', 'Bo\'sh kun']:
            return

        reminder_text = (
            f"🔔 **ESLATMA (10 daqiqadan so'ng): {class_name}**\n\n"
            f"🔸 **{lesson.get('para', 'N/A')}**-juft: **{lesson.get('time', 'N/A')}**\n"
            f"📚 Fan: **{lesson.get('subject', 'N/A')}**\n"
            f"🚪 Xona: {lesson.get('room', 'N/A')}\n"
            f"👤 O'qituvchi: {lesson.get('teacher', 'N/A')}"
        )

        user_chat_ids = db_session.query(User.chat_id).filter(User.class_name == class_name).all()
        for chat_id_tuple in user_chat_ids:
            chat_id = chat_id_tuple[0]
            try:
                await application.bot.send_message(chat_id=chat_id, text=reminder_text, parse_mode='Markdown')
            except Exception as e:
                print(f"Eslatma yuborishda xato ({chat_id}): {e}")

    finally:
        db_session.close()


async def refresh_all_cache():
    db_session = SessionLocal()
    try:
        all_class_names = [r[0] for r in db_session.query(Group.class_name).distinct().all()]
    finally:
        db_session.close()

    # Async har bir guruh uchun
    await asyncio.gather(*(fetch_and_update_cache(c) for c in all_class_names))


def schedule_daily_notifications():
    db_session = SessionLocal()
    try:
        all_class_names = [r[0] for r in db_session.query(Group.class_name).distinct().all()]
    finally:
        db_session.close()

    today = datetime.now().strftime('%Y-%m-%d')
    for lesson in LESSON_TIMES:
        start_time = datetime.strptime(lesson['start'], "%H:%M")
        reminder_time = start_time - timedelta(minutes=REMINDER_OFFSET_MINUTES)
        for class_name in all_class_names:
            job_id = f"reminder_{class_name}_{lesson['para']}_{today}"
            scheduler.add_job(
                send_lesson_reminder,
                'cron',
                hour=reminder_time.hour,
                minute=reminder_time.minute,
                args=[class_name, lesson['para']],
                id=job_id,
                misfire_grace_time=60,
                max_instances=1
            )
            print(f"{class_name} {lesson['para']}-para eslatma soat {reminder_time.hour:02d}:{reminder_time.minute:02d} qo‘shildi.")


def start_scheduler():
    # AsyncIOScheduler ishga tushirish
    scheduler.add_job(refresh_all_cache, 'cron', hour=7, minute=0)
    scheduler.add_job(schedule_daily_notifications, 'cron', hour=7, minute=1)
    scheduler.start()
    print("✅ Async scheduler ishga tushirildi.")


if __name__ == "__main__":
    start_scheduler()
    asyncio.get_event_loop().run_forever()
