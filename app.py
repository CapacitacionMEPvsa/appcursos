import streamlit as st
import pandas as pd

# =========================
# CONFIG
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
# 🔥 FUNCION PARA EXTRAER BLOQUES
# =========================
def extraer_bloque(df_emp, inicio, fin, paso=5):
    data = []
    columnas = list(df_emp.columns)

    for col in range(inicio, fin, paso):

        if col + 4 >= len(columnas):
            continue

        try:
            curso = columnas[col].split("|")[0]

            temp = pd.DataFrame({
                "curso": curso,
                "inicio": df_emp.iloc[:, col],
                "emision": df_emp.iloc[:, col + 1],
                "vencimiento": df_emp.iloc[:, col + 2],  # 👈 antes vigencia
                "estatus_excel": df_emp.iloc[:, col + 4],  # por si lo necesitas
                "observaciones": df_emp.iloc[:, col - 1] if col - 1 >= 0 else "N/A"  # 👈 ANTERIOR
            })

            data.append(temp)

        except:
            continue

    if data:
        df_out = pd.concat(data, ignore_index=True)

        # reemplazar vacíos
        df_out = df_out.fillna("N/A")

        return df_out

    return pd.DataFrame()

# =========================
# 🔥 CONSTRUIR TODOS LOS BLOQUES
# =========================
cursos = []

# ANEXO SSPA
cursos.append(extraer_bloque(empleado, 33, 200, "ANEXO SSPA"))

# CURSOS EXTERNOS
cursos.append(extraer_bloque(empleado, 6, 32, "CURSOS EXTERNOS"))
cursos.append(extraer_bloque(empleado, 297, 381, "CURSOS EXTERNOS"))

# CURSOS TÉCNICOS
cursos.append(extraer_bloque(empleado, 201, 265, "CURSOS TECNICOS"))
cursos.append(extraer_bloque(empleado, 289, 296, "CURSOS TECNICOS"))

# COMPLEMENTARIOS
cursos.append(extraer_bloque(empleado, 266, 288, "CURSOS COMPLEMENTARIOS"))

# =========================
# UNIR TODO
# =========================
df_final = pd.concat(cursos, ignore_index=True)

# limpiar vacíos
df_final = df_final[df_final["curso"].notna()]

# =========================
# MOSTRAR
# =========================
st.markdown("## 📋 Mis cursos")

st.dataframe(
    df_final[[
        "categoria",
        "curso",
        "vencimiento",
        "estatus",
        "observaciones"
    ]],
    use_container_width=True
)
