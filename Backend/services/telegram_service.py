import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import APIRouter
from pydantic import BaseModel

# ⚙️ Configuración
TOKEN = os.getenv("TELEGRAM_TOKEN", "8227761535:AAFIGpUjlLAoSR71eiwxsfS6Cun2uDukTTM")
OMNIRADAR_GROUP_ID = -1003928165700 # ID del grupo Trade_Signals_OmniRadar

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# --- RUTAS API PARA ENVIAR MENSAJES DESDE OTRAS UAEs ---
telegram_router = APIRouter()

class SignalPayload(BaseModel):
    text: str

@telegram_router.post("/signal")
async def send_signal_to_group(payload: SignalPayload):
    """
    Endpoint para que la UAE_01 envíe señales.
    El Backend recibe el POST y el Bot de Telegram lo publica en el grupo.
    """
    try:
        await bot.send_message(chat_id=OMNIRADAR_GROUP_ID, text=payload.text)
        return {"status": "success", "message": "Señal enviada al grupo OmniRadar"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 🎯 Handlers de Comandos Directos
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"🤖 ¡Hola {message.from_user.first_name}! Soy OmniRadarAI.\n\n"
        f"✅ Sistemas en línea (BI OS v3.0).\n"
        f"📡 Control de Misión establecido."
    )

@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    try:
        with open("/root/.openclaw/workspace/global/balances.md", "r") as f:
            status_text = f.read()
        await message.answer(f"📊 **Estado del Sistema:**\n\n{status_text}")
    except:
        await message.answer("⚠️ No se pudo leer el archivo de balances.")

# 🔄 Bucle principal de ejecución
async def start_telegram_bot():
    print("✅ [OmniRadarAI] Bot interactivo iniciado (Aiogram Polling)...")
    
    # FORZAR CONFIGURACIÓN DEL MENÚ DIRECTAMENTE DESDE EL BACKEND
    from aiogram.types import BotCommand
    await bot.set_my_commands([
        BotCommand(command="start", description="Iniciar conexión OmniRadar"),
        BotCommand(command="status", description="Ver estado del BI OS")
    ])
    print("✅ Menú de Telegram configurado exitosamente.")

    # Enviar mensaje de inicio de sesión al grupo
    try:
        startup_msg = "🚀 **SISTEMA OMNIRADAR ONLINE**\n\n✅ Conexión con el BI OS v3.0 establecida desde el Backend Central.\n📡 Esperando señales de la UAE_01..."
        await bot.send_message(chat_id=OMNIRADAR_GROUP_ID, text=startup_msg)
        print("✅ Mensaje de inicio enviado al grupo.")
    except Exception as e:
        print(f"⚠️ Error enviando mensaje al grupo: {e}")

    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)
