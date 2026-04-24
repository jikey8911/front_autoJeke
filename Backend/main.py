import os
import asyncio
import uvicorn
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware # 1. Importar CORS
from contextlib import asynccontextmanager

# Tus servicios
from services.telegram_service import dp, bot, start_telegram_bot, telegram_router
from services.openclaw_gateway import start_openclaw_gateway
from services.api_service import router as api_all_router

# --- LIFESPAN OPTIMIZADO ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 [BI OS] Levantando servicios core...")
    
    # Iniciar tareas en background
    bg_task_tg = asyncio.create_task(start_telegram_bot())
    bg_task_oc = asyncio.create_task(start_openclaw_gateway())
    
    yield
    
    # Limpieza controlada
    print("🛑 [BI OS] Iniciando secuencia de apagado...")
    bg_task_tg.cancel()
    bg_task_oc.cancel()
    
    try:
        # Esperar un momento a que las tareas se cancelen
        await asyncio.gather(bg_task_tg, bg_task_oc, return_exceptions=True)
        await bot.session.close()
    except Exception as e:
        print(f"⚠️ Error durante el cierre: {e}")
        
    print("✅ [BI OS] Servicios offline.")

app = FastAPI(
    title="BI OS Backend", 
    version="3.0",
    lifespan=lifespan
)

# --- 2. CONFIGURACIÓN DE CORS ---
# Ajusta 'allow_origins' con la URL de tu frontend cuando lo despliegues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, usa ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. MIDDLEWARE DE LOGS (Opcional pero recomendado) ---
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# --- ROUTERS ---
api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {
        "status": "online", 
        "system": "BI_OS_v3.0", 
        "location": "Pasto, CO",
        "telegram_bridge": "active"
    }

app.include_router(api_router, prefix="/api")
app.include_router(api_all_router, prefix="/api")
app.include_router(telegram_router, prefix="/api/telegram")

if __name__ == "__main__":
    # Nota: El puerto 5000 es común para Flask, 8000 para FastAPI. 
    # Mantengo tu puerto 5000.
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)