import streamlit as st
import pandas as pd
from fpdf import FPDF

def color_estatus(val):
    val = str(val).lower()

    if "vigente" in val or "ok" in val:
        return "background-color: #c6f6d5; color: #22543d"

    if "proximo" in val or "por vencer" in val or "vence" in val:
        return "background-color: #fefcbf; color: #744210"

    if "vencido" in val or "expirado" in val:
        return "background-color: #fed7d7; color: #742a2a"

    return ""

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("Consulta de Cursos")

# =========================
# CARGAR EXCEL
# =========================
FILE = "BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx"

df_raw = pd.read_excel(FILE, header=None)

# fila donde están los nombres de cursos
fila_cursos = df_raw.iloc[1]

# limpiar dataframe
df = df_raw.copy()
df.columns = df.iloc[1]
df = df[2:].reset_index(drop=True)
df.columns = df.columns.astype(str).str.strip()

# =========================
# COLUMNAS BASE
# =========================
COL_NOMINA = "Nómina"
COL_NOMBRE = "Nombre del Colaborador"

# =========================
# INPUT
# =========================
if "nomina" not in st.session_state:
    st.session_state.nomina = None

if st.session_state.nomina is None:
    st.image("logo.png", width=150)

    nomina_input = st.text_input("Ingresa tu número de nómina")

    if st.button("Ver mis cursos"):
        if nomina_input.strip() == "":
            st.warning("Ingresa tu número de nómina")
        else:
            st.session_state.nomina = nomina_input.strip()
            st.rerun()

    st.stop()

nomina = st.session_state.nomina

# =========================
# FILTRAR EMPLEADO
# =========================
empleado_df = df[
    df[COL_NOMINA].astype(str).str.strip() == nomina.strip()
]

if empleado_df.empty:
    st.error("No encontrado")
    st.stop()

fila = empleado_df.iloc[0]
nombre = fila[COL_NOMBRE]
proceso = fila.iloc[3]

col1, col2 = st.columns([6,1])

with col1:
    st.image("logo.png", width=120)

with col2:
    if st.button("Cerrar sesión"):
        st.session_state.nomina = None
        st.rerun()

st.markdown(f"## 👤 {nombre}")
filtro_activo = st.toggle("🚀 Por Vencer / Vencido")

st.markdown("---")

# =========================
# CONFIGURACIÓN DE CURSOS (CON RANGOS)
# =========================
categorias = {
    "CURSOS TÉCNICOS": [(195, 259), (295, 314)],
    "CURSOS DE SEGURIDAD": [(30, 164)],
    "CURSOS EXTERNOS": [(5, 29), (295, 314), (320, 384), (395,439)],
    "CURSOS COMPLEMENTARIOS": [(165, 194), (260, 284)]
}

rangos_con_certificado = [
    (18, 23),
    (24, 29) # externos (bloques de 6)
]

def icono_estatus(val):
    val = str(val).lower()

    if "vigente" in val or "ok" in val:
        return "🟢 Vigente"

    if "proximo" in val or "por vencer" in val or "vence" in val:
        return "🟡 Por vencer"

    if "vencida" in val or "expirado" in val:
        return "🔴 Vencido"

    return val

