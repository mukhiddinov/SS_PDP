# schedule_updater.py

import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp

from models import get_db, User, Group, Spreadsheet, ScheduleCache

application = None  # bu main.py dan beriladi
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
lock = asyncio.Lock()

async def fetch_and_update_cache(class_name: str):
    async with lock:
        with get_db() as db:
            group = db.query(Group).filter(Group.class_name == class_name).first()
            if not group:
                print(f"Guruh topilmadi: {class_name}")
                return
            spreadsheet_info = db.query(Spreadsheet).filter(Spreadsheet.degree == group.degree).first()
            if not spreadsheet_info:
                print(f"Spreadsheet ma'lumoti topilmadi: {group.degree}-kurs")
                return
            try:
                spreadsheet_id = spreadsheet_info.url.split('/')[5]
                sheet_name = spreadsheet_info.sheet_name or ""
            except IndexError:
                print(f"Noto'g'ri URL formati: {spreadsheet_info.url}")
                return

            day_name = datetime.now().strftime('%A')
            payload = {
                "spreadsheet_id": spreadsheet_id,
                "sheet_name": sheet_name,
                "class_name": class_name,
                "day_name": day_name
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request("GET", "https://ss-pdp-api.onrender.com/schedule/", json=payload) as resp:
                        if resp.status != 200:
                            print(f"API so'rovi xato ({resp.status})")
                            return
                        schedule_data = await resp.json()
            except Exception as e:
                print(f"API fetch error ({class_name}): {e}")
                return

            cache_entry = db.query(ScheduleCache).filter(ScheduleCache.class_name == class_name).first()
            if cache_entry:
                cache_entry.data = schedule_data
            else:
                cache_entry = ScheduleCache(class_name=class_name, data=schedule_data)
                db.add(cache_entry)
            db.commit()
            print(f"Kesh yangilandi: {class_name} uchun {day_name}")

async def refresh_all_cache():
    with get_db() as db:
        class_names = [r[0] for r in db.query(Group.class_name).distinct().all()]
    await asyncio.gather(*(fetch_and_update_cache(c) for c in class_names))

async def send_lesson_reminder(class_name: str, para_number: int):
    if not application:
        return
    with get_db() as db:
        cache_entry = db.query(ScheduleCache).filter(ScheduleCache.class_name == class_name).first()
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
        user_chat_ids = db.query(User.chat_id).filter(User.class_name == class_name).all()
        for (chat_id,) in user_chat_ids:
            try:
                await application.bot.send_message(chat_id=chat_id, text=reminder_text, parse_mode='Markdown')
            except Exception as e:
                print(f"Eslatma yuborishda xato ({chat_id}): {e}")

def schedule_daily_notifications():
    with get_db() as db:
        class_names = [r[0] for r in db.query(Group.class_name).distinct().all()]
    today = datetime.now().strftime('%Y-%m-%d')
    for lesson in LESSON_TIMES:
        start_time = datetime.strptime(lesson['start'], "%H:%M")
        reminder_time = start_time - timedelta(minutes=REMINDER_OFFSET_MINUTES)
        for class_name in class_names:
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

def start_scheduler():
    # Har kuni ertalab 7:00 da keshni yangilash
    scheduler.add_job(lambda: asyncio.create_task(refresh_all_cache()), 'cron', hour=7, minute=0)
    # Har kuni 7:01 da bugungi eslatmalarni rejalashtirish
    scheduler.add_job(schedule_daily_notifications, 'cron', hour=7, minute=1)
    scheduler.start()
    print("✅ Scheduler ishga tushirildi")
