import os
import asyncio
import httpx

OPENCLAW_GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://host.docker.internal:10424")
OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "")

async def send_message_to_agent(agent_name: str, message: str) -> str:
    """
    Envía un mensaje a un agente especificado en OpenClaw de forma asíncrona.
    """
    # IMPORTANTE: Reemplaza "/api/v1/chat" con la ruta asíncrona real que maneje las peticiones hacia tu Gateway
    endpoint = f"{OPENCLAW_GATEWAY_URL}/api/v1/chat"
    
    payload = {
        "agent": agent_name, # O la convención de llaves que use tu OpenClaw API
        "prompt": message
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENCLAW_TOKEN}"
    }
    
    # Timeout largo (60s) porque los agentes de IA pueden demorar generando la respuesta asíncrona
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            # Asumimos que la respuesta del agente viene anidada en data["response"] o data["text"]
            data = response.json()
            return data.get("response", data.get("text", "{}"))
        except Exception as e:
            print(f"⚠️ Error consultando al agente {agent_name}: {e}")
            # Mock / Fallback temporal en caso de que falle la petición o la IP sea inalcanzable
            return '{"balance": "Mock $0.00", "uaes_activas": 0, "oportunidades": 0}'

async def start_openclaw_gateway():
    """
    Inicia la conexión y/o puente con OpenClaw.
    """
    print(f"🔗 Inicializando pasarela OpenClaw hacia {OPENCLAW_GATEWAY_URL}...")
    try:
        while True:
            await asyncio.sleep(60)
            
    except asyncio.CancelledError:
        print("🛑 Pasarela OpenClaw detenida correctamente.")
    except Exception as e:
        print(f"⚠️ Error crítico en OpenClaw Gateway: {e}")
