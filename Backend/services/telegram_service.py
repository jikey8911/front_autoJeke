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
USER_ID_PERSONAL = 8591803663

# 1. Instancias necesarias para exportar
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()
telegram_router = APIRouter()

class TelegramMessage(BaseModel):
    message: str

# 2. Router para el endpoint de la API
@telegram_router.post("/")
async def send_to_telegram(payload: TelegramMessage):
    try:
        # El bloque de código ``` protege el contenido de errores de parsing de Markdown
        formatted_text = f"```\n📡 DATA_INCOMING\n----------------\n{payload.message}\n```"
        await bot.send_message(chat_id=GROUP_ID, text=formatted_text)
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Error en API Telegram: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3. Función principal para el Background Task en main.py
async def start_telegram_bot():
    """Inicia el bot y envía notificaciones de activación"""
    
    # Configurar el menú de comandos para que aparezca el botón [/] en tu chat
    await bot.set_my_commands([
        BotCommand(command="start", description="Reiniciar conexión"),
        BotCommand(command="status", description="Estado del BI OS v3.0")
    ])

    try:
        # Notificación al grupo
        await bot.send_message(
            chat_id=GROUP_ID, 
            text="🚀 **Sistemas OmniRadar Online**\nBridge establecido con el Backend."
        )
        
        # Notificación Directa Personal
        await bot.send_message(
            chat_id=USER_ID_PERSONAL, 
            text="✨ **Hola, activo.**\nEl backend de BI OS v3.0 se ha iniciado correctamente."
        )
        
        print("✅ [Telegram] Saludos de inicio enviados exitosamente.")
    except Exception as e:
        print(f"⚠️ [Telegram] Error en saludo inicial (¿Iniciaste el chat con el bot?): {e}")

    # Limpiar actualizaciones pendientes y arrancar escucha
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)