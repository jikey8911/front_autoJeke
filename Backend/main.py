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
# Usamos el nombre DNS del contenedor en lugar de la IP, ya que la IP cambia en cada reinicio de Docker
OPENCLAW_WS_URL = os.getenv("OPENCLAW_WS_URL", "ws://openclaw_instance:10424")

class OpenClawRequest(BaseModel):
    data_needed: str
    format_expected: str

async def query_openclaw_ws(data_needed: str, format_expected: str):
    """
    Función helper para abrir conexión WebSocket, enviar la petición a OpenClaw,
    esperar la respuesta, cerrarla y retornarla.
    """
    token = "6c7e7cefc776dd2bad574d8314ca6549b5bfa2b8b2bff403"
    
    try:
        headers = {
            "User-Agent": "Automata-Backend/1.0",
            "Origin": "http://127.0.0.1:8080", # Uno de los allowedOrigins en openclaw.json
            "Authorization": f"Bearer {token}"
        }
        async with websockets.connect(OPENCLAW_WS_URL, extra_headers=headers) as websocket:
            # 1. Esperar el mensaje de bienvenida/challenge de OpenClaw
            welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"[Backend] Recibido saludo de OpenClaw: {welcome_msg}")
            
            welcome_json = json.loads(welcome_msg)
            nonce = welcome_json.get("payload", {}).get("nonce", "")
            
            # 2. Construir el Handshake v3 de OpenClaw
            connect_payload = {
                "type": "req",
                "id": "1",
                "method": "connect",
                "params": {
                    "minProtocol": 3,
                    "maxProtocol": 3,
                    "client": {
                        "id": "cli", # OpenClaw solo acepta clientes oficiales ("cli", "ios", etc.)
                        "version": "1.2.3",
                        "platform": "linux",
                        "mode": "standalone" # El CLI suele correr en modo standalone o daemon
                    },
                    "role": "operator",
                    "scopes": ["operator.read", "operator.admin"],
                    "caps": [],
                    "commands": [],
                    "permissions": {},
                    "auth": { "token": token },
                    "locale": "en-US",
                    "userAgent": "openclaw-cli/1.2.3", # Mimics the official CLI
                    "device": {
                        "id": "automata_backend_fingerprint",
                        "publicKey": "dummy_pk",
                        "signature": "dummy_sig",
                        "signedAt": 1737264000000,
                        "nonce": nonce
                    }
                }
            }
            
            await websocket.send(json.dumps(connect_payload))
            print(f"[Backend] Handshake enviado con nonce: {nonce}")

            # 3. Esperar confirmación del Handshake
            auth_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"[Backend] Respuesta Handshake: {auth_response}")
            auth_json = json.loads(auth_response)
            
            if not auth_json.get("ok"):
                return {"error": "Handshake rechazado por OpenClaw", "details": auth_json}

            # 4. Ahora sí, enviar la petición de datos real usando métodos RPC de OpenClaw
            openclaw_method = "agents.list"
            if data_needed == "status": openclaw_method = "status"
            if data_needed == "balance": openclaw_method = "usage.cost"
            
            request_payload = {
                "type": "req",
                "id": "2",
                "method": openclaw_method,
                "params": {}
            }
            await websocket.send(json.dumps(request_payload))
            print(f"[Backend] Petición de datos enviada: {request_payload}")

            # 5. Esperar la respuesta real a nuestra petición
            response_str = await asyncio.wait_for(websocket.recv(), timeout=60.0)
            print(f"[Backend] Respuesta recibida: {response_str}")
            
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
    token = "6c7e7cefc776dd2bad574d8314ca6549b5bfa2b8b2bff403"
    url_with_token = f"{OPENCLAW_WS_URL}?token={token}"
    
    print(f"[Backend] Recibida petición en /test_ws. Probando conexión WS hacia {OPENCLAW_WS_URL}...")
    try:
        # Solo intenta abrir y cerrar la conexión
        async with websockets.connect(OPENCLAW_WS_URL, close_timeout=2) as websocket:
            welcome_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"[Backend] Conexión WS /test_ws EXITOSA. Challenge recibido: {welcome_msg}")
            print("[Backend] Conexión WS /test_ws EXITOSA.")
            return {
                "status": "success",
                "message": "Conexión WebSocket a OpenClaw exitosa.",
                "url_tested": OPENCLAW_WS_URL
            }
    except Exception as e:
        print(f"[Backend] Conexión WS /test_ws FALLIDA. Error: {e}")
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