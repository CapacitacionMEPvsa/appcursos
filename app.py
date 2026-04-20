import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.title("Consulta de Cursos")

# =========================
# CARGAR EXCEL
# =========================
df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx")

# Limpiar columnas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

# =========================
# INPUT
# =========================
nomina = st.text_input("Ingresa tu número de nómina")

if nomina:
    empleado = df[df["nomina"].astype(str).str.strip() == nomina.strip()].copy()

    if empleado.empty:
        st.error("No se encontraron registros")
    else:
        nombre = empleado.iloc[0]["nombre"]
        st.success(f"Empleado: {nombre}")

        # =========================
        # LIMPIEZA
        # =========================
        empleado["vencimiento"] = pd.to_datetime(
            empleado["vencimiento"], errors="coerce"
        ).dt.date

        empleado["tipodecurso"] = (
            empleado["tipodecurso"]
            .astype(str)
            .str.lower()
            .str.strip()
            .str.replace("á", "a")
            .str.replace("é", "e")
            .str.replace("í", "i")
            .str.replace("ó", "o")
            .str.replace("ú", "u")
        )

        # =========================
        # ESTATUS
        # =========================
        hoy = datetime.today().date()

        def calcular_estatus(fecha):
            if pd.isna(fecha):
                return "Sin fecha"
            dias = (fecha - hoy).days
            if dias < 0:
                return "Vencido"
            elif dias <= 30:
                return "Por vencer"
            else:
                return "Vigente"

        empleado["Estatus"] = empleado["vencimiento"].apply(calcular_estatus)

        # =========================
        # SEMÁFORO EN APP
        # =========================
        def semaforo(val):
            if val == "Vencido":
                return "🔴 Vencido"
            elif val == "Por vencer":
                return "🟡 Por vencer"
            elif val == "Vigente":
                return "🟢 Vigente"
            return val

        # =========================
        # MOSTRAR SECCIONES
        # =========================
        def mostrar_seccion(titulo, filtro):
            data = empleado[empleado["tipodecurso"] == filtro]

            st.subheader(titulo)

            if data.empty:
                st.write("Sin registros")
            else:
                tabla = data[["curso", "Estatus", "vencimiento"]].copy()
                tabla["Estatus"] = tabla["Estatus"].apply(semaforo)
                st.dataframe(tabla, use_container_width=True)

        mostrar_seccion("📘 Cursos Técnicos", "Técnicos")
        st.markdown("---")
        mostrar_seccion("🛡️ Cursos de Seguridad", "seguridad")
        st.markdown("---")
        mostrar_seccion("🛡️ Cursos Externos", "externos")
        st.markdown("---")        
        mostrar_seccion("🤝 Cursos Complementarios", "complementario")

        # =========================
        # GENERAR PDF
        # =========================
        def generar_pdf(data, nombre):

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)

            elements = []
            styles = getSampleStyleSheet()

            # ENCABEZADO
            encabezado = []

            if os.path.exists("logo.png"):
                logo = Image("logo.png", width=80, height=50)
            else:
                logo = ""

            titulo = Paragraph(
                "<para align='center'><b>Materiales y Equipo Petrolero</b><br/>"
                "<font size=10>Kardex de Capacitación Laboral</font></para>",
                styles["Title"]
            )

            encabezado.append([logo, titulo])

            tabla_encabezado = Table(encabezado, colWidths=[100, 380])
            tabla_encabezado.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")])

            elements.append(tabla_encabezado)
            elements.append(Spacer(1, 15))

            # DATOS
            nomina_emp = str(data.iloc[0]["nomina"])
            proceso = str(data.iloc[0].get("proceso", "N/A"))

            elements.append(Paragraph(f"<b>Nombre del colaborador:</b> {nombre}", styles["Normal"]))
            elements.append(Paragraph(f"<b>No. Nómina:</b> {nomina_emp}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Proceso:</b> {proceso}", styles["Normal"]))
            elements.append(Spacer(1, 15))

            # =========================
            # CALCULAR CUMPLIMIENTO
            # =========================
            total = len(data)
            vigentes = len(data[data["Estatus"] == "Vigente"])
            por_vencer = len(data[data["Estatus"] == "Por vencer"])

            cumplidos = vigentes + por_vencer
            porcentaje = round((cumplidos / total) * 100, 1) if total > 0 else 0

            # =========================
            # TABLAS
            # =========================
            def tabla_cursos(titulo, filtro):

                seccion = data[data["tipodecurso"] == filtro]

                if seccion.empty:
                    return

                elements.append(Paragraph(f"<b>{titulo}</b>", styles["Heading2"]))
                elements.append(Spacer(1, 5))

                tabla_data = [["No.", "Curso", "Vencimiento", "Estatus", "Observaciones"]]

                for i, (_, row) in enumerate(seccion.iterrows(), start=1):

                    if row["Estatus"] == "Vencido":
                        estatus = "🔴 Vencido"
                    elif row["Estatus"] == "Por vencer":
                        estatus = "🟡 Por vencer"
                    else:
                        estatus = "🟢 Vigente"

                    tabla_data.append([
                        str(i),
                        str(row["curso"]),
                        str(row["vencimiento"]),
                        estatus,
                        ""
                    ])

                tabla = Table(
                    tabla_data,
                    colWidths=[40, 200, 90, 90, 120],
                    repeatRows=1
                )

                tabla.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (2, 1), (4, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                ]))

                elements.append(tabla)
                elements.append(Spacer(1, 15))

            # SECCIONES
            tabla_cursos("Cursos Técnicos", "Técnicos")
            tabla_cursos("Cursos de Seguridad", "seguridad")
            tabla_cursos("Cursos de Externos", "Externos")
            tabla_cursos("Cursos de Complementarios", "Complementarios")
            
            # RESUMEN
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(
                f"<b>Resumen:</b><br/>Total cursos: {total}<br/>"
                f"Cumplidos: {cumplidos}<br/>"
                f"<b>Porcentaje: {porcentaje}%</b>",
                styles["Normal"]
            ))

            # FECHA
            elements.append(Spacer(1, 20))
            fecha = datetime.today().strftime("%Y-%m-%d")
            elements.append(Paragraph(f"<b>Fecha del reporte:</b> {fecha}", styles["Normal"]))

            doc.build(elements)
            buffer.seek(0)
            return buffer

        # BOTÓN PDF
        pdf = generar_pdf(empleado, nombre)

        st.download_button(
            label="📄 Descargar Kardex en PDF",
            data=pdf,
            file_name="kardex_capacitacion.pdf",
            mime="application/pdf"
        )