# =========================
# FUNCIÓN PARA EXTRAER CURSOS
# =========================
def obtener_cursos(rangos):
    cursos = []

    for col_inicio, col_fin in rangos:

        for col in range(col_inicio, col_fin):

            nombre_curso = fila_cursos.iloc[col]

            if not isinstance(nombre_curso, str) or nombre_curso.strip() == "":
                continue

            vencimiento = None
            estatus = None
            observaciones = None
            certificado = None

            # 🔹 VENCIMIENTO (único que cambia en especiales)
            try:
                if any(inicio <= col < fin for inicio, fin in rangos_con_certificado):
                    vencimiento = pd.to_datetime(fila.iloc[col + 3], errors="coerce")
                else:
                    vencimiento = pd.to_datetime(fila.iloc[col + 2], errors="coerce")

                vencimiento = vencimiento.date() if pd.notna(vencimiento) else None
            except:
                pass

            # 🔹 ESTATUS (solo cambia en cursos con certificado)
            try:
                if any(inicio <= col < fin for inicio, fin in rangos_con_certificado):
                    estatus = fila.iloc[col + 5]
                else:
                    estatus = fila.iloc[col + 4]
            except:
                pass

            # 🔹 OBSERVACIONES (NO SE TOCA)
            try:
                observaciones = fila.iloc[col + 0]
            except:
                pass

            # 🔥 SOLO PARA RANGOS ESPECIALES
            if any(inicio <= col < fin for inicio, fin in rangos_con_certificado):
                try:
                    certificado = fila.iloc[col + 1]  # ajusta si no coincide
                except:
                    pass

            curso_dict = {
                "Curso": nombre_curso,
                "Vencimiento": vencimiento,
                "Estatus": estatus,
                "Observaciones": observaciones
            }

            # agregar columna solo si aplica
            if any(inicio <= col < fin for inicio, fin in rangos_con_certificado):
                curso_dict["Cert/Folio"] = certificado

            cursos.append(curso_dict)

    return pd.DataFrame(cursos)

# =========================
# BOTÓN DESCARGA PDF (FIX)
# =========================
from fpdf import FPDF

TABLE_WIDTH = 270
PAGE_WIDTH = 297

