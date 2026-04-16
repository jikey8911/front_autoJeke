from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import glob

app = FastAPI(title="Automata Platform Backend")

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
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[BACKEND ERROR] {endpoint}: {str(e)}")
            return None

@app.get("/api/all")
async def get_all_dashboard():
    global_balance = 0.0
    try:
        with open("/workspace/LOGS/wallets_globales.json", "r") as f:
            wallets = json.load(f)
            for w in wallets:
                if w.get("owner") == "BROKER_GLOBAL":
                    global_balance = w.get("balance", 1250.00) 
    except: pass

    oportunidades_count = 0
    try:
        with open("/workspace/STACKS/oportunidades.md", "r") as f:
            oportunidades_count = f.read().count("Oportunidad Detectada")
    except: pass

    uae_list = []
    try:
        uaes_dirs = glob.glob("/workspace/UAEs/UAE_*")
        for uae_path in uaes_dirs:
            if not uae_path.endswith("_DEAD"):
                uae_list.append({"id": os.path.basename(uae_path), "balance": 0.0})
    except: pass

    agentes_globales = ["CEO Global", "BROKER Global", "RESEARCHER Global", "INTERFACEAGENT"]
    try:
        agents_data = await query_openclaw_api("agents")
        if agents_data and "agents" in agents_data:
            agentes_globales = [a.get("name", "Agente") for a in agents_data["agents"]]
    except: pass

    real_data = {
        "estado_sistema": "Activo",
        "estado_gateway": "Ok",
        "balance": {"global": global_balance, "uaes": uae_list},
        "agentes_globales": agentes_globales,
        "uaes": {"activas": len(uae_list), "inactivas": 0, "duplicadas": 0, "muertas": 0},
        "oportunidades_globales": oportunidades_count
    }

    payload = {
        "model": "openclaw",
        "messages": [
            {"role": "system", "content": "Eres el InterfaceAgent. Devuelve este JSON real con formato profesional."},
            {"role": "user", "content": json.dumps(real_data)}
        ],
        "response_format": { "type": "json_object" }
    }
    
    res = await query_openclaw_api("chat/completions", "POST", payload)
    if res and "choices" in res:
        try:
            return json.loads(res["choices"][0]["message"]["content"].strip())
        except: pass
    
    return real_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000)
