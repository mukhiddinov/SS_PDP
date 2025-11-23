import os
import threading
from fastapi import FastAPI
import uvicorn
from main import main as start_bot

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

def run_bot_thread():
    # Bu yerda sening main() funksiyang botni to'liq ishga tushiradi
    start_bot()

if __name__ == "__main__":
    # Botni alohida threadda ishlatamiz
    t = threading.Thread(target=run_bot_thread, daemon=True)
    t.start()

    # Uvicorn server port ochib Renderga xizmat qiladi
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
