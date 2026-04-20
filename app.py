import streamlit as st
import pandas as pd
from datetime import datetime
import io

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(layout="wide")
st.title("Consulta de Cursos")

# =========================
# CARGA EXCEL (SEGURO)
# =========================
df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx")

# limpiar columnas
df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.replace("\n", "")
    .str.replace("\xa0", " ")
)

# =========================
# DETECCIÓN DIRECTA (YA SIMPLIFICADO EN TU EXCEL)
# =========================
COL_NOMINA = "Nómina"
COL_NOMBRE = "Nombre del Colaborador"

if COL_NOMINA not in df.columns or COL_NOMBRE not in df.columns:
    st.error("Revisa tu Excel: faltan columnas requeridas")
    st.write(df.columns.tolist())
    st.stop()

# =========================
# INPUT (PRIMERO SIEMPRE)
# =========================
nomina = st.text_input("Ingresa tu número de nómina")

if not nomina:
    st.info("Ingresa tu número de nómina para continuar")
    st.stop()

# =========================
# BLOQUES (TU ESTRUCTURA ORIGINAL)
# =========================
bloques = [
    {"nombre": "CERTIFICACIONES TECNICAS", "inicio": 20, "tipo": "tecnico"},
    {"nombre": "ANEXO SSPA", "inicio": 88, "tipo": "seguridad"},
    {"nombre": "COMPETENCIAS TECNICAS BASICAS", "inicio": 200, "tipo": "tecnico"},
]

# =========================
# PROCESAMIENTO SEGURO
# =========================
try:
    cursos = []

    base = df[[COL_NOMINA, COL_NOMBRE]].copy()
    base.columns = ["nomina", "nombre"]

    for b in bloques:

        temp = base.copy()

        temp["curso"] = df.iloc[:, b["inicio"]]
        temp["vencimiento"] = df.iloc[:, b["inicio"] + 1]
        temp["estatus"] = df.iloc[:, b["inicio"] + 2]

        temp["categoria"] = b["nombre"]
        temp["tipodecurso"] = b["tipo"]

        cursos.append(temp)

    df_final = pd.concat(cursos, ignore_index=True)
    df_final = df_final[df_final["curso"].notna()]

except Exception as e:
    st.error("Error procesando los cursos")
    st.write(str(e))
    st.stop()

# =========================
# FILTRO POR NÓMINA
# =========================
empleado = df_final[
    df_final["nomina"].astype(str).str.strip() == nomina.strip()
].copy()

if empleado.empty:
    st.error("No se encontraron registros para esta nómina")
    st.stop()

nombre = empleado.iloc[0]["nombre"]

# =========================
# HEADER
# =========================
col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.png", width=120)

with col2:
    st.markdown(f"## 👤 {nombre}")

# =========================
# BOTONES
# =========================
colA, colB = st.columns([1, 2])

with colA:
    descargar = st.button("📄 Descargar PDF")

with colB:
    filtro = st.toggle("🚀 Solo pendientes o por vencer")

# =========================
# FECHAS Y ESTATUS
# =========================
empleado["vencimiento"] = pd.to_datetime(
    empleado["vencimiento"],
    errors="coerce"
).dt.date

hoy = datetime.today().date()

def calcular_estatus(fecha):
    if pd.isna(fecha):
        return "Pendiente"
    dias = (fecha - hoy).days
    if dias < 0:
        return "Vencido"
    elif dias <= 30:
        return "Por vencer"
    else:
        return "Vigente"

empleado["estatus"] = empleado["estatus"].fillna(
    empleado["vencimiento"].apply(calcular_estatus)
)

# =========================
# FILTRO
# =========================
if filtro:
    empleado = empleado[
        empleado["estatus"].isin(["Vencido", "Por vencer", "Pendiente"])
    ]

# =========================
# TABLA
# =========================
st.markdown("## 📋 Cursos del trabajador")

st.dataframe(
    empleado[[
        "categoria",
        "curso",
        "vencimiento",
        "estatus"
    ]],
    use_container_width=True
)

# =========================
# PDF (BÁSICO SIN CAMBIOS)
# =========================
def generar_pdf(data, nombre):
    buffer = io.BytesIO()
    buffer.write(f"Kardex de {nombre}".encode())
    buffer.seek(0)
    return buffer

if descargar:
    pdf = generar_pdf(empleado, nombre)

    st.download_button(
        label="Descargar PDF",
        data=pdf,
        file_name="kardex.pdf",
        mime="application/pdf"
    )
