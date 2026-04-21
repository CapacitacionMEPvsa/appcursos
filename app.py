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
# CONFIGURACIÓN DE CURSOS (CON RANGOS)
# =========================
categorias = {
    "CURSOS TÉCNICOS": (201, 265),
    "CURSOS DE SEGURIDAD": (18, 175),
    "CURSOS EXTERNOS": (21, 32),
    "CURSOS COMPLEMENTARIOS": (266, df.shape[1])
}

# estructura del bloque
OFFSET_CURSO = 1
OFFSET_VENCIMIENTO = 3
OFFSET_ESTATUS = 5
OFFSET_OBSERVACIONES = 1

SALTO = 6  # columnas por curso

# =========================
# FUNCIÓN PARA EXTRAER CURSOS
# =========================
def obtener_cursos(col_inicio, col_fin):
    cursos = []

    for col in range(col_inicio, col_fin, SALTO):

        if col + OFFSET_ESTATUS >= df.shape[1]:
            break

        nombre_curso = fila_cursos.iloc[col + OFFSET_CURSO]

        if pd.isna(nombre_curso):
            continue

        curso = {
            "Curso": nombre_curso,
            "Vencimiento": fila.iloc[col + OFFSET_VENCIMIENTO],
            "Estatus": fila.iloc[col + OFFSET_ESTATUS],
            "Observaciones": fila.iloc[col + OFFSET_OBSERVACIONES]
        }

        cursos.append(curso)

    return pd.DataFrame(cursos)

# =========================
# MOSTRAR POR CATEGORÍA
# =========================
for categoria, (col_inicio, col_fin) in categorias.items():

    df_cat = obtener_cursos(col_inicio, col_fin)

    if df_cat.empty:
        continue

    st.markdown(f"## 📂 {categoria}")

    st.dataframe(
        df_cat,
        use_container_width=True
    )
