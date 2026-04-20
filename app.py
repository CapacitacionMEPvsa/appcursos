import streamlit as st
import pandas as pd

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

# =========================
# 🔥 LIMPIEZA CRÍTICA DE COLUMNAS
# =========================
df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.replace("\n", "", regex=True)
    .str.replace("\xa0", "", regex=True)
)

# usar fila real de encabezados
df.columns = df.iloc[1]
df = df[2:].reset_index(drop=True)

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.replace("\n", "", regex=True)
    .str.replace("\xa0", "", regex=True)
)

# =========================
# 🔥 DETECCIÓN AUTOMÁTICA DE COLUMNAS (FIX KEYERROR)
# =========================
def find_col(df, keyword):
    for c in df.columns:
        if keyword.lower() in str(c).lower():
            return c
    return None

COL_NOMINA = find_col(df, "nomina")
COL_NOMBRE = find_col(df, "nombre")
COL_PROCESO = find_col(df, "proceso")

# validar
if COL_NOMINA is None or COL_NOMBRE is None:
    st.error("No se encontraron columnas de Nómina o Nombre")
    st.write(df.columns.tolist())
    st.stop()

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
# 🔥 BLOQUES DE CURSOS
# =========================
def extraer_bloque(df_emp, inicio, fin, categoria):
    data = []

    for col in range(inicio, fin + 1):

        if col >= len(df_emp.columns):
            continue

        try:
            data.append(pd.DataFrame({
                "nomina": df_emp[COL_NOMINA].values,
                "nombre": df_emp[COL_NOMBRE].values,
                "proceso": df_emp[COL_PROCESO].values if COL_PROCESO else None,
                "categoria": categoria,
                "curso": df_emp.iloc[:, col],
                "vencimiento": df_emp.iloc[:, col + 1] if col + 1 < len(df_emp.columns) else None,
                "estatus": df_emp.iloc[:, col + 2] if col + 2 < len(df_emp.columns) else None,
                "observaciones": df_emp.iloc[:, 33] if 33 < len(df_emp.columns) else None
            }))
        except:
            continue

    if data:
        return pd.concat(data, ignore_index=True)
    return pd.DataFrame()

# =========================
# CONSTRUIR TODOS LOS BLOQUES
# =========================
cursos = []

# ANEXO SSPA
cursos.append(extraer_bloque(empleado, 33, 200, "ANEXO SSPA"))

# CURSOS EXTERNOS
cursos.append(extraer_bloque(empleado, 6, 32, "CURSOS EXTERNOS"))
cursos.append(extraer_bloque(empleado, 297, 381, "CURSOS EXTERNOS"))

# CURSOS TECNICOS
cursos.append(extraer_bloque(empleado, 201, 265, "CURSOS TECNICOS"))
cursos.append(extraer_bloque(empleado, 289, 296, "CURSOS TECNICOS"))

# COMPLEMENTARIOS
cursos.append(extraer_bloque(empleado, 266, 288, "CURSOS COMPLEMENTARIOS"))

# =========================
# UNIR
# =========================
df_final = pd.concat(cursos, ignore_index=True)

# limpiar vacíos
df_final = df_final[df_final["curso"].notna()]

# quitar duplicados de columnas
df_final = df_final.loc[:, ~df_final.columns.duplicated()]

# =========================
# MOSTRAR SOLO LO NECESARIO
# =========================
columnas_visibles = [
    "nomina",
    "nombre",
    "proceso",
    "categoria",
    "curso",
    "vencimiento",
    "estatus",
    "observaciones"
]

columnas_finales = [c for c in columnas_visibles if c in df_final.columns]

st.markdown("## 📋 Mis cursos")

st.dataframe(
    df_final[columnas_finales],
    use_container_width=True
)
