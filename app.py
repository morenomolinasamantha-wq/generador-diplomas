import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Certificados | Tu Marca", layout="wide", page_icon="📜")

# CSS Avanzado para que NO parezca Streamlit genérico
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    /* Fondo con degradado profesional */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Tarjetas blancas con sombra para los controles */
    .stExpander {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: none !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1) !important;
        margin-bottom: 15px;
    }

    /* Botón principal llamativo */
    div.stButton > button:first-child {
        background: linear-gradient(to right, #1e3c72, #2a5298);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Personalizar barra lateral */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA ---
ARCHIVO_FUENTE_LOCAL = "fuente.ttf" 

def generar_diploma(imagen_plantilla, datos_estudiante, textos_fijos, config_diseño):
    img = Image.open(imagen_plantilla).convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    def dibujar_linea(texto, tamaño, color, pos_y):
        if not texto: return
        try:
            font = ImageFont.truetype(ARCHIVO_FUENTE_LOCAL, tamaño)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), str(texto), font=font)
        w_texto = bbox[2] - bbox[0]
        draw.text(((W - w_texto) / 2, pos_y), str(texto), font=font, fill=color)

    dibujar_linea(datos_estudiante['nombre'], config_diseño['tam_nombre'], config_diseño['col_nombre'], config_diseño['y_nombre'])
    dibujar_linea(f"{config_diseño['prefijo_id']} {datos_estudiante['id']}", config_diseño['tam_id'], config_diseño['col_id'], config_diseño['y_id'])
    dibujar_linea(textos_fijos['motivo_intro'], config_diseño['tam_intro'], config_diseño['col_intro'], config_diseño['y_intro'])
    dibujar_linea(textos_fijos['curso'], config_diseño['tam_curso'], config_diseño['col_curso'], config_diseño['y_curso'])
    dibujar_linea(textos_fijos['horas'], config_diseño['tam_horas'], config_diseño['col_horas'], config_diseño['y_horas'])
    return img

# --- 3. INTERFAZ ---

# Imagen de cabecera para dar estilo
st.image("https://images.unsplash.com/photo-1589330694653-ded6df03f754?auto=format&fit=crop&q=80&w=1500", use_container_width=True)
st.title("🌟 Generador de Certificados Premium")

with st.sidebar:
    # CORRECCIÓN DEL LOGO
    if os.path.exists("mi_logo.png"):
        st.image("mi_logo.png", width=200)
    else:
        st.warning("No se encontró mi_logo.png")
        
    st.markdown("---")
    txt_intro = st.text_input("Introducción", "Certifica que:")
    txt_curso = st.text_area("Curso", "CURSO DE ALTA GERENCIA")
    txt_horas = st.text_input("Detalles", "120 Horas | Bogotá D.C.")
    txt_prefijo_id = st.text_input("Prefijo ID", "C.C.")

col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("📁 Carga de Datos")
    archivo_plantilla = st.file_uploader("Plantilla (JPG/PNG)", type=["jpg", "png"])
    archivo_excel = st.file_uploader("Excel de Alumnos", type=["xlsx"])

with col2:
    st.subheader("🎨 Personalización")
    with st.expander("📏 Ajustar Posiciones", expanded=True):
        tam_nombre = st.slider("Tamaño Nombre", 50, 300, 150)
        y_nombre = st.slider("Altura Nombre", 0, 1500, 600)
        col_nombre = st.color_picker("Color Nombre", "#1e3c72")
        
        st.divider()
        tam_id = st.slider("Tamaño ID", 20, 150, 40)
        y_id = st.slider("Altura ID", 0, 1500, 720)
        col_id = st.color_picker("Color ID", "#333333")

    with st.expander("📝 Otros Textos"):
        col_resto = st.color_picker("Color Textos", "#2a5298")
        y_intro = st.slider("Altura Intro", 0, 1500, 850)
        y_curso = st.slider("Altura Curso", 0, 1500, 1000)
        y_horas = st.slider("Altura Horas", 0, 1500, 1150)

# CONFIGURACIONES
config = {
    'tam_nombre': tam_nombre, 'y_nombre': y_nombre, 'col_nombre': col_nombre,
    'tam_id': tam_id, 'y_id': y_id, 'col_id': col_id, 'prefijo_id': txt_prefijo_id,
    'tam_intro': 40, 'y_intro': y_intro, 'col_intro': col_resto,
    'tam_curso': 80, 'y_curso': y_curso, 'col_curso': col_resto,
    'tam_horas': 30, 'y_horas': y_horas, 'col_horas': col_resto
}

if st.button("👁️ Vista Previa"):
    if archivo_plantilla and archivo_excel:
        df = pd.read_excel(archivo_excel)
        fila = df.iloc[0]
        img = generar_diploma(archivo_plantilla, {'nombre': str(fila["Nombres"]), 'id': str(fila["Identificacion"])}, {'motivo_intro': txt_intro, 'curso': txt_curso, 'horas': txt_horas}, config)
        st.image(img)

if st.button("🚀 Generar Todo (ZIP)"):
    if archivo_plantilla and archivo_excel:
        df = pd.read_excel(archivo_excel)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for _, row in df.iterrows():
                img = generar_diploma(archivo_plantilla, {'nombre': str(row["Nombres"]), 'id': str(row["Identificacion"])}, {'motivo_intro': txt_intro, 'curso': txt_curso, 'horas': txt_horas}, config)
                b = io.BytesIO()
                img.save(b, format="PDF")
                zf.writestr(f"Diploma_{row['Nombres']}.pdf", b.getvalue())
        st.download_button("📥 Descargar ZIP", zip_buffer.getvalue(), "diplomas.zip")