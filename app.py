import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Generador Pro de Diplomas", layout="wide", page_icon="🎓")

# Inyectamos CSS para fuentes personalizadas y estilo único
st.markdown("""
    <style>
    /* Importamos una fuente moderna de Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    /* Aplicamos la fuente a toda la aplicación */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Color de fondo principal más limpio */
    .main {
        background-color: #f8f9fa;
    }

    /* Estilo para los títulos */
    h1, h2, h3 {
        color: #2c3e50; /* Un azul oscuro elegante */
        font-weight: 600;
        text-align: center;
    }

    /* Personalización de botones con un degradado sutil */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(to right, #3498db, #2c3e50); /* Degradado azul */
        color: white;
        border: none;
        font-weight: 500;
        transition: 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #2c3e50, #3498db); /* Invertir degradado al pasar el mouse */
        transform: translateY(-2px); /* Pequeño efecto de elevación */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Contenedores de opciones (Expander) con sombra suave */
    .stExpander {
        background-color: white;
        border: none;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Personalizar la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eee;
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
st.title("🎓 Sistema de Certificación Digital")
st.markdown("---") # Línea separadora sutil

if not os.path.exists(ARCHIVO_FUENTE_LOCAL):
    st.error(f"❌ Error crítico: No se encontró '{ARCHIVO_FUENTE_LOCAL}' en el servidor. Asegúrate de subirlo a GitHub.")

# Barra lateral
with st.sidebar:
    # --- SECCIÓN PARA TU LOGO ---
    # 1. Sube tu archivo de logo (ej. "mi_logo.png") a GitHub igual que subiste los otros archivos.
    # 2. Cambia el nombre "logo_placeholder.png" por el nombre exacto de tu archivo.
    logo_archivo = "logo_placeholder.png" # <-- ¡CAMBIA ESTO POR EL NOMBRE DE TU LOGO!
    
    if os.path.exists(logo_archivo):
        st.image(logo_archivo, width=180)
    else:
        # Si no has subido logo, muestra un texto o un logo genérico de internet
        st.header("🌟 Tu Marca Aquí") 
        st.info(f"Sube una imagen llamada '{logo_archivo}' a GitHub para verla aquí.")

    st.markdown("---")
    st.header("⚙️ Configuración del Evento")
    txt_intro = st.text_input("Frase de Introducción", "Por haber participado y aprobado el:")
    txt_curso = st.text_area("Nombre del Curso / Evento", "CURSO DE EJEMPLO")
    txt_horas = st.text_input("Intensidad y Fecha", "Intensidad: X Horas | Ciudad, Fecha")
    txt_prefijo_id = st.text_input("Texto antes del número (ID)", "Doc. Identidad:")

# Diseño principal en columnas
col_archivos, col_ajustes = st.columns([1, 1.5], gap="large")

with col_archivos:
    st.subheader("📂 1. Carga de Archivos")
    st.markdown("Sube la plantilla base y el listado de personas.")
    archivo_plantilla = st.file_uploader("Imagen de Fondo (Plantilla)", type=["jpg", "png"])
    archivo_excel = st.file_uploader("Listado de Estudiantes (Excel)", type=["xlsx"])
    if not archivo_excel:
        st.info("💡 El Excel debe tener columnas llamadas: **'Nombres'** e **'Identificacion'**.")

with col_ajustes:
    st.subheader("🎨 2. Personalización del Diseño")
    st.markdown("Ajusta la posición y tamaño de los textos sobre la plantilla.")
    
    with st.expander("👤 Nombres e Identificación", expanded=True):
        c1, c2, c3 = st.columns(3)
        tam_nombre = c1.slider("Tamaño Nombre", 50, 400, 160)
        y_nombre = c2.slider("Posición Vertical (Y)", 0, 2000, 600)
        col_nombre = c3.color_picker("Color", "#000000", key="c_nom")
        
        st.divider()
        c4, c5, c6 = st.columns(3)
        tam_id = c4.slider("Tamaño ID", 20, 200, 50)
        y_id = c5.slider("Posición Vertical (Y)", 0, 2000, 750)
        col_id = c6.color_picker("Color", "#555555", key="c_id")

    with st.expander("📝 Textos del Evento (Curso, Horas)"):
        col_textos = st.color_picker("Color para todos estos textos", "#2c3e50")
        c1, c2 = st.columns(2)
        tam_intro = c1.slider("Tamaño Intro", 20, 150, 45)
        y_intro = c2.slider("Posición Y", 0, 2000, 900)
        
        c3, c4 = st.columns(2)
        tam_curso = c3.slider("Tamaño Curso", 30, 250, 90)
        y_curso = c4.slider("Posición Y", 0, 2000, 1050)
        
        c5, c6 = st.columns(2)
        tam_horas = c5.slider("Tamaño Horas", 20, 120, 35)
        y_horas = c6.slider("Posición Y", 0, 2000, 1200)

# Empaquetamos configuraciones
config_diseño = {
    'tam_nombre': tam_nombre, 'y_nombre': y_nombre, 'col_nombre': col_nombre,
    'tam_id': tam_id, 'y_id': y_id, 'col_id': col_id, 'prefijo_id': txt_prefijo_id,
    'tam_intro': tam_intro, 'y_intro': y_intro, 'col_intro': col_textos,
    'tam_curso': tam_curso, 'y_curso': y_curso, 'col_curso': col_textos,
    'tam_horas': tam_horas, 'y_horas': y_horas, 'col_horas': col_textos
}
textos_fijos = {'motivo_intro': txt_intro, 'curso': txt_curso, 'horas': txt_horas}

st.markdown("---")

# --- 4. ACCIONES ---
st.subheader("🚀 3. Generar y Descargar")
col_pre, col_gen = st.columns(2, gap="medium")

with col_pre:
    if st.button("👁️ Vista Previa (Primer Nombre)"):
        if archivo_plantilla and archivo_excel:
            try:
                df = pd.read_excel(archivo_excel)
                df['Identificacion'] = df['Identificacion'].astype(str)
                fila = df.iloc[0]
                datos_preview = {'nombre': str(fila["Nombres"]), 'id': str(fila["Identificacion"])}
                
                img = generar_diploma(archivo_plantilla, datos_preview, textos_fijos, config_diseño)
                st.image(img, caption="Así se verá el primer diploma", use_container_width=True)
                st.success("¡Vista previa generada con éxito!")
            except Exception as e:
                 st.error(f"Error al leer archivos: {e}. Revisa que el Excel tenga las columnas correctas.")
        else:
            st.warning("⚠️ Por favor, sube primero la plantilla y el Excel.")

with col_gen:
    st.markdown("Cuando la vista previa esté perfecta, genera todos los diplomas.")
    if st.button("✨ Generar Todos los Diplomas (ZIP)"):
        if archivo_plantilla and archivo_excel:
            try:
                df = pd.read_excel(archivo_excel)
                df['Identificacion'] = df['Identificacion'].astype(str)
                zip_buffer = io.BytesIO()
                bar_progreso = st.progress(0, text="Iniciando...")
                
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    total = len(df)
                    for i, row in df.iterrows():
                        datos = {'nombre': str(row["Nombres"]), 'id': str(row["Identificacion"])}
                        img = generar_diploma(archivo_plantilla, datos, textos_fijos, config_diseño)
                        b = io.BytesIO()
                        img.save(b, format="PDF")
                        zf.writestr(f"Diploma_{datos['nombre']}.pdf", b.getvalue())
                        bar_progreso.progress((i+1)/total, text=f"Procesando {i+1} de {total}...")
                
                bar_progreso.empty()
                st.success(f"✅ ¡{total} diplomas generados correctamente!")
                st.download_button("📥 Descargar Archivo ZIP", zip_buffer.getvalue(), "diplomas_generados.zip", "application/zip", type="primary")
            except Exception as e:
                st.error(f"Ocurrió un error durante la generación: {e}")
        else:
             st.warning("⚠️ Faltan archivos para poder generar el ZIP."))