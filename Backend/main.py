import os
from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager
import asyncio
from services.telegram_service import dp, bot, start_telegram_bot
from services.openclaw_gateway import start_openclaw_gateway
from services.api_service import router as api_all_router
# --- LIFESPAN PARA MANEJAR TAREAS EN BACKGROUND ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar el bot de Telegram en segundo plano al arrancar FastAPI
    print("🚀 Levantando servicio de Telegram (Aiogram)...")
    bg_task_tg = asyncio.create_task(start_telegram_bot())
    print("🚀 Levantando servicio de OpenClaw Gateway...")
    bg_task_oc = asyncio.create_task(start_openclaw_gateway())
    yield
    # Limpieza al apagar
    bg_task_tg.cancel()
    bg_task_oc.cancel()
    await bot.session.close()
    print("🛑 Servicios apagados.")

app = FastAPI(title="BI OS Backend", lifespan=lifespan)
api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "ok", "service": "BI_OS_Backend", "telegram_bridge": "active"}

app.include_router(api_router, prefix="/api")
app.include_router(api_all_router, prefix="/api")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
