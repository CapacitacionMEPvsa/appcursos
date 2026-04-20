import streamlit as st
import pandas as pd
from datetime import datetime

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(layout="wide")
st.title("Consulta de Cursos")

# =========================
# CARGA EXCEL
# =========================
df = pd.read_excel(
    "BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx",
    header=None
)

df.columns = df.iloc[1]
df = df[2:].reset_index(drop=True)
df.columns = df.columns.astype(str).str.strip()

# =========================
# COLUMNAS BASE
# =========================
COL_NOMINA = "Nómina"
COL_NOMBRE = "Nombre del Colaborador"
COL_PROCESO = "Proceso"

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
# 🔥 CURSOS (YA MAPEADO CORRECTAMENTE)
# =========================
data = pd.DataFrame()

data["nomina"] = empleado[COL_NOMINA]
data["nombre"] = empleado[COL_NOMBRE]
data["proceso"] = empleado[COL_PROCESO]

# =========================
# ANEXO SSPA (TU CASO)
# =========================
data["categoria"] = "ANEXO SSPA"
data["curso"] = df.iloc[:, 34]
data["vencimiento"] = df.iloc[:, 35]
data["estatus"] = df.iloc[:, 3]

# =========================
# FILTRAR SOLO ESTE EMPLEADO
# =========================
data = data[data["nomina"].astype(str).str.strip() == nomina.strip()]

# limpiar vacíos
data = data[data["curso"].notna()]

# =========================
# LIMPIEZA FINAL
# =========================
data = data.loc[:, ~data.columns.duplicated()]
data = data.dropna(axis=1, how="all")

# =========================
# COLUMNAS A MOSTRAR
# =========================
columnas_visibles = [
    "Curso",
    "Vencimiento",
    "Estatus",
    "Observaciones",
]

columnas_finales = [c for c in columnas_visibles if c in data.columns]

# =========================
# MOSTRAR
# =========================
st.markdown("## 📋 Mis cursos")

st.dataframe(
    data[columnas_finales],
    use_container_width=True
)
