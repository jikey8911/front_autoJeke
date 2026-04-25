from fastapi import APIRouter
import json
from services.openclaw_gateway import send_message_to_agent

router = APIRouter()

@router.get("/all")
async def get_all_data():
    """
    Endpoint unificado.
    Solicita asíncronamente al agente de comunicación la información en el formato predefinido.
    """
    # El Dashboard busca datos holísticos, delegamos al agente 'comunication'
    target_agent = "comunication"
    
    # Prompt optimizado para reporte estricto v3.0
    prompt = (
        "Genera un reporte de estado técnico del BI OS v3.0. "
        "Necesito: balance global consolidado, conteo total de carpetas en /uaes/ y conteo de misiones en oportunidades_global.md. "
        "Devuelve ÚNICAMENTE un JSON con este formato exacto, sin bloques de código ni texto extra: "
        '{"balance": "36.02", "uaes_activas": 21, "oportunidades": 14}'
    )
    
    try:
        # Espera asíncrona de la respuesta del agente
        agent_response_text = await send_message_to_agent(target_agent, prompt)
        
        # Limpiamos posibles formatos de markdown (```json ... ```) si el modelo los añade
        cleaned_text = agent_response_text.replace("```json", "").replace("```", "").strip()
        
        # Parseamos el JSON
        data = json.loads(cleaned_text)
        
        return {
            "status": "success",
            "data": data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error parseando o esperando al agente: {str(e)}",
            "data": None
        }
