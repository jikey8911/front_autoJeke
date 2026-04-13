
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# CORS — permite peticiones desde el frontend en puerto 3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENCLAW_GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://host.docker.internal:10424")

class OpenClawRequest(BaseModel):
    data_needed: str
    format_expected: str

@app.get("/agents")
async def get_agents():
    """
    Obtiene la lista de agentes y sus características.
    """
    try:
        response = requests.post(f"{OPENCLAW_GATEWAY_URL}/request_info", json={
            "data_needed": "agents",
            "format_expected": "json"
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con OpenClaw Gateway: {e}")

@app.get("/opportunities")
async def get_opportunities():
    """
    Obtiene la lista de oportunidades encontradas.
    """
    try:
        response = requests.post(f"{OPENCLAW_GATEWAY_URL}/request_info", json={
            "data_needed": "opportunities",
            "format_expected": "json"
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con OpenClaw Gateway: {e}")

@app.get("/running_tasks")
async def get_running_tasks():
    """
    Obtiene las tareas que se están ejecutando y por qué agentes.
    """
    try:
        response = requests.post(f"{OPENCLAW_GATEWAY_URL}/request_info", json={
            "data_needed": "running_tasks",
            "format_expected": "json"
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con OpenClaw Gateway: {e}")

@app.get("/balance")
async def get_balance():
    """
    Obtiene el balance del broker.
    """
    try:
        response = requests.post(f"{OPENCLAW_GATEWAY_URL}/request_info", json={
            "data_needed": "balance",
            "format_expected": "json"
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con OpenClaw Gateway: {e}")

@app.get("/status")
async def get_status():
    """
    Obtiene el estado global del sistema.
    """
    try:
        response = requests.post(f"{OPENCLAW_GATEWAY_URL}/request_info", json={
            "data_needed": "status",
            "format_expected": "json"
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con OpenClaw Gateway: {e}")

@app.get("/mitosis")
async def get_mitosis():
    """
    Obtiene cuántos grupos se han duplicado.
    """
    try:
        response = requests.post(f"{OPENCLAW_GATEWAY_URL}/request_info", json={
            "data_needed": "mitosis",
            "format_expected": "json"
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con OpenClaw Gateway: {e}")

@app.get("/kill")
async def get_kill():
    """
    Obtiene cuántos grupos han muerto.
    """
    try:
        response = requests.post(f"{OPENCLAW_GATEWAY_URL}/request_info", json={
            "data_needed": "kill",
            "format_expected": "json"
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con OpenClaw Gateway: {e}")



if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000, reload=True)

