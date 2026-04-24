import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# --- CONFIGURACIÓN ---
TOKEN = "8227761535:AAFIGpUjlLAoSR71eiwxsfS6Cun2uDukTTM"
GROUP_ID = -1003928165700 

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
telegram_router = APIRouter()

class TelegramMessage(BaseModel):
    message: str

# --- ENDPOINT (Como Router) ---
@telegram_router.post("/telegram")
async def send_to_telegram(payload: TelegramMessage):
    try:
        formatted_text = f"```\n📡 DATA_INCOMING\n----------------\n{payload.message}\n```"
        await bot.send_message(chat_id=GROUP_ID, text=formatted_text)
        return {"status": "success", "sent": True}
    except Exception as e:
        print(f"❌ Telegram Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- LA FUNCIÓN QUE FALTABA ---
async def start_telegram_bot():
    """
    Función de inicialización llamada por el startup de FastAPI.
    """
    try:
        await bot.send_message(chat_id=GROUP_ID, text="✅ **BI OS v3.0: Telegram Bridge Online**")
        print("🚀 [Services] Telegram Bridge conectado.")
    except Exception as e:
        print(f"⚠️ [Services] No se pudo enviar mensaje inicial: {e}")