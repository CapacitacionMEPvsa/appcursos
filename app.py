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
# CARGA EXCEL (YA FUNCIONAL)
# =========================
df = pd.read_excel(
    "BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx",
    header=None
)

df.columns = df.iloc[1]
df = df[2:].reset_index(drop=True)

df.columns = df.columns.astype(str).str.strip()

# =========================
# COLUMNAS FIJAS
# =========================
COL_NOMINA = "Nómina"
COL_NOMBRE = "Nombre del Colaborador"

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

# =========================
# LIMPIEZA DUPLICADOS
# =========================
empleado = empleado.loc[:, ~empleado.columns.duplicated()]
empleado = empleado.dropna(axis=1, how="all")

# =========================
# 🔥 AQUÍ DEFINES QUÉ COLUMNAS QUIERES VER
# =========================
columnas_visibles = [
    COL_NOMINA,
    COL_NOMBRE,
    "categoria",
    "curso",
    "vencimiento",
    "estatus"
]

# =========================
# VALIDACIÓN DE COLUMNAS
# =========================
columnas_finales = [c for c in columnas_visibles if c in empleado.columns]

# =========================
# MOSTRAR SOLO LO NECESARIO
# =========================
st.markdown("## 📋 Mis cursos")

st.dataframe(
    empleado[columnas_finales],
    use_container_width=True
)
