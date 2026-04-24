import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# --- CONFIGURACIÓN ---
TOKEN = "8227761535:AAFIGpUjlLAoSR71eiwxsfS6Cun2uDukTTM"
GROUP_ID = -1003928165700 

# 1. Instancias necesarias para exportar
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
telegram_router = APIRouter()

class TelegramMessage(BaseModel):
    message: str

# 2. Router para el endpoint de la API
@telegram_router.post("/") # El prefijo /api/telegram se pone en main.py
async def send_to_telegram(payload: TelegramMessage):
    try:
        formatted_text = f"```\n📡 DATA_INCOMING\n----------------\n{payload.message}\n```"
        await bot.send_message(chat_id=GROUP_ID, text=formatted_text)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. La función que main.py espera para el background task
async def start_telegram_bot():
    """
    Se encarga de configurar el bot y arrancar el polling.
    """
    # Configurar menú de comandos
    await bot.set_my_commands([
        BotCommand(command="start", description="Iniciar conexión"),
        BotCommand(command="status", description="Ver estado BI OS")
    ])
    
    # Mensaje de inicio en el grupo
    try:
        await bot.send_message(chat_id=GROUP_ID, text="🚀 **BI OS v3.0: Telegram Bridge Online**")
    except Exception as e:
        print(f"⚠️ Error inicial de Telegram: {e}")

    # Arrancar el polling (escucha de mensajes)
    # Importante: drop_pending_updates evita que el bot responda mensajes viejos al arrancar
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)