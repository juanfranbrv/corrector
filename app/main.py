# app/main.py

from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

# Importa tus nuevos servicios
from app.services.transcription_service import transcribe_image_to_text
from app.services.correction_service import correct_text_with_llm

# Cargar variables de entorno desde .env
load_dotenv()

# Cargar claves API desde Streamlit Secrets
openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
together_api_key = os.getenv("TOGETHER_API_KEY")

# Crear instancia de FastAPI
app = FastAPI(title="Corrector App") # Puedes darle un título

# Montar archivos estáticos (CSS, JS, imágenes)
# El primer "static" es la ruta URL, "directory" es la carpeta local
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar Jinja2Templates
# "templates" es el nombre de la carpeta donde están tus plantillas
templates = Jinja2Templates(directory="templates")

# Obtener el título de la app desde .env o usar uno por defecto
APP_TITLE = os.getenv("APP_TITLE", "Asistente de Corrección")

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Sirve la página principal (index.html).
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_title": APP_TITLE # Pasamos el título a la plantilla base
    })

@app.get("/greet", response_class=HTMLResponse)
async def greet_htmx():
    """
    Endpoint de demostración de HTMX (opcional, puedes quitarlo si quieres).
    Devuelve un fragmento HTML para ser insertado por HTMX.
    """
    return """
    <p class="text-green-600 font-semibold">¡Hola desde el servidor con HTMX! 🎉</p>
    <p class="text-sm text-gray-500">Este contenido fue cargado dinámicamente.</p>
    """

@app.post("/upload-and-correct/", response_class=HTMLResponse)
async def handle_upload_and_correct(request: Request, essay_image: UploadFile = File(...)):
    """
    Endpoint para subir una imagen de redacción, transcribirla y corregirla.
    Devuelve un fragmento HTML con los resultados para HTMX.
    """
    filename = essay_image.filename
    error_message_transcription = None
    error_message_correction = None
    transcribed_text_result = ""
    corrected_text_result = ""

    try:
        image_bytes = await essay_image.read()

        # 1. Transcribir imagen a texto
        print(f"Iniciando transcripción para: {filename}")
        transcribed_text = await transcribe_image_to_text(image_bytes)
        print(f"Texto transcrito (primeros 100 chars): {transcribed_text[:100]}")

        if "Error:" in transcribed_text or not transcribed_text.strip():
            error_message_transcription = transcribed_text if "Error:" in transcribed_text else "La transcripción no produjo texto."
            transcribed_text_result = error_message_transcription # Mostrar el error en la UI
            # No continuar con la corrección si la transcripción falló gravemente
            corrected_text_result = "No se pudo transcribir la imagen para proceder con la corrección."
        else:
            transcribed_text_result = transcribed_text
            # 2. Corregir el texto transcrito
            print(f"Iniciando corrección para texto transcrito...")
            corrected_text = await correct_text_with_llm(transcribed_text)
            print(f"Texto corregido (primeros 100 chars): {corrected_text[:100]}")
            if "Error:" in corrected_text:
                error_message_correction = corrected_text
                corrected_text_result = error_message_correction
            else:
                corrected_text_result = corrected_text

    except Exception as e:
        print(f"Error general en el endpoint /upload-and-correct/ para {filename}: {e}")
        # Esto es un error más del sistema, no específico de un paso LLM.
        # Puedes personalizar el mensaje según el tipo de error si es necesario.
        error_message_transcription = f"Error del sistema al procesar el archivo: {str(e)}"
        transcribed_text_result = "Ocurrió un error procesando la imagen."
        corrected_text_result = "No se pudo completar el proceso debido a un error del sistema."


    # Devolver un fragmento HTML con los resultados
    return templates.TemplateResponse("partials/correction_results.html", {
        "request": request,
        "filename": filename,
        "transcribed_text": transcribed_text_result,
        "corrected_text": corrected_text_result,
        "error_transcription": error_message_transcription, # Para mostrar errores específicos si los hay
        "error_correction": error_message_correction
    })


# Si quieres poder ejecutar con 'python app/main.py' para pruebas rápidas,
# aunque 'uvicorn app.main:app --reload' o 'uv run dev' es lo recomendado.
if __name__ == "__main__":
    import uvicorn
    # Asegúrate de tener Uvicorn instalado si corres así: uv pip install uvicorn[standard]
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)