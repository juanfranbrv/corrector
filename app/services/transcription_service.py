# app/services/transcription_service.py
import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Cargar claves API desde Streamlit Secrets
openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
together_api_key = os.getenv("TOGETHER_API_KEY")


# Inicializa el LLM (puedes hacerlo fuera de la función si planeas reutilizarlo)
# Asegúrate de que tu OPENAI_API_KEY está en .env
# Para GPT-4o (que tiene capacidades de visión)
vision_llm = ChatOpenAI(model="o4-mini", api_key=openai_api_key) 

async def transcribe_image_to_text(image_bytes: bytes) -> str:
    """
    Transcribe el texto manuscrito de una imagen usando un LLM con capacidad de visión.
    """
    try:
        # Codificar la imagen a base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # Crear el mensaje para el LLM
        # El prompt es crucial aquí. Necesitarás experimentar.
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Transcribe el texto manuscrito que se encuentra en esta imagen. "
                            "Prioriza la precisión del texto transcrito. "
                            "Si hay partes ilegibles, indícalo con [ilegible].",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ]
        )

        # Llamar al LLM
        response = await vision_llm.ainvoke([message]) # Usamos ainvoke para asíncrono

        if response.content and isinstance(response.content, str):
            return response.content
        else:
            # Manejar el caso donde la respuesta no es lo esperado
            return "Error: No se pudo obtener una transcripción válida."

    except Exception as e:
        print(f"Error durante la transcripción: {e}")
        # En un caso real, querrías un logging más robusto
        return f"Error al procesar la imagen para transcripción: {str(e)}"