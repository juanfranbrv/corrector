# app/services/correction_service.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Inicializa el LLM (puedes hacerlo fuera de la función si planeas reutilizarlo)
# language_llm = ChatOpenAI(model="gpt-4o") # Opción más potente
language_llm = ChatOpenAI(model="gpt-3.5-turbo") # Opción más económica para empezar

async def correct_text_with_llm(transcribed_text: str) -> str:
    """
    Utiliza un LLM para corregir el texto y proporcionar feedback.
    """
    try:
        # El prompt es CRUCIAL aquí. Este es solo un ejemplo inicial.
        # Deberás refinarlo mucho, basándote en los criterios de Cambridge, etc.
        system_prompt = """
        Eres un asistente experto en la enseñanza de inglés, especializado en corregir redacciones 
        escritas por estudiantes. Tu tarea es analizar el siguiente texto y proporcionar 
        una corrección detallada.

        Por favor, sigue estas directrices:
        1.  Identifica errores gramaticales, de ortografía, puntuación, uso de vocabulario y estructura de las frases.
        2.  Para cada error, indica claramente el error y la corrección sugerida.
        3.  Proporciona una breve explicación del error, especialmente si es común o conceptualmente importante.
        4.  Ofrece sugerencias para mejorar la claridad, coherencia y estilo general del texto.
        5.  Utiliza un tono constructivo y educativo.
        6.  Formatea tu respuesta de manera clara y organizada, por ejemplo, usando listas o secciones.
            Ejemplo de formato por error:
            - Error: [Texto original con el error]
            - Corrección: [Texto corregido]
            - Explicación: [Breve explicación]
        7.  Al final, puedes dar un breve resumen o una evaluación general si lo consideras útil.
        """

        human_prompt = f"Por favor, corrige la siguiente redacción:\n\n{transcribed_text}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

        response = await language_llm.ainvoke(messages) # Usamos ainvoke para asíncrono

        if response.content and isinstance(response.content, str):
            return response.content
        else:
            return "Error: No se pudo obtener una corrección válida."

    except Exception as e:
        print(f"Error durante la corrección: {e}")
        return f"Error al procesar el texto para corrección: {str(e)}"