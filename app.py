import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Generador Pro | Uniagustiniana", layout="wide")

# Inyectamos CSS para que la página sea única (interés en Web Development)
st.markdown("""
    <style>
    /* Color de fondo y tipografía general */
    .main {
        background-color: #f5f7f9;
    }
    /* Estilo para los títulos */
    h1 {
        color: #002d55;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
        padding-bottom: 20px;
    }
    /* Personalización de botones */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #002d55;
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #c41e3a;
        color: white;
        border: none;
    }
    /* Contenedores de opciones */
    .stExpander {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA DE PROCESAMIENTO ---
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
        pos_x = (W - w_texto) / 2
        draw.text((pos_x, pos_y), str(texto), font=font, fill=color)

    # Dibujamos cada elemento según el diseño
    dibujar_linea(datos_estudiante['nombre'], config_diseño['tam_nombre'], config_diseño['col_nombre'], config_diseño['y_nombre'])
    
    texto_id = f"{config_diseño['prefijo_id']} {datos_estudiante['id']}"
    dibujar_linea(texto_id, config_diseño['tam_id'], config_diseño['col_id'], config_diseño['y_id'])
    
    dibujar_linea(textos_fijos['motivo_intro'], config_diseño['tam_intro'], config_diseño['col_intro'], config_diseño['y_intro'])
    dibujar_linea(textos_fijos['curso'], config_diseño['tam_curso'], config_diseño['col_curso'], config_diseño['y_curso'])
    dibujar_linea(textos_fijos['horas'], config_diseño['tam_horas'], config_diseño['col_horas'], config_diseño['y_horas'])

    return img

# --- 3. INTERFAZ DE USUARIO ---
st.title("🎓 Sistema Institucional de Certificación")

if not os.path.exists(ARCHIVO_FUENTE_LOCAL):
    st.error(f"❌ Error crítico: No se encontró '{ARCHIVO_FUENTE_LOCAL}' en el servidor.")

# Barra lateral para textos que no cambian por estudiante
with st.sidebar:
    st.image("https://www.uniagustiniana.edu.co/sites/default/files/logo-uniagustiniana.png", width=200) # Opcional: logo si tienes link
    st.header("⚙️ Configuración Global")
    txt_intro = st.text_input("Frase de Introducción", "Por haber participado y aprobado el:")
    txt_curso = st.text_area("Nombre del Curso / Evento", "DIPLOMADO EN GESTIÓN EDUCATIVA")
    txt_horas = st.text_input("Intensidad y Fecha", "Intensidad: 120 Horas | Bogotá D.C.")
    txt_prefijo_id = st.text_input("Texto antes del número (ID)", "C.C.")

# Diseño principal en columnas
col_archivos, col_ajustes = st.columns([1, 1.5], gap="large")

with col_archivos:
    st.subheader("📂 Carga de Archivos")
    archivo_plantilla = st.file_uploader("1. Imagen de Fondo (Plantilla)", type=["jpg", "png"])
    archivo_excel = st.file_uploader("2. Listado de Estudiantes (Excel)", type=["xlsx"])
    st.info("El Excel debe tener columnas: 'Nombres' e 'Identificacion'")

with col_ajustes:
    st.subheader("🎨 Ajustes de Posición")
    
    with st.expander("👤 Estilo del Nombre e Identificación", expanded=True):
        c1, c2, c3 = st.columns(3)
        tam_nombre = c1.slider("Tamaño Nombre", 50, 400, 160)
        y_nombre = c2.slider("Altura Nombre (Y)", 0, 2000, 600)
        col_nombre = c3.color_picker("Color Nombre", "#000000")
        
        c4, c5, c6 = st.columns(3)
        tam_id = c4.slider("Tamaño Cédula", 20, 200, 50)
        y_id = c5.slider("Altura Cédula (Y)", 0, 2000, 700)
        col_id = c6.color_picker("Color Cédula", "#444444")

    with st.expander("✍️ Estilo del Motivo y Curso"):
        c1, c2 = st.columns(2)
        tam_intro = c1.slider("Tamaño Intro", 20, 150, 45)
        y_intro = c2.slider("Altura Intro (Y)", 0, 2000, 850)
        
        c3, c4 = st.columns(2)
        tam_curso = c3.slider("Tamaño Curso", 30, 250, 90)
        y_curso = c4.slider("Altura Curso (Y)", 0, 2000, 1000)
        
        c5, c6 = st.columns(2)
        tam_horas = c5.slider("Tamaño Horas", 20, 120, 35)
        y_horas = c6.slider("Altura Horas (Y)", 0, 2000, 1150)
        
        col_textos = st.color_picker("Color de textos adicionales", "#002d55")

# Empaquetamos configuraciones
config_diseño = {
    'tam_nombre': tam_nombre, 'y_nombre': y_nombre, 'col_nombre': col_nombre,
    'tam_id': tam_id, 'y_id': y_id, 'col_id': col_id, 'prefijo_id': txt_prefijo_id,
    'tam_intro': tam_intro, 'y_intro': y_intro, 'col_intro': col_textos,
    'tam_curso': tam_curso, 'y_curso': y_curso, 'col_curso': col_textos,
    'tam_horas': tam_horas, 'y_horas': y_horas, 'col_horas': col_textos
}
textos_fijos = {'motivo_intro': txt_intro, 'curso': txt_curso, 'horas': txt_horas}

st.divider()

# --- 4. ACCIONES ---
col_pre, col_gen = st.columns(2)

with col_pre:
    if st.button("👁️ Ver Vista Previa"):
        if archivo_plantilla and archivo_excel:
            df = pd.read_excel(archivo_excel)
            df['Identificacion'] = df['Identificacion'].astype(str)
            fila = df.iloc[0]
            datos_preview = {'nombre': str(fila["Nombres"]), 'id': str(fila["Identificacion"])}
            
            img = generar_diploma(archivo_plantilla, datos_preview, textos_fijos, config_diseño)
            st.image(img, use_container_width=True)
        else:
            st.warning("⚠️ Sube los archivos primero.")

with col_gen:
    if st.button("🚀 Generar y Descargar Todo (ZIP)"):
        if archivo_plantilla and archivo_excel:
            df = pd.read_excel(archivo_excel)
            df['Identificacion'] = df['Identificacion'].astype(str)
            zip_buffer = io.BytesIO()
            bar = st.progress(0)
            
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i, row in df.iterrows():
                    datos = {'nombre': str(row["Nombres"]), 'id': str(row["Identificacion"])}
                    img = generar_diploma(archivo_plantilla, datos, textos_fijos, config_diseño)
                    b = io.BytesIO()
                    img.save(b, format="PDF")
                    zf.writestr(f"Diploma_{datos['nombre']}.pdf", b.getvalue())
                    bar.progress((i+1)/len(df))
            
            st.success("✅ ¡Proceso completado!")
            st.download_button("📥 Descargar Archivo ZIP", zip_buffer.getvalue(), "diplomas.zip", "application/zip")