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
    cursos = []

    for nombre in nombres_cursos:

inicio = None

for k in mapa_cursos.keys():
    if nombre.upper() in k.upper():
        inicio = mapa_cursos[k]
        break

if inicio is None:
    continue
        inicio = mapa_cursos[nombre]

        for col in range(inicio, inicio + 100, SALTO):

            if col + 5 >= df.shape[1]:
                break

            nombre_curso = encabezados.iloc[col + 1]

            if pd.isna(nombre_curso):
                break

            cursos.append({
                "Bloque": nombre,
                "Curso": nombre_curso,
                "Observación": fila.iloc[col + 1],
                "Vencimiento": fila.iloc[col + 3],
                "Estatus": fila.iloc[col + 5],
            })

    return pd.DataFrame(cursos)
    
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
for categoria, cursos_base in categorias.items():

    df_cat = obtener_cursos_por_nombre(fila, cursos_base)

    if df_cat.empty:
        continue

    st.markdown(f"## 📂 {categoria}")
    st.dataframe(df_cat, use_container_width=True)

    if df_cat.empty:
        continue

    st.markdown(f"## 📂 {categoria}")

    st.dataframe(
        df_cat,
        use_container_width=True
    )
