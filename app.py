import streamlit as st
import pandas as pd
from datetime import datetime

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
    header=[1, 2]  # encabezados múltiples
)

# Unir encabezados
df.columns = df.columns.map(lambda x: f"{x[0]}|{x[1]}" if pd.notna(x[1]) else x[0])
df = df.reset_index(drop=True)

# Limpiar nombres
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
# FUNCION EXTRAER BLOQUES
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
                "vencimiento": df_emp.iloc[:, col + 2],
                "estatus_excel": df_emp.iloc[:, col + 4],
                "observaciones": df_emp.iloc[:, col - 1] if col - 1 >= 0 else "N/A"
            })

            data.append(temp)

        except Exception:
            continue

    if data:
        df_out = pd.concat(data, ignore_index=True)
        df_out = df_out.fillna("N/A")
        return df_out

    return pd.DataFrame()

# =========================
# CONSTRUIR BLOQUES
# =========================
cursos = []

cursos.append(extraer_bloque(empleado, 5, 200))
cursos.append(extraer_bloque(empleado, 200, 400))

# =========================
# UNIR TODO
# =========================
df_final = pd.concat(cursos, ignore_index=True)

# limpiar filas sin datos reales
df_final = df_final[
    (df_final["vencimiento"] != "N/A") |
    (df_final["estatus_excel"] != "N/A")
]

# =========================
# FORMATO FECHA
# =========================
df_final["vencimiento"] = pd.to_datetime(df_final["vencimiento"], errors="coerce")
df_final["vencimiento"] = df_final["vencimiento"].dt.strftime("%d/%m/%Y")

# =========================
# SEMAFORO = ESTATUS
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

# =========================
# ALERTAS
# =========================
vencidos = df_final[df_final["estatus"] == "🔴 VENCIDO"]
por_vencer = df_final[df_final["estatus"] == "🟠 POR VENCER"]

if not vencidos.empty:
    st.error(f"🚨 Tienes {len(vencidos)} curso(s) vencido(s)")

if not por_vencer.empty:
    st.warning(f"⚠️ Tienes {len(por_vencer)} curso(s) por vencer en los próximos 30 días")

if vencidos.empty and por_vencer.empty:
    st.success("✅ Todos tus cursos están vigentes")

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
