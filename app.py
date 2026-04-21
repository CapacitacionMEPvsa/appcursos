import streamlit as st
import pandas as pd

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
nomina = st.text_input("Ingresa tu número de nómina")

if not nomina:
    st.stop()

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

st.markdown(f"## 👤 {nombre}")

# =========================
# CONFIGURACIÓN DE CURSOS
# =========================
# 👉 AQUÍ defines dónde empieza cada tipo
categorias = {
    "CURSOS TÉCNICOS": 4,        # F
    "CURSOS DE SEGURIDAD": 65,   # ejemplo (ajústalo)
    "CURSOS EXTERNOS": 125,      # ejemplo
    "CURSOS COMPLEMENTARIOS": 185 # ejemplo
}

# estructura del bloque
OFFSET_CURSO = 1
OFFSET_VENCIMIENTO = 2
OFFSET_ESTATUS = 4
OFFSET_OBSERVACIONES = 0

SALTO = 6  # columnas por curso

# =========================
# FUNCIÓN PARA EXTRAER CURSOS
# =========================
def obtener_cursos(col_inicio):
    cursos = []
    num_cols = df.shape[1]

    for col in range(col_inicio, num_cols, SALTO):

        if col + OFFSET_ESTATUS >= num_cols:
            break

        nombre_curso = fila_cursos.iloc[col + OFFSET_CURSO]

        if pd.isna(nombre_curso):
            continue

        curso = {
            "Curso": nombre_curso,
            "Vencimiento": fila.iloc[col + OFFSET_VENCIMIENTO],
            "Estatus": fila.iloc[col + OFFSET_ESTATUS],
            "Observaciones": fila.iloc[col + OFFSET_OBSERVACIONES],
            "Capacitación": "Tomar Curso" if str(fila.iloc[col + OFFSET_ESTATUS]).upper() == "PENDIENTE" else ""
        }

        cursos.append(curso)

    return pd.DataFrame(cursos)

# =========================
# MOSTRAR POR CATEGORÍA
# =========================
for categoria, col_inicio in categorias.items():

    df_cat = obtener_cursos(col_inicio)

    if df_cat.empty:
        continue

    st.markdown(f"## 📂 {categoria}")

    st.dataframe(
        df_cat,
        use_container_width=True
    )
