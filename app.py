import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("📚 Cursos del Colaborador")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx", header=2)
    df.columns = df.columns.astype(str).str.strip()
    return df

df = cargar_datos()

# 🔎 INPUT
nomina_input = st.text_input("Ingresa tu nómina")

if nomina_input:

    # 🔍 Detectar columna de nómina automáticamente
    col_nomina = None
    for col in df.columns:
        if "nom" in col.lower() or "no." in col.lower():
            col_nomina = col
            break

    st.write("Columna usada:", col_nomina)
    st.write("Valores en Excel:", df[col_nomina].head(10))

    # filtro
    persona = df[df[col_nomina].astype(str).str.strip() == nomina_input.strip()]
    
    if col_nomina is None:
        st.error("No se encontró columna de nómina")
        st.write(df.columns)
        st.stop()

persona = df[
    df[col_nomina]
    .astype(str)
    .str.replace(".0", "", regex=False)
    .str.strip()
    == nomina_input.strip()
]

    if persona.empty:
        st.error("Nómina no encontrada")
        st.stop()

    persona = persona.iloc[0]

    st.subheader("📂 CURSOS TÉCNICOS")

    # 🔥 EXTRAER CURSOS DINÁMICAMENTE
    cursos = []

    columnas = list(df.columns)

    for i in range(len(columnas)):
        col = columnas[i]

        # Detectar bloques tipo: Curso, Emisión, Vigencia, Estatus
        if "vigencia" in col.lower():

            curso_nombre = columnas[i-2] if i >= 2 else col

            try:
                curso = {
                    "Curso": curso_nombre,
                    "Vencimiento": persona[col],
                    "Estatus": persona[columnas[i+2]] if i+2 < len(columnas) else "",
                    "Observaciones": persona[columnas[i-1]] if i-1 >= 0 else "",
                    "Capacitación": ""
                }

                cursos.append(curso)
            except:
                pass

    df_cursos = pd.DataFrame(cursos)

    # Limpiar vacíos
    df_cursos = df_cursos[df_cursos["Curso"].notna()]

    # 🎨 COLORES
    def color_fila(row):
        if "VIGENTE" in str(row["Estatus"]):
            return ["background-color: #c8e6c9"] * len(row)
        elif "PENDIENTE" in str(row["Estatus"]):
            return ["background-color: #ffcdd2"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_cursos.style.apply(color_fila, axis=1),
        use_container_width=True
    )
