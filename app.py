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
# USAR FILA REAL DE ENCABEZADOS
# =========================
df.columns = df.iloc[1]
df = df[2:].reset_index(drop=True)

# =========================
# LIMPIEZA DE COLUMNAS
# =========================
def clean_text(x):
    return (
        str(x)
        .lower()
        .strip()
        .replace(" ", "")
        .replace(".", "")
        .replace("\n", "")
        .replace("\xa0", "")
    )

df.columns = [str(c).strip() for c in df.columns]

cols_clean = {clean_text(c): c for c in df.columns}

def find_col(keyword):
    for k, v in cols_clean.items():
        if keyword in k:
            return v
    return None

COL_NOMINA = find_col("nomina")
COL_NOMBRE = find_col("nombre")
COL_PROCESO = find_col("proceso")

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
# FUNCIÓN BLOQUES
# =========================
def extraer_bloque(emp, inicio, fin, categoria, obs_col=None):

    data = []

    for col in range(inicio, fin + 1):

        if col >= len(emp.columns):
            continue

        try:
            data.append(pd.DataFrame({
                "nomina": emp[COL_NOMINA].values,
                "nombre": emp[COL_NOMBRE].values,
                "proceso": emp[COL_PROCESO].values if COL_PROCESO else None,
                "categoria": categoria,
                "curso": emp.iloc[:, col],
                "vencimiento": emp.iloc[:, col + 1] if col + 1 < len(emp.columns) else None,
                "estatus": emp.iloc[:, col + 2] if col + 2 < len(emp.columns) else None,
                "observaciones": emp.iloc[:, obs_col] if obs_col is not None and obs_col < len(emp.columns) else None
            }))
        except:
            continue

    if data:
        return pd.concat(data, ignore_index=True)

    return pd.DataFrame()

# =========================
# BLOQUES DE CURSOS
# =========================
cursos = []

# CURSOS EXTERNOS
cursos.append(extraer_bloque(empleado, 6, 32, "CURSOS EXTERNOS"))
cursos.append(extraer_bloque(empleado, 297, 381, "CURSOS EXTERNOS"))

# ANEXO SSPA
cursos.append(extraer_bloque(empleado, 33, 200, "ANEXO SSPA", obs_col=33))

# CURSOS TECNICOS
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

# eliminar duplicados de columnas
df_final = df_final.loc[:, ~df_final.columns.duplicated()]

# =========================
# MOSTRAR SOLO LO NECESARIO
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
