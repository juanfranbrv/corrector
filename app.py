import streamlit as st
import io
import os
from PIL import Image
import base64
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import tempfile

# Función para inicializar la configuración de la sesión
if 'extracted_text' not in st.session_state:
    st.session_state['extracted_text'] = ""

# Configuración de la página
st.set_page_config(
    page_title="OCR con LangChain y LLMs",
    page_icon="📝",
    layout="wide"
)

# Título principal
st.title("Extracción de Texto desde Imágenes con LLMs")

def encode_image(image_file):
    """Codifica una imagen en base64 para enviarla a la API"""
    temp_file = None
    try:
        if hasattr(image_file, 'read'):
            # Si ya es un objeto tipo archivo (como el resultado de st.file_uploader)
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(image_file.getvalue())
            temp_file.close()
            image_path = temp_file.name
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        else:
            # Si es una ruta de archivo
            with open(image_file, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
    finally:
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

def extract_text_from_image(image_file, model_name, api_keys):
    """
    Extrae texto de una imagen utilizando el modelo LLM seleccionado a través de LangChain.
    """
    # Instrucción para la extracción de texto
    prompt = "Por favor, extrae y transcribe todo el texto que aparece en esta imagen. Devuelve únicamente el texto, sin explicaciones adicionales."
    
    if model_name == "OpenAI GPT-4 Vision":
        # Configurar el modelo de OpenAI
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_keys["OPENAI_API_KEY"],
            max_tokens=1000
        )
        
        # Convertir imagen a base64
        if hasattr(image_file, 'getvalue'):
            image_data = image_file.getvalue()
            temp_img = Image.open(io.BytesIO(image_data))
            # Redimensionar la imagen si es muy grande
            max_size = 1000
            if max(temp_img.size) > max_size:
                ratio = max_size / max(temp_img.size)
                new_size = (int(temp_img.size[0] * ratio), int(temp_img.size[1] * ratio))
                temp_img = temp_img.resize(new_size, Image.LANCZOS)
            
            buffered = io.BytesIO()
            temp_img.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Crear mensaje con imagen
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        )
        
        # Invocar al modelo
        response = llm.invoke([message])
        return response.content
    
    elif model_name == "Groq LLM+":
        # Configurar el modelo de Groq
        llm = ChatGroq(
            model="llama-3.2-90b-vision-preview",  # Modelo de Groq con capacidades de visión
            api_key=api_keys["GROQ_API_KEY"]
        )
        
        # Convertir imagen a base64
        if hasattr(image_file, 'getvalue'):
            image_data = image_file.getvalue()
            temp_img = Image.open(io.BytesIO(image_data))
            # Redimensionar la imagen si es muy grande
            max_size = 1500  # Groq puede manejar imágenes más grandes
            if max(temp_img.size) > max_size:
                ratio = max_size / max(temp_img.size)
                new_size = (int(temp_img.size[0] * ratio), int(temp_img.size[1] * ratio))
                temp_img = temp_img.resize(new_size, Image.LANCZOS)
            
            buffered = io.BytesIO()
            temp_img.save(buffered, format="PNG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Crear mensaje con imagen para Groq
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        )
        
        # Invocar al modelo
        response = llm.invoke([message])
        return response.content
    
    else:
        return "Modelo no soportado"

# Verificar si las claves API existen en secrets o en el entorno
api_keys = {}
for key in ["OPENAI_API_KEY", "GROQ_API_KEY"]:
    # Intentar obtener de st.secrets
    try:
        api_keys[key] = st.secrets[key]
    except:
        # Si no está en secrets, intentar obtener del entorno
        api_keys[key] = os.environ.get(key, "")

# Panel lateral (sidebar)
with st.sidebar:

    # Logo en la parte superior del sidebar
    try:
        logo = Image.open("logoweb1.png")
        st.image(logo, width=200, caption="")
    except Exception as e:
        st.error(f"No se pudo cargar el logo: {e}")
    
    # Texto dummy debajo del logo
    st.markdown("""
    <div style="; padding: 10px 0; margin-bottom: 20px; border-bottom: 1px solid #eee;">
        <p>Herramienta de extracción OCR basada en modelos LLM</p>
        <small>Versión 0.1</small>
    </div>
    """, unsafe_allow_html=True)

    st.header("Configuración")
    
    # Selector de modelos LLM (removido Claude)
    selected_model = st.selectbox(
        "Selecciona un modelo LLM",
        options=["OpenAI GPT-4 Vision", "Groq LLM+"],
        index=0
    )
    
    # Campos para las API keys si no están configuradas
    if selected_model == "OpenAI GPT-4 Vision" and not api_keys["OPENAI_API_KEY"]:
        api_keys["OPENAI_API_KEY"] = st.text_input("OpenAI API Key", type="password")
    elif selected_model == "Groq LLM+" and not api_keys["GROQ_API_KEY"]:
        api_keys["GROQ_API_KEY"] = st.text_input("Groq API Key", type="password")
    
    # Uploader de imágenes
    uploaded_file = st.file_uploader(
        "Sube una imagen con texto",
        type=["jpg", "jpeg", "png"],
        help="Formatos aceptados: JPG, JPEG, PNG"
    )
    
    # Botón para iniciar proceso
    process_button = st.button("Extraer Texto", type="primary", use_container_width=True)

# Contenido principal
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Imagen Original")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
    else:
        st.info("Por favor, sube una imagen para comenzar")

with col2:
    st.subheader("Texto Extraído")
    
    if process_button and uploaded_file is not None:
        # Verificar que tengamos la API key necesaria
        api_key_name = ""
        if selected_model == "OpenAI GPT-4 Vision":
            api_key_name = "OPENAI_API_KEY"
        elif selected_model == "Groq LLM+":
            api_key_name = "GROQ_API_KEY"
        
        if not api_keys[api_key_name]:
            st.error(f"Por favor, proporciona una API key válida para {selected_model}")
        else:
            with st.spinner(f"Extrayendo texto con {selected_model}..."):
                try:
                    # Realizar la extracción real de texto
                    extracted_text = extract_text_from_image(uploaded_file, selected_model, api_keys)
                    st.session_state['extracted_text'] = extracted_text
                    
                    st.success(f"Texto extraído con éxito usando {selected_model}")
                    
                    # Mostrar resultado
                    st.text_area("Resultado:", value=extracted_text, height=300)
                    
                    # Botón para descargar el texto extraído
                    st.download_button(
                        label="Descargar texto",
                        data=extracted_text,
                        file_name="texto_extraido.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Error al extraer texto: {str(e)}")
    
    elif process_button and uploaded_file is None:
        st.error("⚠️ Debes subir una imagen antes de extraer texto")
    
    # Mostrar el texto extraído anteriormente si existe
    elif st.session_state['extracted_text']:
        st.text_area("Resultado anterior:", value=st.session_state['extracted_text'], height=300)
        
        # Botón para descargar el texto extraído anteriormente
        st.download_button(
            label="Descargar texto",
            data=st.session_state['extracted_text'],
            file_name="texto_extraido.txt",
            mime="text/plain"
        )