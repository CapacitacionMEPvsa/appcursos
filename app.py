import streamlit as st
import pandas as pd

def color_estatus(val):
    val = str(val).lower()

    if "vigente" in val or "ok" in val:
        return "background-color: #c6f6d5; color: #22543d"

    if "proximo" in val or "por vencer" in val or "vence" in val:
        return "background-color: #fefcbf; color: #744210"

    if "vencido" in val or "expirado" in val:
        return "background-color: #fed7d7; color: #742a2a"

    return ""

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
    "CURSOS TÉCNICOS": [(195, 259), (295, 314)],
    "CURSOS DE SEGURIDAD": [(30, 164)],
    "CURSOS EXTERNOS": [(3, 29), (295, 314), (320, 384), (395,439)],
    "CURSOS COMPLEMENTARIOS": [(165, 194), (260, 284)]
}

rangos_con_certificado = [
    (3, 29),  # externos (bloques de 6)
]
def icono_estatus(val):
    val = str(val).lower()

    if "vigente" in val or "ok" in val:
        return "🟢 " + val

    if "proximo" in val or "por vencer" in val or "vence" in val:
        return "🟡 " + val

    if "vencido" in val or "expirado" in val:
        return "🔴 " + val

    return val
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

            if not isinstance(nombre_curso, str) or nombre_curso.strip() == "":
                continue

            vencimiento = None
            estatus = None
            observaciones = None
            certificado = None

            try:
                vencimiento = pd.to_datetime(fila.iloc[col + 2], errors="coerce")
                vencimiento = vencimiento.date() if pd.notna(vencimiento) else None
            except:
                pass

            try:
                # si es bloque con certificado → se recorre 1 columna
                if any(inicio <= col < fin for inicio, fin in rangos_con_certificado):
                    estatus = fila.iloc[col + 5]
                else:
                    estatus = fila.iloc[col + 4]
            except:
                pass

            try:
                observaciones = fila.iloc[col + 0]
            except:
                pass

            # 🔥 SOLO PARA RANGOS ESPECIALES
            if any(inicio <= col < fin for inicio, fin in rangos_con_certificado):
                try:
                    certificado = fila.iloc[col + 1]  # ajusta si no coincide
                except:
                    pass

            curso_dict = {
                "Curso": nombre_curso,
                "Vencimiento": vencimiento,
                "Estatus": estatus,
                "Observaciones": observaciones
            }

            # agregar columna solo si aplica
            if any(inicio <= col < fin for inicio, fin in rangos_con_certificado):
                curso_dict["Cert/Folio"] = certificado

            cursos.append(curso_dict)

    return pd.DataFrame(cursos)

# =========================
# MOSTRAR POR CATEGORÍA
# =========================
for categoria, cursos_base in categorias.items():

    df_cat = obtener_cursos(cursos_base).copy()

    if categoria == "CURSOS EXTERNOS" and "Cert/Folio" in df_cat.columns:
        columnas = ["Curso", "Cert/Folio", "Vencimiento", "Estatus", "Observaciones"]
        columnas = [col for col in columnas if col in df_cat.columns]
        df_cat = df_cat[columnas]

    # 🔥 SI NO HAY DATOS, MUESTRA MENSAJE PERO NO ROMPAS
    if df_cat.empty:
        st.markdown(f"## 📂 {categoria}")
        st.warning("Sin datos en esta categoría")
        continue

    # 🔥 SEMÁFORO SEGURO
    if "Estatus" in df_cat.columns:
        df_cat["Estatus"] = df_cat["Estatus"].apply(icono_estatus)

    # ⚠️ FILTRO SEGURO (NO ELIMINA TODO)
    if "Vencimiento" in df_cat.columns:
        df_cat = df_cat[df_cat["Vencimiento"].notna()]

    st.markdown(f"## 📂 {categoria}")
    st.dataframe(df_cat, use_container_width=True)
