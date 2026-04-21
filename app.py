import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Cursos Técnicos", layout="wide")

st.title("📚 Consulta de Cursos por Nómina")

# Cargar Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx", header=1)  # Cambia el nombre si es necesario
    return df
    df.columns = df.columns.str.strip()  # quita espacios

df = cargar_datos()
st.write(list(df.columns))

# Input de nómina
nomina_input = st.text_input("🔎 Ingresa tu número de nómina")

if nomina_input:
    # Filtrar datos
    persona = df[df["Nómina"].astype(str) == nomina_input]

    if not persona.empty:
        st.subheader("👤 Información del colaborador")

        nombre = persona.iloc[0]["Nombre del Colaborador"]
        st.write(f"**Nombre:** {nombre}")
        st.write(f"**Nómina:** {nomina_input}")

        st.divider()

        st.subheader("📋 Cursos")

        # 🔥 Aquí está lo importante:
        # Tomar TODAS las columnas dinámicamente excepto datos base
        columnas_base = ["Nomina", "Nombre del Colaborador", "Proceso", "Categoría"]
        columnas_cursos = [col for col in df.columns if col not in columnas_base]

        # Convertir a formato vertical (tipo tabla bonita)
        cursos = persona[columnas_cursos].T.reset_index()
        cursos.columns = ["Curso", "Valor"]

        # Quitar vacíos o "NO APLICA"
        cursos = cursos[cursos["Valor"].notna()]
        cursos = cursos[cursos["Valor"] != "NO APLICA"]

        st.dataframe(cursos, use_container_width=True)

    else:
        st.error("❌ Nómina no encontrada")
col_nomina = None

for col in df.columns:
    if "nom" in col.lower():
        col_nomina = col
        break

st.write("Columna detectada:", col_nomina)

persona = df[df[col_nomina].astype(str) == nomina_input]
for col in df.columns:
    st.write(f"'{col}'")
