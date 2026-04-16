from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import glob

app = FastAPI(title="Automata Platform Backend")

# URL del Gateway para comunicación dentro de la red de contenedores
GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://172.21.0.1:10424")
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
    # En el contenedor, el volumen está montado en /workspace
    global_balance = 0.0
    try:
        with open("/workspace/LOGS/finanzas_globales.json", "r") as f:
            d = json.load(f)
            global_balance = d.get("balance_actual", 0.0)
    except Exception:
        pass

    oportunidades_count = 0
    try:
        with open("/workspace/STACKS/oportunidades.md", "r") as f:
            content = f.read()
            oportunidades_count = content.count("Oportunidad Detectada")
    except Exception:
        pass

    uaes_dirs = glob.glob("/workspace/UAEs/UAE_*")
    uaes_count = len(uaes_dirs)
    
    uae_list_json = []
    for uae_path in uaes_dirs:
        uae_id = os.path.basename(uae_path)
        uae_list_json.append({"id": uae_id, "balance": 0.0})

    fallback_data = {
        "estado_sistema": "Activo",
        "estado_gateway": "Ok",
        "balance": {"global": global_balance, "uaes": uae_list_json},
        "agentes_globales": ["CEO Global", "BROKER Global", "RESEARCHER Global", "INTERFACEAGENT"],
        "uaes": {"activas": uaes_count, "inactivas": 0, "duplicadas": 0, "muertas": 0},
        "oportunidades_globales": oportunidades_count
    }

    payload = {
        "model": "openclaw",
        "messages": [
            {
                "role": "system", 
                "content": f"Eres el InterfaceAgent. Telemetría real: BALANCE: {global_balance} UAEs: {uaes_count}"
            },
            {
                "role": "user", 
                "content": f"Genera un reporte JSON basado en esto: {json.dumps(fallback_data)}"
            }
        ],
        "response_format": { "type": "json_object" }
    }
    
    res = await query_openclaw_api("chat/completions", "POST", payload)
    
    if res and "choices" in res:
        try:
            content = res["choices"][0]["message"]["content"].strip()
            return json.loads(content)
        except Exception:
            pass
    
    return fallback_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000)
