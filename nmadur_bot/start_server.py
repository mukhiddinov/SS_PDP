import os
import asyncio
from fastapi import FastAPI
import uvicorn
from main import application, refresh_all_cache, start_bot_services

app = FastAPI()

# Health check endpoint
@app.get("/")
async def read_root():
    return {"status": "ok"}

# Botni background-da ishga tushirish
async def start_bot():
    print("⏳ Bot ishga tushmoqda...")
    await application.initialize()
    await application.start()
    
    # Keshni dastlabki yangilash (optional)
    await refresh_all_cache()
    print("✅ Kesh yangilandi.")

    # Scheduler ishga tushadi
    start_bot_services()
    
    # Polling ishga tushadi
    await application.run_polling()
    print("🤖 Bot ishga tushdi va polling ishlayapti.")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
