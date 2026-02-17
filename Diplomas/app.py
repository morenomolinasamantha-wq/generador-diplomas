import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile
import os

# --- CONFIGURACIÓN ---
ARCHIVO_FUENTE_LOCAL = "fuente.ttf" 

def generar_diploma(imagen_plantilla, datos_estudiante, textos_fijos, config_diseño):
    img = Image.open(imagen_plantilla).convert("RGB")
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Intentamos cargar la fuente
    try:
        # Cargamos la fuente una vez para usarla en todo
        fuente_base = ARCHIVO_FUENTE_LOCAL
    except:
        st.error(f"⚠️ NO ENCUENTRO EL ARCHIVO '{ARCHIVO_FUENTE_LOCAL}'.")
        return img

    # --- FUNCIÓN AYUDANTE PARA DIBUJAR CADA LÍNEA ---
    def dibujar_linea(texto, tamaño, color, pos_y_offset):
        if not texto: return
        try:
            font = ImageFont.truetype(fuente_base, tamaño)
        except:
            font = ImageFont.load_default()
            
        bbox = draw.textbbox((0, 0), str(texto), font=font)
        w_texto = bbox[2] - bbox[0]
        pos_x = (W - w_texto) / 2
        draw.text((pos_x, pos_y_offset), str(texto), font=font, fill=color)

    # 1. NOMBRE (Del Excel)
    dibujar_linea(datos_estudiante['nombre'], config_diseño['tam_nombre'], config_diseño['col_nombre'], config_diseño['y_nombre'])

    # 2. IDENTIFICACIÓN (Del Excel) - Se suele poner "C.C. " antes del número
    texto_id = f"{config_diseño['prefijo_id']} {datos_estudiante['id']}"
    dibujar_linea(texto_id, config_diseño['tam_id'], config_diseño['col_id'], config_diseño['y_id'])

    # 3. TEXTO MOTIVO (Ej: "Participó en el curso de")
    dibujar_linea(textos_fijos['motivo_intro'], config_diseño['tam_intro'], config_diseño['col_intro'], config_diseño['y_intro'])

    # 4. NOMBRE DEL CURSO (Ej: "PYTHON PARA TODOS")
    dibujar_linea(textos_fijos['curso'], config_diseño['tam_curso'], config_diseño['col_curso'], config_diseño['y_curso'])

    # 5. HORAS (Ej: "Intensidad de 40 horas")
    dibujar_linea(textos_fijos['horas'], config_diseño['tam_horas'], config_diseño['col_horas'], config_diseño['y_horas'])

    return img

# --- INTERFAZ ---
st.set_page_config(page_title="Generador de Diplomas Pro", layout="wide")
st.title("🎓 Generador de Diplomas - Multilínea")

# Verificación inicial
if not os.path.exists(ARCHIVO_FUENTE_LOCAL):
    st.warning(f"🚨 FALTANTE: No veo el archivo '{ARCHIVO_FUENTE_LOCAL}' en la carpeta.")

# --- BARRA LATERAL (DATOS FIJOS) ---
with st.sidebar:
    st.header("📝 Datos del Diploma")
    txt_intro = st.text_input("1. Texto Intro", "Participó y aprobó el curso de:")
    txt_curso = st.text_input("2. Nombre del Curso", "INTELIGENCIA ARTIFICIAL")
    txt_horas = st.text_input("3. Horas/Fecha", "Duración: 40 Horas - Agosto 2025")
    txt_prefijo_id = st.text_input("Prefijo ID", "C.C.", help="Lo que va antes del número")

# --- ÁREA PRINCIPAL ---
col_izq, col_der = st.columns([1, 2], gap="large")

with col_izq:
    st.subheader("📂 Archivos")
    archivo_plantilla = st.file_uploader("Subir Plantilla (Imagen)", type=["jpg", "png"])
    archivo_excel = st.file_uploader("Subir Excel (con Nombres e Identificacion)", type=["xlsx"])

