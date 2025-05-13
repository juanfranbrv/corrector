from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# Crear instancia de FastAPI
app = FastAPI()

# Montar archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Endpoint para la página principal
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Sirve la página principal (index.html).
    """
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hola desde FastAPI"})

# Endpoint para la demostración de HTMX
@app.get("/greet", response_class=HTMLResponse)
async def greet_htmx():
    """
    Devuelve un fragmento HTML para ser insertado por HTMX.
    """
    return """
    <p class="text-green-600 font-semibold">¡Hola desde el servidor con HTMX! 🎉</p>
    <p class="text-sm text-gray-500">Este contenido fue cargado dinámicamente.</p>
    """



if __name__ == "__main__":
    pass