def generar_pdf(nombre, datos_dict, nomina="N/A", proceso="N/A"):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    
    # =========================
    # 🔰 LOGO
    # =========================
    try:
        pdf.image("logo.png", x=12, y=12, w=25)
    except:
        pass

    # =========================
    # 🧾 MARCO DEL ENCABEZADO
    # =========================
    pdf.set_draw_color(0, 0, 0)

    # =========================
    # 📄 DATOS DERECHA (código)
    # =========================
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(230, 12)
    pdf.cell(50, 5, "CH-04-FO-39", align="R")

    pdf.set_xy(230, 17)
    pdf.cell(50, 5, "Autor: MEP/CH", align="R")

    pdf.set_xy(230, 22)
    pdf.cell(50, 5, "Página 1 de 1", align="R")

    # =========================
    # 🏢 EMPRESA
    # =========================
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_xy(50, 12)
    pdf.cell(180, 6, "Materiales y Equipo Petrolero S.A. de C.V.", align="C")

    # =========================
    # 🟢 TÍTULO
    # =========================
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(0, 128, 0)
    pdf.set_xy(50, 18)
    pdf.cell(180, 7, "Kardex de Capacitación Laboral", align="C")

    pdf.set_text_color(0, 0, 0)

    # =========================
    # 📅 CONTROL DE DOCUMENTO
    # =========================
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(50, 30)
    pdf.cell(180, 5,
        "Elaboración: 10-may-21                                Revisión: 20-abr-26                                       Emisión: 22-abr-26                                       Versión: 02                                       Idioma: ES                                       Página 1 de 1",
        align="C"
    )
    # =========================
    # 🔲 LÍNEAS NEGRAS (FORMATO FINAL)
    # =========================
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.8)

    start_x = (PAGE_WIDTH - TABLE_WIDTH) / 3
    end_x = start_x + TABLE_WIDTH

    pdf.line(start_x, 35, end_x, 35)

    # 🔁 REGRESAR A NEGRO PARA EL RESTO DEL PDF
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    
    # =========================
    # 👤 DATOS DEL COLABORADOR
    # =========================
    pdf.set_xy(10, 36)

    pdf.set_font("Helvetica", "", 10)

    y = pdf.get_y()

    # Colaborador
    pdf.set_xy(10, y)
    pdf.cell(60, 6, "Colaborador:", border=0)
    pdf.line(35, y + 6, 100, y + 6)

    # Nombre
    pdf.set_xy(36, y)
    pdf.cell(60, 6, str(nombre), border=0)

    # Nómina
    pdf.set_xy(105, y)
    pdf.cell(40, 6, "Núm. nómina:", border=0)
    pdf.line(135, y + 6, 190, y + 6)

    pdf.set_xy(136, y)
    pdf.cell(40, 6, str(nomina), border=0)

    # Proceso
    pdf.set_xy(195, y)
    pdf.cell(30, 6, "Proceso:", border=0)
    pdf.line(220, y + 6, end_x, y + 6)

    pdf.set_xy(221, y)
    pdf.cell(60, 6, str(proceso), border=0)

    pdf.ln(10)

    # =========================
    # 📊 TABLAS
    # =========================
    GRIS = (200, 200, 200)
    for categoria, df in datos_dict.items():

        start_x = (PAGE_WIDTH - TABLE_WIDTH) / 3
        pdf.set_x(start_x)

        # 👉 SOLO aplicar nuevo formato desde SEGURIDAD en adelante
        if categoria in ["CURSOS TÉCNICOS", "CURSOS DE SEGURIDAD", "CURSOS EXTERNOS", "CURSOS COMPLEMENTARIOS"]:

            # ⚪ BARRA GRIS (título de sección)
            pdf.set_fill_color(*GRIS)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_x(start_x)
            pdf.cell(TABLE_WIDTH, 8, categoria, ln=True, fill=True, align="L")

            pdf.ln(1)

            columnas = df.columns.tolist()

            # 🔹 Anchos tipo reporte (más ordenado)
            if categoria == "CURSOS EXTERNOS":
                columnas = ["Curso", "Cert/Folio", "Vencimiento", "Estatus", "Observaciones"]

                col_widths = [
                    TABLE_WIDTH * 0.35,  # Curso
                    TABLE_WIDTH * 0.15,  # Cert/Folio
                    TABLE_WIDTH * 0.20,  # Vencimiento
                    TABLE_WIDTH * 0.15,  # Estatus
                    TABLE_WIDTH * 0.15   # Observaciones
                ]
            else:
                col_widths = [
                    TABLE_WIDTH * 0.50,
                    TABLE_WIDTH * 0.20,
                    TABLE_WIDTH * 0.15,
                    TABLE_WIDTH * 0.15
                ]

            # 🔹 Encabezados
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_fill_color(230, 230, 230)
            pdf.set_x(start_x)
            for i, col in enumerate(columnas):
                txt = str(col).encode("latin-1", "ignore").decode("latin-1")
                pdf.cell(col_widths[i], 7, txt, border=1, fill=True)
            pdf.ln()

            # 🔹 Filas
            pdf.set_font("Helvetica", "", 8)

            for _, row in df.iterrows():
                pdf.set_x(start_x)

                estatus = str(row.get("Estatus", "")).lower()

                # 🎨 color por fila completa (más limpio como tu imagen)
                if "vigente" in estatus:
                    pdf.set_fill_color(198, 239, 206)
                elif "por vencer" in estatus:
                    pdf.set_fill_color(255, 235, 156)
                elif "vencido" in estatus:
                    pdf.set_fill_color(255, 199, 206)
                else:
                    pdf.set_fill_color(255, 255, 255)

                for i, col in enumerate(columnas):
                    valor = str(row.get(col, ""))[:100]
                    valor = valor.encode("latin-1", "ignore").decode("latin-1")

                    pdf.cell(col_widths[i], 6, valor, border=1, fill=True)

                pdf.ln()

            pdf.ln(6)
        else:
            # 👉 lo técnico lo dejas como ya lo tienes
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, categoria, ln=True)
            pdf.In(3)
            
    return pdf.output(dest="S").encode("latin-1")


