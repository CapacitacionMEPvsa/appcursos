import streamlit as st
import pandas as pd

st.title("Consulta por Nómina")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("base_datos.xlsx", header=2)
    df.columns = df.columns.astype(str).str.strip()
    return df

df = cargar_datos()

# DEBUG (puedes quitar luego)
st.write(df.columns)

nomina_input = st.text_input("Ingresa nómina")

if nomina_input:
    col_nomina = [col for col in df.columns if "nom" in col.lower()][0]

    persona = df[df[col_nomina].astype(str) == nomina_input]

    if not persona.empty:
        st.success("Encontrado")
        st.dataframe(persona)
    else:
        st.error("No encontrado")
