import streamlit as st
import pandas as pd

st.title("Consulta de Cursos")

# Leer Excel (usa EXACTAMENTE el mismo nombre que subiste)
df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx")

nomina = st.text_input("Ingresa tu número de nómina")

if nomina:
    empleado = df[df["mep"].astype(str) == nomina]

    if empleado.empty:
        st.error("No se encontraron registros")
    else:
        st.success(f"Cursos de {empleado.iloc[0]['nombre']}")
        st.dataframe(empleado)

        csv = empleado.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Descargar reporte",
            csv,
            "reporte_cursos.csv",
            "text/csv"
        )
