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
    header=[1, 2]
)

# Limpiar columnas
df.columns = df.columns.map(lambda x: f"{x[0]}|{x[1]}" if pd.notna(x[1]) else x[0])
df = df.reset_index(drop=True)
df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]

# =========================
# DETECTAR COLUMNAS (FIX ROBUSTO)
# =========================
def buscar_columna(nombre):
    for col in df.columns:
        if nombre.lower() in str(col).lower():
            return col
    return None

COL_NOMINA = buscar_columna("nomina")
COL_NOMBRE = buscar_columna("nombre")
COL_PROCESO = buscar_columna("proceso")

# 🔴 FALLBACK IMPORTANTE (evita error)
if not COL_NOMINA:
    COL_NOMINA = df.columns[0]

if not COL_NOMBRE:
    COL_NOMBRE = df.columns[1]

# DEBUG
st.write("Columnas detectadas:")
st.write("Nómina:", COL_NOMINA)
st.write("Nombre:", COL_NOMBRE)
st.write("Proceso:", COL_PROCESO)

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

        except:
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

df_final = pd.concat(cursos, ignore_index=True)

# =========================
# VALIDAR VACÍO
# =========================
if df_final.empty:
    st.warning("No se encontraron cursos para este trabajador")
    st.stop()

# =========================
# FORMATO FECHA
# =========================
df_final["vencimiento"] = pd.to_datetime(df_final["vencimiento"], errors="coerce")
df_final["vencimiento"] = df_final["vencimiento"].dt.strftime("%d/%m/%Y")

# =========================
# SEMAFORO (ESTATUS)
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
    st.warning(f"⚠️ Tienes {len(por_vencer)} curso(s) por vencer")

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
