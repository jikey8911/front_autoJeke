from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import json

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración del Gateway (Inyectada por Docker-Compose)
TOKEN = os.getenv("OPENCLAW_TOKEN", "8941487567606a620353868ebbcd32f73ba9b26de1551c09")
GATEWAY_BASE = os.getenv("OPENCLAW_GATEWAY_URL", "http://openclaw_instance:10424")
OPENCLAW_API_BASE = f"{GATEWAY_BASE}/v1"

def query_openclaw_api(endpoint: str, method: str = "GET", payload: dict = None):
    url = f"{OPENCLAW_API_BASE}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        else:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[Backend] Error en API {endpoint}: {e}")
        return {"error": f"Fallo en API OpenClaw ({endpoint})", "details": str(e)}

@app.get("/test_ws")
async def test_ws_connection():
    """Adaptado para probar la API HTTP nativa"""
    return query_openclaw_api("models")

@app.get("/agents")
async def get_agents():
    # En la API v1 nativa, listamos los agentes
    return query_openclaw_api("agents")

@app.get("/status")
async def get_status():
    return query_openclaw_api("status")

@app.get("/opportunities")
async def get_opportunities():
    # Simula un chat para obtener información específica si no hay endpoint directo
    payload = {
        "model": "openclaw/default",
        "messages": [{"role": "user", "content": "Dame la lista de oportunidades de oportunidades.md en formato JSON."}]
    }
    return query_openclaw_api("chat/completions", "POST", payload)

@app.get("/running_tasks")
async def get_running_tasks():
    return query_openclaw_api("sessions")

@app.get("/balance")
async def get_balance():
    return query_openclaw_api("usage/status")

@app.get("/mitosis")
async def get_mitosis():
    return {"status": "success", "info": "Endpoint en desarrollo para API v1"}

@app.get("/kill")
async def get_kill():
    return {"status": "success", "info": "Endpoint en desarrollo para API v1"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000, reload=True)
