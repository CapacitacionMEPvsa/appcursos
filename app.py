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
def extraer_bloque(emp, inicio, fin, categoria, obs_col=33):

    data = []

    for col in range(inicio, fin):

        if col >= len(emp.columns):
            continue

        curso = emp.iloc[:, col]

        # saltar columnas vacías
        if curso.isna().all():
            continue

        data.append(pd.DataFrame({
            "nomina": emp[COL_NOMINA].values,
            "nombre": emp[COL_NOMBRE].values,
            "proceso": emp[COL_PROCESO].values if COL_PROCESO else None,
            "categoria": categoria,
            "curso": curso,
            "vencimiento": emp.iloc[:, col + 1] if col + 1 < len(emp.columns) else None,
            "estatus": emp.iloc[:, col + 2] if col + 2 < len(emp.columns) else None,
            "observaciones": emp.iloc[:, obs_col] if obs_col < len(emp.columns) else None
        }))

    if data:
        return pd.concat(data, ignore_index=True)

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
cursos = [c for c in cursos if not c.empty]

if len(cursos) == 0:
    st.error("No se encontraron cursos para este trabajador")
    st.stop()

df_final = pd.concat(cursos, ignore_index=True)
df_final.columns = df_final.columns.astype(str).str.strip()

# limpiar vacíos
df_final = df_final[df_final["curso"].notna()]

# =========================
# MOSTRAR
# =========================
st.markdown("## 📋 Mis cursos")

st.dataframe(
    df_final[[
        "curso",
        "inicio",
        "emision",
        "vencimiento",
        "estatus",
        "observaciones"
    ]],
    use_container_width=True
)

from datetime import datetime

# =========================
# FORMATO FECHA
# =========================
df_final["vencimiento"] = pd.to_datetime(df_final["vencimiento"], errors="coerce")

# mostrar fecha completa bonita
df_final["vencimiento"] = df_final["vencimiento"].dt.strftime("%d/%m/%Y")

# =========================
# CALCULO SEMAFORO
# =========================
hoy = pd.Timestamp.today().normalize()

def calcular_estatus(fecha):
    try:
        fecha_dt = pd.to_datetime(fecha, dayfirst=True)
    except:
        return "N/A"

    if pd.isna(fecha_dt):
        return "N/A"

    dias = (fecha_dt - hoy).days

    if dias < 0:
        return "🔴 VENCIDO"
    elif dias <= 30:
        return "🟠 POR VENCER"
    else:
        return "🟢 VIGENTE"

df_final["estatus"] = df_final["vencimiento"].apply(calcular_estatus)
