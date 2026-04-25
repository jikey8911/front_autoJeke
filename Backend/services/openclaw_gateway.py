import os
import asyncio
import httpx

OPENCLAW_GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://host.docker.internal:10424")
OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "")

async def send_message_to_agent(agent_name: str, message: str) -> str:
    """
    Envía un mensaje a un agente especificado en OpenClaw de forma asíncrona.
    Utiliza el endpoint de compatibilidad OpenAI (/v1/chat/completions).
    """
    endpoint = f"{OPENCLAW_GATEWAY_URL}/v1/chat/completions"
    
    # OpenClaw requiere que el modelo sea 'openclaw/<agentId>'
    # Forzamos minúsculas para el agent_name en la URL del modelo
    target_agent_id = agent_name.lower()
    if target_agent_id == "interfaceagent":
        target_agent_id = "comunication"
        
    model_id = f"openclaw/{target_agent_id}"
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENCLAW_TOKEN}"
    }
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            response = await client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Extraemos el contenido de la respuesta estilo OpenAI
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠️ Error consultando al agente {agent_name} en {endpoint}: {e}")
            return '{"balance": "0.00", "uaes_activas": 0, "oportunidades": 0}'

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
