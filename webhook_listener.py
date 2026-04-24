from fastapi import FastAPI, Request
import subprocess
import os

app = FastAPI(title="Github Webhook Listener")

@app.post("/webhook")
async def github_webhook(request: Request):
    # Aquí podríamos validar el signature de Github, pero para agilizar:
    payload = await request.json()
    
    # Solo actuar si el push es en la rama 'main'
    if payload.get("ref") == "refs/heads/main":
        print("🔔 Push detectado en rama main. Iniciando despliegue automático...")
        
        # Script de despliegue
        deploy_script = """
        cd /root/.openclaw/workspace/front_autoJeke
        git pull origin main
        # Intentar ejecutar docker compose (asumiendo que este script correrá fuera del container de OpenClaw, o montando el socket)
        docker compose up -d --build backend
        """
        
        try:
            # Ejecutar el script en el host
            os.system(deploy_script)
            return {"status": "Deployment triggered"}
        except Exception as e:
            return {"status": "error", "detail": str(e)}
            
    return {"status": "ignored", "reason": "Not main branch"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)
