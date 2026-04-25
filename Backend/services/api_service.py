from fastapi import APIRouter
import json
from services.openclaw_gateway import send_message_to_agent

router = APIRouter()

@router.get("/all")
async def get_all_data():
    """
    Endpoint unificado.
    Solicita asíncronamente a INTERFACEAGENT la información en el formato predefinido.
    """
    prompt = (
        "Entrégame tu reporte de estado actual. Necesito el balance, las UAEs activas y la cantidad de oportunidades. "
        "Devuelve tu respuesta ÚNICAMENTE en formato JSON estricto con la siguiente estructura, "
        "sin usar bloques de código Markdown ni texto extra introductorio:\n"
        "{\n"
        '  "balance": "1000.00",\n'
        '  "uaes_activas": 0,\n'
        '  "oportunidades": 0\n'
        "}"
    )
    
    try:
        # Espera asíncrona de la respuesta del agente
        # agent_name recibido del frontend suele ser INTERFACEAGENT, lo mapeamos a 'comunication'
        target_agent = "comunication" if agent_name.upper() == "INTERFACEAGENT" else agent_name
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
