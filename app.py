import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

st.title("Consulta de Cursos")

# Leer Excel
df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx")

# Limpiar columnas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

nomina = st.text_input("Ingresa tu número de nómina")

if nomina:
    empleado = df[df["nomina"].astype(str).str.strip() == nomina.strip()]

    if empleado.empty:
        st.error("No se encontraron registros")
    else:
        nombre = empleado.iloc[0]["nombre"]
        st.success(f"Empleado: {nombre}")

        # Limpiar datos
        empleado["vencimiento"] = pd.to_datetime(
            empleado["vencimiento"], errors='coerce'
        ).dt.date

        empleado["tipodecurso"] = empleado["tipodecurso"].str.lower().str.strip()

        # Función para mostrar secciones
        def mostrar_seccion(titulo, filtro):
            data = empleado[empleado["tipodecurso"] == filtro]
            with st.expander(titulo):
                if data.empty:
                    st.write("Sin registros")
                else:
                    st.dataframe(data[["curso", "estatus", "vencimiento"]])

        # Secciones automáticas
        mostrar_seccion("📘 Cursos Técnicos", "técnico")
        mostrar_seccion("🤝 Habilidades", "habilidades")
        mostrar_seccion("🛡️ Seguridad", "seguridad")

        # -------- PDF --------
        def generar_pdf(data, nombre):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)

            y = 750
            c.setFont("Helvetica", 10)

            c.drawString(50, y, f"Empleado: {nombre}")
            y -= 20

            for i, row in data.iterrows():
                texto = f"{row['curso']} | {row['estatus']} | {row['vencimiento']}"
                c.drawString(50, y, texto)
                y -= 15

                if y < 50:
                    c.showPage()
                    y = 750

            c.save()
            buffer.seek(0)
            return buffer

        pdf = generar_pdf(empleado, nombre)

        st.download_button(
            label="📄 Descargar reporte en PDF",
            data=pdf,
            file_name="reporte_cursos.pdf",
            mime="application/pdf"
        )