with col_der:
    st.subheader("🎨 Diseño y Posiciones")
    st.info("Ajusta el tamaño y la altura (Y) de cada elemento.")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👤 Nombre", "🆔 ID", "✍️ Intro", "🎓 Curso", "⏰ Horas"])

    with tab1:
        c1, c2 = st.columns(2)
        tam_nombre = c1.slider("Tamaño Nombre", 50, 300, 150)
        y_nombre = c2.slider("Altura Nombre (Y)", 0, 1500, 500)
        col_nombre = st.color_picker("Color Nombre", "#000000")
    
    with tab2:
        c1, c2 = st.columns(2)
        tam_id = c1.slider("Tamaño ID", 20, 150, 60)
        y_id = c2.slider("Altura ID (Y)", 0, 1500, 650)
        col_id = st.color_picker("Color ID", "#555555")

    with tab3: # Intro (Motivo)
        c1, c2 = st.columns(2)
        tam_intro = c1.slider("Tamaño Intro", 20, 150, 50)
        y_intro = c2.slider("Altura Intro (Y)", 0, 1500, 750)
        col_intro = st.color_picker("Color Intro", "#555555")

    with tab4: # Curso
        c1, c2 = st.columns(2)
        tam_curso = c1.slider("Tamaño Curso", 40, 300, 100)
        y_curso = c2.slider("Altura Curso (Y)", 0, 1500, 850)
        col_curso = st.color_picker("Color Curso", "#003366")

    with tab5: # Horas
        c1, c2 = st.columns(2)
        tam_horas = c1.slider("Tamaño Horas", 20, 150, 40)
        y_horas = c2.slider("Altura Horas (Y)", 0, 1500, 1000)
        col_horas = st.color_picker("Color Horas", "#555555")

# --- EMPAQUETAR CONFIGURACIÓN ---
config_diseño = {
    'tam_nombre': tam_nombre, 'y_nombre': y_nombre, 'col_nombre': col_nombre,
    'tam_id': tam_id, 'y_id': y_id, 'col_id': col_id, 'prefijo_id': txt_prefijo_id,
    'tam_intro': tam_intro, 'y_intro': y_intro, 'col_intro': col_intro,
    'tam_curso': tam_curso, 'y_curso': y_curso, 'col_curso': col_curso,
    'tam_horas': tam_horas, 'y_horas': y_horas, 'col_horas': col_horas
}
textos_fijos = {'motivo_intro': txt_intro, 'curso': txt_curso, 'horas': txt_horas}

st.divider()

# --- BOTONES DE ACCIÓN ---
if st.button("👁️‍🗨️ Vista Previa (Primer estudiante)"):
    if archivo_plantilla and archivo_excel:
        df = pd.read_excel(archivo_excel)
        # Convertimos a string para evitar errores con números
        df['Identificacion'] = df['Identificacion'].astype(str)
        
        if "Nombres" in df.columns and "Identificacion" in df.columns:
            fila = df.iloc[0]
            datos_preview = {'nombre': str(fila["Nombres"]), 'id': str(fila["Identificacion"])}
            
            img = generar_diploma(archivo_plantilla, datos_preview, textos_fijos, config_diseño)
            st.image(img, caption="Así se verá el diploma")
        else:
            st.error("❌ El Excel debe tener columnas: 'Nombres' e 'Identificacion'")
    else:
        st.warning("Sube la plantilla y el Excel para ver la prueba.")

if st.button("🚀 Generar Todos"):
    if archivo_plantilla and archivo_excel:
        df = pd.read_excel(archivo_excel)
        df['Identificacion'] = df['Identificacion'].astype(str) # Importante
        
        if "Nombres" in df.columns and "Identificacion" in df.columns:
            zip_buffer = io.BytesIO()
            progreso = st.progress(0)
            
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for i, row in df.iterrows():
                    datos = {'nombre': str(row["Nombres"]), 'id': str(row["Identificacion"])}
                    img = generar_diploma(archivo_plantilla, datos, textos_fijos, config_diseño)
                    
                    b = io.BytesIO()
                    img.save(b, format="PDF")
                    zf.writestr(f"Diploma_{datos['nombre']}.pdf", b.getvalue())
                    progreso.progress((i+1)/len(df))
            
            st.success("¡Diplomas listos!")
            st.download_button("Descargar ZIP", zip_buffer.getvalue(), "diplomas_completos.zip", "application/zip")