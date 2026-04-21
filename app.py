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
    "CURSOS TÉCNICOS": [(198, 262), (289, 312)],
    "CURSOS DE SEGURIDAD": [(32, 81), (82, 87), (88,167)],
    "CURSOS EXTERNOS": [(5, 32), (319, 381)],
    "CURSOS COMPLEMENTARIOS": [(170, 198), (265, 288)]
}

SALTO = 5 # columnas por curso

# estructura del bloque
OFFSET_CURSO = 1
OFFSET_VENCIMIENTO = 3
OFFSET_ESTATUS = 5
OFFSET_OBSERVACIONES = 1


# =========================
# FUNCIÓN PARA EXTRAER CURSOS
# =========================
def obtener_cursos(rangos):
    cursos = []

    for col_inicio, col_fin in rangos:

        for col in range(col_inicio, col_fin):

            if col + 5 >= df.shape[1]:
                break

            nombre_curso = fila_cursos.iloc[col]

            if not isinstance(nombre_curso, str) or nombre_curso.strip() == "":
                continue

            cursos.append({
                "Curso": nombre_curso,
                "Vencimiento": fila.iloc[col],
                "Estatus": fila.iloc[col + 2] if col + 2 < df.shape[1] else None,
                "Observaciones": fila.iloc[col + 1] if col + 1 < df.shape[1] else None
            })

    return pd.DataFrame(cursos)

# =========================
# MOSTRAR POR CATEGORÍA
# =========================
for categoria, cursos_base in categorias.items():

    df_cat = obtener_cursos(cursos_base)

    if not isinstance(df_cat, pd.DataFrame) or df_cat.empty:
        continue

    st.markdown(f"## 📂 {categoria}")
    st.dataframe(df_cat, use_container_width=True)
