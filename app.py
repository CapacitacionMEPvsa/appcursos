import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("Consulta de Cursos")

# =========================
# CARGA EXCEL (CORREGIDO)
# =========================
df = pd.read_excel(
    "BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx",
    header=[1, 2]  # 👈 IMPORTANTE
)

# Unir encabezados
df.columns = df.columns.map(lambda x: f"{x[0]}|{x[1]}" if pd.notna(x[1]) else x[0])
df = df.reset_index(drop=True)

# Limpiar nombres de columnas
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
# FILTRAR TRABAJADOR
# =========================
empleado = df[df[COL_NOMINA].astype(str).str.strip() == nomina.strip()].copy()

if empleado.empty:
    st.error("No encontrado")
    st.stop()

nombre = empleado.iloc[0][COL_NOMBRE]
st.markdown(f"## 👤 {nombre}")

# =========================
# FUNCION CORREGIDA
# =========================
def extraer_bloque(df_emp, inicio, fin, paso=5):
    data = []
    columnas = list(df_emp.columns)

    for col in range(inicio, fin, paso):

        # evitar errores por límites
        if col + 4 >= len(columnas):
            continue

        try:
            # 👇 nombre del curso desde encabezado
            curso = columnas[col].split("|")[0]

            temp = pd.DataFrame({
                "curso": curso,
                "inicio": df_emp.iloc[:, col],
                "emision": df_emp.iloc[:, col + 1],
                "vigencia": df_emp.iloc[:, col + 2],
                "dias": df_emp.iloc[:, col + 3],
                "estatus": df_emp.iloc[:, col + 4],
                "observaciones": df_emp.iloc[:, 33] if 33 < len(columnas) else "N/A"
            })

            data.append(temp)

        except Exception:
            continue

    if data:
        df_out = pd.concat(data, ignore_index=True)

        # reemplazar vacíos
        df_out = df_out.fillna("N/A")

        return df_out

    return pd.DataFrame()

# =========================
# CONSTRUIR BLOQUES (AJUSTA RANGOS SI NECESARIO)
# =========================
cursos = []

cursos.append(extraer_bloque(empleado, 5, 200))   # técnicos / certificaciones
cursos.append(extraer_bloque(empleado, 200, 400)) # otros bloques

# =========================
# UNIR TODO
# =========================
df_final = pd.concat(cursos, ignore_index=True)

# eliminar filas sin datos reales
df_final = df_final[
    (df_final["inicio"] != "N/A") |
    (df_final["estatus"] != "N/A")
]

# =========================
# MOSTRAR
# =========================
st.markdown("## 📋 Mis cursos")

st.dataframe(
    df_final[[
        "curso",
        "inicio",
        "emision",
        "vigencia",
        "dias",
        "estatus",
        "observaciones"
    ]],
    use_container_width=True
)
