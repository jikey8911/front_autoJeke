from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json

app = FastAPI(title="Automata Platform Backend")

# --- CONFIGURACIÓN DE ENTORNO ---
GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://openclaw_instance:10424")
TOKEN = os.getenv("OPENCLAW_TOKEN", "8941487567606a620353868ebbcd32f73ba9b26de1551c09")
OPENCLAW_API_BASE = f"{GATEWAY_URL}/v1"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def query_openclaw_api(endpoint: str, method: str = "GET", payload: dict = None):
    """Orquestador ASÍNCRONO de peticiones a OpenClaw v1 API"""
    url = f"{OPENCLAW_API_BASE}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            print(f"[ASYNCHRONOUS-REQ] {method} a {url}")
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            else:
                response = await client.post(url, headers=headers, json=payload, timeout=60.0)

            response.raise_for_status()
            data = response.json()
            print(f"[GATEWAY-RESPONSE] {endpoint}: {json.dumps(data, indent=2)}")
            return data
        except Exception as e:
            print(f"[ERROR-GATEWAY] Fallo en {endpoint}: {str(e)}")
            return {
                "error": "GATEWAY_UNREACHABLE",
                "details": str(e),
                "endpoint": endpoint
            }

@app.get("/test_ws") # Mantenemos este nombre para compatibilidad con el frontend actual
@app.get("/health")
async def health_check():
    """Verifica la conectividad básica con el Gateway"""
    return query_openclaw_api("models")

@app.get("/agents")
async def get_agents():
    """Lista de agentes activos en el sistema"""
    return query_openclaw_api("agents")

@app.get("/status")
async def get_status():
    """Estado de salud del Gateway y sus canales"""
    return query_openclaw_api("status")

@app.get("/opportunities")
async def get_opportunities():
    """
    Extracción de datos desde el sistema de archivos de OpenClaw.
    Utiliza el modelo default para procesar el archivo local.
    """
    payload = {
        "model": "openclaw/default",
        "messages": [
            {"role": "system", "content": "Eres un extractor de datos JSON."},
            {"role": "user", "content": "Analiza oportunidades.md y devuelve un JSON con las oportunidades detectadas."}
        ],
        "response_format": { "type": "json_object" }
    }
    return query_openclaw_api("chat/completions", "POST", payload)

@app.get("/running_tasks")
async def get_running_tasks():
    """Sesiones de agentes en ejecución"""
    return query_openclaw_api("sessions")

@app.get("/balance")
async def get_balance():
    """Uso de tokens y balance del sistema"""
    return query_openclaw_api("usage/status")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000, reload=True)