# 🔘 BOTÓN REAL
if st.button("📄 Descargar Kardex de Capacitación Laboral"):

    datos_export = {}
    for categoria, cursos_base in categorias.items():

        df_export = obtener_cursos(cursos_base).copy()

        if categoria == "CURSOS EXTERNOS" and "Cert/Folio" in df_export.columns:
            df_export["Cert/Folio"] = df_export["Cert/Folio"].fillna("")

        if "Observaciones" in df_export.columns:
            df_export["Observaciones"] = df_export["Observaciones"].fillna("")

        if "Estatus" in df_export.columns:
            df_export["Estatus"] = df_export["Estatus"].apply(icono_estatus)

        if "Vencimiento" in df_export.columns:
            df_export = df_export[df_export["Vencimiento"].notna()]

        datos_export[categoria] = df_export

    pdf_bytes = generar_pdf(
        nombre,
        datos_export,
        nomina=nomina,
        proceso=proceso
    )

    st.download_button(
        label="⬇️ Descargar PDF",
        data=pdf_bytes,
        file_name=f"Kardex_{nombre}.pdf",
        mime="application/pdf"
    )
    
SALTO = 5 # columnas por curso

# estructura del bloque
OFFSET_CURSO = 4
OFFSET_VENCIMIENTO = 3
OFFSET_ESTATUS = 1
OFFSET_OBSERVACIONES = 5

# =========================
# MOSTRAR POR CATEGORÍA
# =========================
from datetime import datetime

def calcular_estado(fecha):
    if pd.isna(fecha):
        return "SIN FECHA"

    hoy = datetime.now().date()
    diff = (fecha - hoy).days

    if diff < -0:
        return "VENCIDO"
    elif diff <= 90:
        return "POR VENCER"
    else:
        return "VIGENTE"


for categoria, cursos_base in categorias.items():

    df_cat = obtener_cursos(cursos_base).copy()
    df_cat = df_cat[
        df_cat["Curso"].notna() &
        (df_cat["Curso"].astype(str).str.strip() != "")
    ]
    # -------------------------
    # LIMPIEZA
    # -------------------------
    if categoria == "CURSOS EXTERNOS" and "Cert/Folio" in df_cat.columns:
        df_cat["Cert/Folio"] = df_cat["Cert/Folio"].fillna("")

    if "Observaciones" in df_cat.columns:
        df_cat["Observaciones"] = df_cat["Observaciones"].fillna("")

    # -------------------------
    # ASEGURAR VENCIMIENTO + ESTADO (FIX EXTERNOS)
    # -------------------------
    if "Vencimiento" in df_cat.columns:
        # 👇 ESTA LÍNEA ES LA IMPORTANTE (PÉGALA AQUÍ)
        df_cat["Vencimiento"] = pd.to_datetime(df_cat["Vencimiento"], errors="coerce").dt.date

        df_cat = df_cat.copy()
        df_cat["Vencimiento"] = df_cat["Vencimiento"]

    # -------------------------
    # FILTRO SOLO CON ESTATUS DEL EXCEL
    # -------------------------
    if filtro_activo and "Estatus" in df_cat.columns:

        estatus = df_cat["Estatus"].fillna("").astype(str).str.lower()

        df_cat = df_cat[
        estatus.str.contains("venc", na=False) |
        estatus.str.contains("por vencer", na=False) |
        estatus.str.contains("vence", na=False)
    ]
        df_cat = df_cat[df_cat["Curso"].notna()]
    # -------------------------
    # EVITAR TABLAS VACÍAS
    # -------------------------
    if df_cat.empty:
        continue
    df_cat = df_cat[df_cat["Vencimiento"].notna()]
    # -------------------------
    # ESTATUS VISUAL
    # -------------------------
    if "Estatus" in df_cat.columns:
        df_cat["Estatus"] = df_cat["Estatus"].apply(icono_estatus)
    df_cat = df_cat.dropna(how="all")
    # -------------------------
    # MOSTRAR
    # -------------------------
    st.markdown(f"## 📂 {categoria}")
    st.dataframe(df_cat, use_container_width=True)
