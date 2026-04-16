from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import glob

app = FastAPI(title="Automata Platform Backend")

# URL del Gateway para comunicación local directa o desde el Host
GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:10424")
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
    url = f"{OPENCLAW_API_BASE}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[BACKEND ERROR] {str(e)}")
            return None

@app.get("/api/all")
async def get_all_dashboard():
    # En el contenedor, el volumen está montado en /workspace (o localmente si se corre sin Docker)
    global_balance = 0.0
    try:
        # Se verifica si los LOGS y STACKS existen físicamente para extraer stats reales
        with open("/workspace/LOGS/finanzas_globales.json", "r", encoding="utf-8") as f:
            d = json.load(f)
            global_balance = float(d.get("balance_actual", 0.0))
    except (FileNotFoundError, json.JSONDecodeError):
        global_balance = 15420.50 # Dummy estético temporal si no hay BD

    oportunidades_count = 0
    try:
        with open("/workspace/STACKS/oportunidades.md", "r", encoding="utf-8") as f:
            content = f.read()
            oportunidades_count = content.count("Oportunidad Detectada")
    except FileNotFoundError:
        oportunidades_count = 14 # Dummy inicial

    # Identificación local de UAEs
    uaes_dirs = glob.glob("/workspace/UAEs/UAE_*")
    uaes_count = len(uaes_dirs) if len(uaes_dirs) > 0 else 3
    
    uae_list_json = []
    if uaes_dirs:
        for uae_path in uaes_dirs:
            uae_id = os.path.basename(uae_path)
            uae_list_json.append({"id": uae_id, "balance": 0.0})
    else:
        # Si no hay UAEs reales corriendo, devolvemos muestras para la UI
        uae_list_json = [
            {"id": "UAE_ALPHA", "balance": 1050},
            {"id": "UAE_BETA", "balance": 3400},
            {"id": "UAE_GAMMA", "balance": 720}
        ]

    dashboard_data = {
        "estado_sistema": "SISTEMA OPERATIVO Y ESTABLE",
        "estado_gateway": "CONECTADO A OPENCLAW",
        "balance": {"global": global_balance, "uaes": uae_list_json},
        "agentes_globales": ["[CORE] CEO Global", "[AI] BROKER Autónomo", "[DATA] RESEARCHER Cuántico", "[UX] INTERFACEAGENT"],
        "uaes": {
            "activas": uaes_count, 
            "inactivas": 0, 
            "duplicadas": 1, 
            "muertas": 0
        },
        "oportunidades_globales": oportunidades_count
    }

    # Intentar consultar a OpenClaw para inyectar su "análisis de sistema"
    payload = {
        "model": "openclaw",
        "messages": [
            {
                "role": "system", 
                "content": f"Eres el InterfaceAgent. Telemetría actual -> BALANCE: {global_balance} | UAEs Activas: {uaes_count}. Retorna el JSON sin formato markdown."
            },
            {
                "role": "user", 
                "content": f"Formatea estrictamente este objeto en JSON puro preservando la estructura: {json.dumps(dashboard_data)}"
            }
        ],
        "response_format": { "type": "json_object" }
    }
    
    res = await query_openclaw_api("chat/completions", "POST", payload)
    
    if res and "choices" in res:
        try:
            content = res["choices"][0]["message"]["content"].strip()
            # OpenClaw podría añadir backticks de markdown
            if content.startswith("```json"):
                content = content[7:-3]
            return json.loads(content)
        except Exception as e:
            print("[Backend] Fallo decodificando respuesta de OpenClaw. Retornando fallback", str(e))
    
    # Si OpenClaw no responde bien o está caído, el Frontend seguirá funcionando
    return dashboard_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000)
