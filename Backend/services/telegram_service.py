import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ⚙️ Configuración
TOKEN = os.getenv("TELEGRAM_TOKEN", "8227761535:AAFIGpUjlLAoSR71eiwxsfS6Cun2uDukTTM")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# 🎯 Handler /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"🤖 ¡Hola {message.from_user.first_name}! Soy OmniRadarAI.\n\n"
        f"✅ Sistemas en línea (BI OS v3.0).\n"
        f"📡 Esperando comandos de Control de Misión..."
    )

# 🎯 Handler /status (Ejemplo de integración con el OS)
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
    await bot.delete_webhook(drop_pending_updates=True) 
    await dp.start_polling(bot)
