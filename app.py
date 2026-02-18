import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Generador de Diplomas", layout="wide", page_icon="🎓")

# --- 2. ESTILO (Solo colores y botones) ---
st.markdown("""
    <style>
    /* Fondo con un degradado suave y profesional */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Tarjetas blancas y limpias para los controles */
    .stExpander {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        border: none !important;
    }

    /* Botones más bonitos y llamativos */
    div.stButton > button:first-child {
        background-color: #002d55; /* Azul oscuro */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #c41e3a; /* Rojo al pasar el mouse */
        color: white;
        transform: scale(1.02);
    }
    
    /* Barra lateral limpia */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES ---
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

    # Dibujar elementos
    dibujar_linea(datos_estudiante['nombre'], config_diseño['tam_nombre'], config_diseño['col_nombre'], config_diseño['y_nombre'])
    
    texto_completo_id = f"{config_diseño['prefijo_id']} {datos_estudiante['id']}"
    dibujar_linea(texto_completo_id, config_diseño['tam_id'], config_diseño['col_id'], config_diseño['y_id'])
    
    dibujar_linea(textos_fijos['motivo_intro'], config_diseño['tam_intro'], config_diseño['col_intro'], config_diseño['y_intro'])
    dibujar_linea(textos_fijos['curso'], config_diseño['tam_curso'], config_diseño['col_curso'], config_diseño['y_curso'])
    dibujar_linea(textos_fijos['horas'], config_diseño['tam_horas'], config_diseño['col_horas'], config_diseño['y_horas'])

    return img

# --- 4. INTERFAZ ---

# Título directo, sin imagen encima
st.title("🎓 Generador de Certificados Premium")
st.markdown("---")

# Barra Lateral
with st.sidebar:
    if os.path.exists("mi_logo.png"):
        st.image("mi_logo.png", width=200)
    else:
        st.info("Sube 'mi_logo.png' a GitHub.")

    st.header("⚙️ Configuración Texto")
    txt_intro = st.text_input("Introducción", "Por haber participado y aprobado el:")
    txt_curso = st.text_area("Nombre del Curso", "DIPLOMADO EN GESTIÓN")
    txt_horas = st.text_input("Detalles / Horas", "Intensidad: 120 Horas")
    txt_prefijo_id = st.text_input("Prefijo ID", "C.C.")

# Columnas principales
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("1. Archivos")
    plantilla = st.file_uploader("Subir Plantilla (Imagen)", type=["jpg", "png", "jpeg"])
    excel = st.file_uploader("Subir Excel Estudiantes", type=["xlsx"])
    if not excel:
        st.caption("El Excel debe tener columnas: 'Nombres' e 'Identificacion'")

with col2:
    st.subheader("2. Diseño y Posición")
    print ("Aquí puedes ajustar el tamaño y la altura del texto. (Podras verlo en la vista previa):")
    
    with st.expander("👤 Ajustar Nombre e Identificación", expanded=True):
        c1, c2 = st.columns(2)
        tam_nombre = c1.slider("Tamaño Nombre", 50, 400, 160)
        y_nombre = c2.slider("Altura Nombre (Y)", 0, 2000, 600)
        col_nombre = st.color_picker("Color Nombre", "#000000")
        
        st.divider()
        c3, c4 = st.columns(2)
        tam_id = c3.slider("Tamaño ID", 20, 200, 50)
        y_id = c4.slider("Altura ID (Y)", 0, 2000, 750)
        col_id = st.color_picker("Color ID", "#555555")

    with st.expander("📝 Ajustar Textos del Curso"):
        col_textos = st.color_picker("Color Textos Curso", "#002d55")
        y_intro = st.slider("Altura Intro", 0, 2000, 850)
        y_curso = st.slider("Altura Curso", 0, 2000, 1000)
        y_horas = st.slider("Altura Horas", 0, 2000, 1150)

# Configuración empaquetada
config = {
    'tam_nombre': tam_nombre, 'y_nombre': y_nombre, 'col_nombre': col_nombre,
    'tam_id': tam_id, 'y_id': y_id, 'col_id': col_id, 'prefijo_id': txt_prefijo_id,
    'tam_intro': 45, 'y_intro': y_intro, 'col_intro': col_textos,
    'tam_curso': 90, 'y_curso': y_curso, 'col_curso': col_textos,
    'tam_horas': 35, 'y_horas': y_horas, 'col_horas': col_textos
}
textos = {'motivo_intro': txt_intro, 'curso': txt_curso, 'horas': txt_horas}

st.markdown("---")

# Botones de Acción
c_btn1, c_btn2 = st.columns(2)

with c_btn1:
    if st.button("👁️ Vista Previa"):
        if plantilla and excel:
            try:
                df = pd.read_excel(excel)
                primero = df.iloc[0]
                datos = {'nombre': str(primero["Nombres"]), 'id': str(primero["Identificacion"])}
                
                img_prev = generar_diploma(plantilla, datos, textos, config)
                st.image(img_prev, caption="Ejemplo del primer estudiante", use_container_width=True)
            except Exception as e:
                st.error(f"Error leyendo el Excel: {e}")
        else:
            st.warning("Sube los archivos primero.")

with c_btn2:
    if st.button("🚀 Descargar Todos (ZIP)"):
        if plantilla and excel:
            df = pd.read_excel(excel)
            buffer = io.BytesIO()
            barra = st.progress(0)
            
            with zipfile.ZipFile(buffer, "w") as zf:
                total = len(df)
                for i, row in df.iterrows():
                    datos = {'nombre': str(row["Nombres"]), 'id': str(row["Identificacion"])}
                    img = generar_diploma(plantilla, datos, textos, config)
                    
                    pdf_bytes = io.BytesIO()
                    img.save(pdf_bytes, format="PDF")
                    zf.writestr(f"Diploma_{datos['nombre']}.pdf", pdf_bytes.getvalue())
                    barra.progress((i + 1) / total)
            
            st.success("¡Diplomas generados!")
            st.download_button("📥 Bajar archivo ZIP", buffer.getvalue(), "diplomas.zip", "application/zip")