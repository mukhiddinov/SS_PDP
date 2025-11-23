import os
import asyncio
from fastapi import FastAPI
import uvicorn
from main import application, refresh_all_cache  # main.py dan

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok"}

async def start_bot():
    await application.initialize()
    await application.start()
    await refresh_all_cache()  # optional: keshni dastlabki yangilash
    await application.run_polling()
    print("Bot polling started.")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
