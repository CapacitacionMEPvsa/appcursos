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

# =========================
# MAPEO AUTOMÁTICO DE CURSOS
# =========================
encabezados = (
    df_raw.iloc[1]
    .astype(str)
    .str.replace("\n", " ")
    .str.replace("  ", " ")
    .str.strip()
)
for categoria, lista in categorias.items():

    df_cat = obtener_cursos_por_categoria(fila, lista)

    if isinstance(df_cat, pd.DataFrame) and not df_cat.empty:

        st.markdown(f"## 📂 {categoria}")
        st.dataframe(df_cat, use_container_width=True)
mapa_cursos = {}

for i, val in enumerate(encabezados):
    if isinstance(val, str) and val.strip() != "" and val != "nan":
        mapa_cursos[val.strip()] = i
st.write(list(mapa_cursos.keys()))

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
    "CURSOS TÉCNICOS": [
        "CONOCIMIENTO DE LAS HERRAMIENTAS DEL SERVICIO INTEGRAL",
        "PROCEDIMIENTOS DE TRABAJO"
    ],
    "CURSOS DE SEGURIDAD": [
        "EQUIPOS Y HERRAMIENTAS PARA INTRODUCCION DE TUBERIAS"
    ],
    "CURSOS EXTERNOS": [
        "APRITE DE TUBERIAS DE REVESTIMIENTO"
    ],
    "CURSOS COMPLEMENTARIOS": [
        "OTRO BLOQUE"  # cámbialo por el nombre real si existe
    ]
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
SALTO = 6

def obtener_cursos_por_nombre(fila, nombres_cursos):
    ...

# =========================
# MOSTRAR POR CATEGORÍA
# =========================
    )
