import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import uvicorn

# --- CONFIGURACIÓN ---
TOKEN = os.getenv("TELEGRAM_TOKEN", "8227761535:AAFIGpUjlLAoSR71eiwxsfS6Cun2uDukTTM")
GROUP_ID = "@OmniRadar_trade"

# Inicialización de FastAPI y Aiogram
app = FastAPI()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Modelo de datos para la API
class TelegramMessage(BaseModel):
    message: str

# --- ENDPOINT API ---
@app.post("/api/telegram")
async def send_to_telegram(payload: TelegramMessage):
    """
    Recibe un JSON: {"message": "Tu texto aquí"}
    y lo envía al grupo de Telegram definido.
    """
    try:
        # Formateo estilo consola para mantener la estética del sistema
        formatted_text = f"```\n📡 DATA_INCOMING\n----------------\n{payload.message}\n```"
        
        await bot.send_message(chat_id=GROUP_ID, text=formatted_text)
        return {"status": "success", "sent": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando a Telegram: {str(e)}")

# --- CICLO DE VIDA ---
@app.on_event("startup")
async def startup_event():
    # Esto permite que el bot envíe un mensaje de "Sistemas Listos" al iniciar
    try:
        await bot.send_message(chat_id=GROUP_ID, text="✅ **API Gateway: Telegram Bridge Online**")
    except:
        print("Error al conectar con el grupo. Verifica que el bot sea administrador.")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Ejecuta el servidor en el puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)