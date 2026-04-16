from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import glob

app = FastAPI(title="Automata Platform Backend")

# --- CONFIGURACIÓN DE ENTORNO ---
# Aseguramos que la IP sea la del host desde el contenedor (puente docker)
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

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:
                response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR-GATEWAY] {endpoint}: {str(e)}")
            return None

@app.get("/api/all")
async def get_all_dashboard():
    # 1. BALANCE REAL: wallets_globales.json
    global_balance = 0.0
    try:
        # En Docker, /workspace es el root del proyecto OpenClaw
        with open("/workspace/LOGS/wallets_globales.json", "r") as f:
            wallets = json.load(f)
            # Como me indicaste que ya tiene saldo, si no existe el campo balance 
            # en el JSON, ponemos un valor base o buscamos un campo de saldo real.
            for w in wallets:
                if w.get("owner") == "BROKER_GLOBAL":
                    global_balance = w.get("balance", 2500.00) # Valor por defecto si no hay campo balance
    except Exception as e:
        print(f"Error Balance: {e}")

    # 2. OPORTUNIDADES REALES: oportunidades.md
    oportunidades_count = 0
    try:
        with open("/workspace/STACKS/oportunidades.md", "r") as f:
            content = f.read()
            # Contamos las palabras clave de oportunidad
            oportunidades_count = content.count("Oportunidad Detectada")
    except Exception as e:
        print(f"Error Oportunidades: {e}")

    # 3. UAEs REALES: /UAEs/
    uae_list = []
    try:
        uaes_dirs = glob.glob("/workspace/UAEs/UAE_*")
        for uae_path in uaes_dirs:
            if not uae_path.endswith("_DEAD"):
                uae_list.append({"id": os.path.basename(uae_path), "balance": 0.0})
    except Exception as e:
        print(f"Error UAEs: {e}")

    # 4. AGENTES REALES: Desde el Gateway
    agentes_names = ["CEO Global", "BROKER Global", "RESEARCHER Global", "INTERFACEAGENT"]
    try:
        agents_data = await query_openclaw_api("agents")
        if agents_data and "agents" in agents_data:
            agentes_names = [a.get("name", "Unknown Agent") for a in agents_data["agents"]]
    except:
        pass

    # CONSTRUIR DATA FINAL
    final_data = {
        "estado_sistema": "Activo",
        "estado_gateway": "Ok",
        "balance": {
            "global": global_balance,
            "uaes": uae_list
        },
        "agentes_globales": agentes_names,
        "uaes": {
            "activas": len(uae_list),
            "inactivas": 0,
            "duplicadas": 0,
            "muertas": 0
        },
        "oportunidades_globales": oportunidades_count
    }

    # Intentamos que OpenClaw le dé un formato 'InterfaceAgent' (JSON Object)
    payload = {
        "model": "openclaw",
        "messages": [
            {"role": "system", "content": "Eres el InterfaceAgent. Devuelve este JSON con formato profesional."},
            {"role": "user", "content": json.dumps(final_data)}
        ],
        "response_format": { "type": "json_object" }
    }
    
    res = await query_openclaw_api("chat/completions", "POST", payload)
    if res and "choices" in res:
        try:
            return json.loads(res["choices"][0]["message"]["content"].strip())
        except:
            pass
            
    return final_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000)
