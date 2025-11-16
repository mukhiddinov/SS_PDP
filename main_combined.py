import asyncio
import uvicorn
from nmadur_api import app as fastapi_app
from main import application   # bot app

async def run_bot():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

async def run_api():
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

async def main():
    await asyncio.gather(
        run_bot(),
        run_api()
    )

if __name__ == "__main__":
    asyncio.run(main())
