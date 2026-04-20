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
# 🔥 CREAR CURSOS (AQUÍ ESTÁ LO IMPORTANTE)
# =========================
bloques = [
    {"categoria": "CERTIFICACIONES TECNICAS", "inicio": 20, "fin":700},
    {"categoria": "ANEXO SSPA", "inicio": 20, "fin":700},
    {"categoria": "COMPETENCIAS TECNICAS BASICAS", "inicio": 20, "fin":700},
]

cursos = []

cursos = []

for b in bloques:
    for i in range(b["inicio"], b["fin"], 6):

        temp = df[[COL_NOMINA, COL_NOMBRE, COL_PROCESO]].copy()

        temp = temp.rename(columns={
            COL_NOMINA: "nomina",
            COL_NOMBRE: "nombre",
            COL_PROCESO: "proceso"
        })

        temp["categoria"] = b["categoria"]

        # nombre del curso
        temp["curso"] = df.columns[i]

        # datos
        temp["vencimiento"] = pd.to_datetime(
            df.iloc[:, i + 3], errors="coerce"
        ).dt.date

        temp["estatus"] = df.iloc[:, i + 5]

        temp["observaciones"] = df.iloc[:, i - 2]

        cursos.append(temp)

df_final = pd.concat(cursos, ignore_index=True)

df_final = df_final[df_final["curso"].notna()]

# =========================
# INPUT
# =========================
nomina = st.text_input("Ingresa tu número de nómina")

if not nomina:
    st.stop()

# =========================
# FILTRAR EMPLEADO
# =========================
empleado = df_final[
    df_final["nomina"].astype(str).str.strip() == nomina.strip()
]

if empleado.empty:
    st.error("No encontrado")
    st.stop()

nombre = empleado.iloc[0]["nombre"]

st.markdown(f"## 👤 {nombre}")

# =========================
# LIMPIEZA
# =========================
empleado = empleado.loc[:, ~empleado.columns.duplicated()]
empleado = empleado.dropna(axis=1, how="all")

# =========================
# COLUMNAS VISIBLES
# =========================
columnas_visibles = [
    "curso",
    "vencimiento",
    "estatus",
    "observaciones"
]

columnas_finales = [c for c in columnas_visibles if c in empleado.columns]

# =========================
# MOSTRAR CURSOS
# =========================
st.markdown("## 📋 Mis cursos")

st.dataframe(
    empleado[columnas_finales],
    use_container_width=True
)
