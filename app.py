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
headers_raw = pd.read_excel(
    "BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx",
    header=None
)

fila_cursos = headers_raw.iloc[1]
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
    {"categoria": "CERTIFICACIONES TECNICAS", "inicio": 1, "fin": df.shape[1]},
    
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
        temp["curso"] = fila_cursos[i]

        # 🔥 bloque completo del curso
        bloque = df.iloc[:, i:i+6]

        # convertir a fechas donde se pueda
        fechas = bloque.apply(pd.to_datetime, errors="coerce")

        temp["No."] = fechas.iloc[:, 1].dt.date
        
        # vencimiento (ajusta si necesitas otra columna)
        temp["vencimiento"] = fechas.iloc[:, 2].dt.date

        # estatus
        temp["estatus"] = bloque.iloc[:, -1]

        # observaciones limpias
        obs = bloque.iloc[:, 0]
        temp["observaciones"] = obs.where(
            ~obs.astype(str).str.isnumeric(), ""
        )

        cursos.append(temp)
        
df_final = pd.concat(cursos, ignore_index=True)

df_final["curso"] = df_final["curso"].fillna("Curso sin nombre")

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
# EXTRAER CURSOS (COLUMNAS FIJAS)
# =========================

cursos = []

num_cols = df.shape[1]

for col in range(5, num_cols, 6):

    # 🔥 validar que no se salga del rango
    if col + 4 >= num_cols:
        continue

    curso = {
        "curso": fila.iloc[col + 1],
        "vencimiento": fila.iloc[col + 2],
        "estatus": fila.iloc[col + 4],
        "observaciones": fila.iloc[col]
    }

    if pd.notna(curso["curso"]):
        cursos.append(curso)

df_mostrar = pd.DataFrame(cursos)
st.write("Total columnas:", num_cols)
st.write("Columnas índice:", list(range(num_cols)))
st.write("col actual:", col)


# =========================
# MOSTRAR
# =========================
st.markdown("## 📋 Mis cursos")

st.dataframe(df_mostrar, use_container_width=True)
