import streamlit as st
import pandas as pd
from datetime import datetime
import io

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("Consulta de Cursos")

# =========================
# 🔥 LECTURA CORRECTA DEL EXCEL (CRÍTICO)
# =========================
df = pd.read_excel(
    "BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx",
    header=None
)

# 🔥 FORZAR HEADERS REALES (SEGÚN TU EXCEL)
df.columns = df.iloc[1]  # fila 2 como encabezado real
df = df[2:].reset_index(drop=True)

# limpiar columnas
df.columns = df.columns.astype(str).str.strip()

# =========================
# DEBUG (USAR SOLO UNA VEZ SI FALLA)
# =========================
# st.write(df.columns.tolist())
# st.stop()

# =========================
# COLUMNAS FIJAS
# =========================
COL_NOMINA = "Nómina"
COL_NOMBRE = "Nombre del Colaborador"

if COL_NOMINA not in df.columns or COL_NOMBRE not in df.columns:
    st.error("No se detectaron columnas correctas")
    st.write(df.columns.tolist())
    st.stop()

# =========================
# INPUT
# =========================
nomina = st.text_input("Ingresa tu número de nómina")

if not nomina:
    st.stop()

# =========================
# FILTRAR EMPLEADO
# =========================
empleado = df[df[COL_NOMINA].astype(str).str.strip() == nomina.strip()]

if empleado.empty:
    st.error("No encontrado")
    st.stop()

nombre = empleado.iloc[0][COL_NOMBRE]

st.markdown(f"## 👤 {nombre}")

st.dataframe(empleado)
