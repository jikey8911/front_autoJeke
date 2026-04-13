from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os

app = FastAPI()

# CORS — permite peticiones desde el frontend en puerto 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL del Plugin API HTTP de OpenClaw Gateway
OPENCLAW_API_URL = os.getenv("OPENCLAW_API_URL", "http://openclaw_instance:9001/api/v1/send")

class OpenClawRequest(BaseModel):
    content: str
    userId: str

async def send_to_openclaw(message: str, user_id: str = "automata_dashboard"):
    """
    Envía un mensaje al agente de OpenClaw usando la API REST (Unidireccional).
    """
    token = "6c7e7cefc776dd2bad574d8314ca6549b5bfa2b8b2bff403"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": message,
        "userId": user_id
    }
    
    print(f"[Backend] Enviando mensaje a OpenClaw API: {message}")
    try:
        # Usamos requests para hacer un HTTP POST simple
        response = requests.post(OPENCLAW_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"[Backend] Respuesta API OpenClaw: {data}")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"[Backend] Error en petición API: {e}")
        return {"error": "Fallo al comunicar con la API de OpenClaw", "details": str(e)}

@app.get("/test_ws")
async def test_ws_connection():
    """
    Test adaptado a la API HTTP.
    """
    return await send_to_openclaw("PING de prueba desde el Dashboard")

@app.get("/agents")
async def get_agents():
    """
    Solicita la lista de agentes por la API.
    Nota: El modo HTTP devuelve {"ok": true} y el agente responderá por Telegram.
    """
    return await send_to_openclaw("Por favor, dame la lista de agentes activos y su estado.")

@app.get("/opportunities")
async def get_opportunities():
    return await send_to_openclaw("Por favor, dame la lista de oportunidades.")

@app.get("/running_tasks")
async def get_running_tasks():
    return await send_to_openclaw("Por favor, dame la lista de tareas en ejecucion.")

@app.get("/balance")
async def get_balance():
    return await send_to_openclaw("Por favor, dame el balance global.")

@app.get("/status")
async def get_status():
    return await send_to_openclaw("Por favor, dame el estado del sistema.")

@app.get("/mitosis")
async def get_mitosis():
    return await send_to_openclaw("Informacion de mitosis.")

@app.get("/kill")
async def get_kill():
    return await send_to_openclaw("Informacion de grupos eliminados.")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000, reload=True)
