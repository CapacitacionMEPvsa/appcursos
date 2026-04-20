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
# 🔥 CARGA CORRECTA DEL EXCEL (CLAVE)
# =========================
df = pd.read_excel(
    "BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx",
    header=2
)

# limpiar columnas
df.columns = df.columns.astype(str).str.strip()

# =========================
# COLUMNAS FIJAS
# =========================
COL_NOMINA = "Nómina"
COL_NOMBRE = "Nombre del Colaborador"

if COL_NOMINA not in df.columns or COL_NOMBRE not in df.columns:
    st.error("Columnas no detectadas correctamente")
    st.write(df.columns.tolist())
    st.stop()

# =========================
# INPUT
# =========================
nomina = st.text_input("Ingresa tu número de nómina")

if not nomina:
    st.stop()

# =========================
# BLOQUES (SE MANTIENE TU LÓGICA)
# =========================
bloques = [
    {"nombre": "CERTIFICACIONES TECNICAS", "inicio": 20, "tipo": "tecnico"},
    {"nombre": "ANEXO SSPA", "inicio": 88, "tipo": "seguridad"},
    {"nombre": "COMPETENCIAS TECNICAS BASICAS", "inicio": 200, "tipo": "tecnico"},
]

# =========================
# EXTRACCIÓN SEGURA
# =========================
cursos = []

for b in bloques:

    try:
        base = df[[COL_NOMINA, COL_NOMBRE]].copy()
        base.columns = ["nomina", "nombre"]

        temp = base.copy()

        temp["curso"] = df.iloc[:, b["inicio"]]
        temp["vencimiento"] = df.iloc[:, b["inicio"] + 1]
        temp["estatus"] = df.iloc[:, b["inicio"] + 2]

        temp["categoria"] = b["nombre"]
        temp["tipodecurso"] = b["tipo"]

        cursos.append(temp)

    except Exception:
        continue

if len(cursos) == 0:
    st.error("No se pudieron construir los cursos. Revisa estructura del Excel.")
    st.stop()

df_final = pd.concat(cursos, ignore_index=True)

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

# =========================
# UI
# =========================
st.markdown(f"## 👤 {nombre}")

st.dataframe(
    empleado[["categoria", "curso", "vencimiento", "estatus"]],
    use_container_width=True
)
