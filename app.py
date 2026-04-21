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
    "CURSOS TÉCNICOS": [(196, 260), (289, 312)],
    "CURSOS DE SEGURIDAD": [(30, 79), (80, 85),(86, 165)],
    "CURSOS EXTERNOS": [(5, 29), (296, 315), (321, 385), (396,440)],
    "CURSOS COMPLEMENTARIOS": [(166, 195), (261, 285)]
}

SALTO = 5 # columnas por curso

# estructura del bloque
OFFSET_CURSO = 4
OFFSET_VENCIMIENTO = 3
OFFSET_ESTATUS = 1
OFFSET_OBSERVACIONES = 5


# =========================
# FUNCIÓN PARA EXTRAER CURSOS
# =========================
def obtener_cursos(rangos):
    cursos = []

    for col_inicio, col_fin in rangos:

        for col in range(col_inicio, col_fin):

            nombre_curso = fila_cursos.iloc[col]

            # detectar columnas que realmente son cursos
            if not isinstance(nombre_curso, str) or nombre_curso.strip() == "":
                continue

            # intentar leer datos cercanos (flexible)
            vencimiento = None
            estatus = None
            observaciones = None

            try:
                vencimiento = pd.to_datetime(fila.iloc[col + 2], errors="coerce")
                vencimiento = vencimiento.date() if pd.notna(vencimiento) else None
            except:
                pass

            try:
                estatus = fila.iloc[col + 4]
            except:
                pass

            try:
                observaciones = fila.iloc[col + 0]
            except:
                pass

            cursos.append({
                "Curso": nombre_curso,
                "Vencimiento": vencimiento,
                "Estatus": estatus,
                "Observaciones": observaciones
            })

    return pd.DataFrame(cursos)

# =========================
# MOSTRAR POR CATEGORÍA
# =========================
for categoria, cursos_base in categorias.items():

    df_cat = obtener_cursos(cursos_base)
    df_cat = df_cat[df_cat["Vencimiento"].notna()]

    if not isinstance(df_cat, pd.DataFrame) or df_cat.empty:
        continue

    st.markdown(f"## 📂 {categoria}")
    st.dataframe(df_cat, use_container_width=True)
