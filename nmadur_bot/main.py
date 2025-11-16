# main.py

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, error # error import qilindi
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Ichki fayllardan zarur funksiyalar va modellar importi ---
from models import SessionLocal, Group, User, ScheduleCache 
# start_scheduler va refresh_all_cache funksiyalari to'g'ri import qilinadi
from schedule_updater import start_scheduler, refresh_all_cache 


# --- Global Sozlamalar ---
BOT_TOKEN = "8232529091:AAEZwONkkio7Fbb-TT2-fbDsP_Txiw8MxQo" 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 👇👇👇 MUHIM O'ZGARTIRISH: Global Application obyektini yaratish 👇👇👇
# Bu obyekt schedule_updater.py ga import qilinadi va eslatmalar yuborish uchun ishlatiladi.
try:
    application = Application.builder().token(BOT_TOKEN).build()
    print("Application obyektini global yaratish muvaffaqiyatli.")
except Exception as e:
    logging.error(f"Application obyektini yaratishda xato: {e}")
    application = None # Xato bo'lsa, None bo'lsin

# --- Bot Funksiyalari (O'zgarishsiz) ---

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kurs (degree) tanlash tugmalarini yuboradi."""
    keyboard = [
        [InlineKeyboardButton("1-kurs", callback_data='degree_1')],
        [InlineKeyboardButton("2-kurs", callback_data='degree_2')],
        [InlineKeyboardButton("3-kurs", callback_data='degree_3')],
        [InlineKeyboardButton("4-kurs", callback_data='degree_4')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Assalomu alaykum! Iltimos, **kursni** tanlang:", reply_markup=reply_markup, parse_mode='Markdown')

# Inline tugmalarni qayta ishlash
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback so'rovlarini qayta ishlaydi (Kurs/Guruh tanlash)."""
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id
    db_session = SessionLocal()

    try:
        # --- Kurs (Degree) tanlangan ---
        if data.startswith('degree_'):
            degree = int(data.split('_')[1])
            groups = db_session.query(Group).filter(Group.degree == degree).all()
            
            if not groups:
                 await query.edit_message_text(f"⚠️ **{degree}-kurs** uchun ma'lumotlar bazasida guruh topilmadi. Ma'lumotlarni tekshiring.")
                 return
            
            keyboard = []
            for group in groups:
                keyboard.append([InlineKeyboardButton(group.class_name, callback_data=f'group_{group.class_name}')])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"✅ **{degree}-kurs** tanlandi. Endi **guruhingizni** tanlang:", reply_markup=reply_markup, parse_mode='Markdown')

        # --- Guruh (Class Name) tanlangan ---
        elif data.startswith('group_'):
            class_name = data.split('_')[1]
            
            # Users jadvalini yangilash/yaratish
            user = db_session.query(User).filter(User.chat_id == chat_id).first()
            if user:
                user.class_name = class_name
            else:
                user = User(chat_id=chat_id, class_name=class_name)
                db_session.add(user)
            db_session.commit()
            
            # Jadvalni ko'rsatish
            schedule_text = get_schedule_from_cache(db_session, class_name)
            
            await query.edit_message_text(f"🎉 **{class_name}** guruhi tanlandi. Bugungi dars jadvali:\n\n{schedule_text}", parse_mode='Markdown')

    except Exception as e:
        # DB huquqlari yoki boshqa kutilmagan xatolar
        logging.error(f"button_handler da xato: {e}")
        await query.edit_message_text("🚫 Kechirasiz, xatolik yuz berdi. Iltimos, /start bosing.")

    finally:
        db_session.close()

# --- Keshdan jadvalni olish funksiyasi (O'zgarishsiz) ---
def get_schedule_from_cache(session, class_name):
    """Keshdan jadval ma'lumotlarini formatlab oladi."""
    cache_entry = session.query(ScheduleCache).filter(ScheduleCache.class_name == class_name).first()
    
    if not cache_entry or not cache_entry.data:
        return "⚠️ Jadval keshda topilmadi. Kesh yangilanishini kuting (har kuni 7:00 da yangilanadi) yoki administratorga murojaat qiling."
    
    schedule_data = cache_entry.data
    day_name = datetime.now().strftime('%A')
    
    if not schedule_data or len(schedule_data) == 0:
        return f"Bugun, **{day_name}** kuni **{class_name}** guruhida dars yo'q."
        
    # Jadvalni Telegram uchun chiroyli formatlash
    output = [f"📅 **Bugungi jadval ({day_name})** uchun **{class_name}**:\n"]
    
    for item in schedule_data:
        # item.get() xato bermasligi uchun ishlatiladi
        output.append(
            f"🔸 **{item.get('para', 'N/A')}**-para: **{item.get('time', 'N/A')}**\n"
            f"📚 {item.get('subject', 'N/A')} ({item.get('room', 'N/A')})\n"
            f"👤 O'qituvchi: {item.get('teacher', 'N/A')}\n"
            "---"
        )
    
    return "\n".join(output)


# --- Asosiy Funksiya ---
def main() -> None:
    # Global 'application' obyekti yuqorida yaratilgan.
    if application is None:
        logging.error("Application obyekti yaratilmadi. Bot ishga tushirilmaydi.")
        return

    # 1. Scheduler ishga tushirish (Endi u eslatmalarni ham qo'shadi)
    start_scheduler() 
    
    # 2. Dastur ishga tushganda keshni birinchi marta yangilash (Qo'lda chaqiruv)
    print("⏳ Dastur ishga tushirilishi munosabati bilan kesh bir marta yangilanmoqda...")
    refresh_all_cache() 
    print("✅ Keshning dastlabki yangilanishi tugadi. Bot ishga tushirilmoqda...")
    
    # 3. Botni ishga tushirish
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
