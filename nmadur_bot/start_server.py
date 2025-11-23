import os
import asyncio
from fastapi import FastAPI
import uvicorn
from main import application

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok"}

asyncio.create_task(application.run_polling())

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
