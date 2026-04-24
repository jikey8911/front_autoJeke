import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import uvicorn

# --- CONFIGURACIÓN ---
TOKEN = "8227761535:AAFIGpUjlLAoSR71eiwxsfS6Cun2uDukTTM"
# IMPORTANTE: El ID de grupo debe ser un entero (int) para evitar errores de parseo
GROUP_ID = -1003928165700 

app = FastAPI(title="OmniRadar Telegram Bridge")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

class TelegramMessage(BaseModel):
    message: str

# --- ENDPOINT API ---
@app.post("/api/telegram")
async def send_to_telegram(payload: TelegramMessage):
    try:
        # Estética de consola para el BI OS v3.0
        formatted_text = (
            f"```\n"
            f"📡 DATA_INCOMING\n"
            f"----------------\n"
            f"{payload.message}\n"
            f"```"
        )
        
        await bot.send_message(chat_id=GROUP_ID, text=formatted_text)
        return {"status": "success", "sent": True}
    except Exception as e:
        # Captura el error real de Telegram para debug
        print(f"❌ Telegram Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# --- CICLO DE VIDA ---
@app.on_event("startup")
async def startup_event():
    try:
        await bot.send_message(chat_id=GROUP_ID, text="✅ **API Gateway: Telegram Bridge Online**")
        print("🚀 Conexión con Telegram establecida exitosamente.")
    except Exception as e:
        print(f"⚠️ Alerta de inicio: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    # Limpieza: cerrar la sesión del bot al apagar el servidor
    await bot.session.close()
    print("🛑 Servidor apagado y sesión de Telegram cerrada.")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Host 0.0.0.0 para que sea accesible desde otros contenedores o UAEs
    uvicorn.run(app, host="0.0.0.0", port=8000)