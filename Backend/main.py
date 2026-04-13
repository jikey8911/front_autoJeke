from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import websockets
import asyncio
import json
import os

app = FastAPI()

# CORS — permite peticiones desde el frontend en puerto 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ajustado temporalmente a * para evitar bloqueos en dev, idealmente "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URL del WebSockets de OpenClaw Gateway
# En Docker-compose definimos host 'openclaw_instance', pero depende de tu red externa
OPENCLAW_WS_URL = os.getenv("OPENCLAW_WS_URL", "ws://172.21.0.3:10424")

class OpenClawRequest(BaseModel):
    data_needed: str
    format_expected: str

async def query_openclaw_ws(data_needed: str, format_expected: str):
    """
    Función helper para abrir conexión WebSocket, enviar la petición a OpenClaw,
    esperar la respuesta, cerrarla y retornarla.
    """
    payload = {
        "action": "request_info", # o la acción que acepte el WS de OpenClaw
        "data_needed": data_needed,
        "format_expected": format_expected
    }
    
    try:
        # Timeout extendido a 60s: El agente IA puede tomar tiempo en leer archivos y formular la respuesta JSON
        async with websockets.connect(OPENCLAW_WS_URL) as websocket:
            await websocket.send(json.dumps(payload))
            response_str = await asyncio.wait_for(websocket.recv(), timeout=60.0)
            
            try:
                return json.loads(response_str)
            except json.JSONDecodeError:
                return {"raw_response": response_str}
                
    except asyncio.TimeoutError:
         return {"error": f"Timeout: El agente en OpenClaw no respondió a la solicitud de '{data_needed}' en 60 segundos."}
    except Exception as e:
        print(f"Error WS: {e}")
        return {"error": f"Fallo de comunicación WS: {e}"}

@app.get("/test_ws")
async def test_ws_connection():
    """
    Endpoint de prueba para confirmar si el backend puede alcanzar y conectar
    con el WebSocket de OpenClaw. No pide datos, solo prueba el handshake.
    """
    try:
        # Solo intenta abrir y cerrar la conexión
        async with websockets.connect(OPENCLAW_WS_URL, close_timeout=2) as websocket:
            return {
                "status": "success",
                "message": "Conexión WebSocket a OpenClaw exitosa.",
                "url_tested": OPENCLAW_WS_URL
            }
    except Exception as e:
        return {
            "status": "error",
            "message": "Fallo al conectar con el WebSocket de OpenClaw.",
            "url_tested": OPENCLAW_WS_URL,
            "details": str(e)
        }

@app.get("/agents")
async def get_agents():
    """
    Obtiene la lista de agentes y sus características.
    """
    print("[Backend] Recibida petición en /agents. Iniciando consulta a OpenClaw WS...")
    response = await query_openclaw_ws(data_needed="agents", format_expected="json")
    print(f"[Backend] Respuesta WS obtenida para /agents: {response}")
    return response

@app.get("/opportunities")
async def get_opportunities():
    """
    Obtiene la lista de oportunidades encontradas.
    """
    return await query_openclaw_ws(data_needed="opportunities", format_expected="json")

@app.get("/running_tasks")
async def get_running_tasks():
    """
    Obtiene las tareas que se están ejecutando y por qué agentes.
    """
    return await query_openclaw_ws(data_needed="running_tasks", format_expected="json")

@app.get("/balance")
async def get_balance():
    """
    Obtiene el balance del broker.
    """
    return await query_openclaw_ws(data_needed="balance", format_expected="json")

@app.get("/status")
async def get_status():
    """
    Obtiene el estado global del sistema.
    """
    return await query_openclaw_ws(data_needed="status", format_expected="json")

@app.get("/mitosis")
async def get_mitosis():
    """
    Obtiene cuántos grupos se han duplicado.
    """
    return await query_openclaw_ws(data_needed="mitosis", format_expected="json")

@app.get("/kill")
async def get_kill():
    """
    Obtiene cuántos grupos han muerto.
    """
    return await query_openclaw_ws(data_needed="kill", format_expected="json")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000, reload=True)