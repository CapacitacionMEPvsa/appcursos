import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

st.title("Consulta de Cursos")

df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

nomina = st.text_input("Ingresa tu número de nómina")

if nomina:
    empleado = df[df["nomina"].astype(str).str.strip() == nomina.strip()]

    if not empleado.empty:
        nombre = empleado.iloc[0]["nombre"]
        st.success(f"Empleado: {nombre}")

        empleado["vencimiento"] = pd.to_datetime(
            empleado["vencimiento"], errors='coerce'
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

        empleado["estatus_calculado"] = empleado["vencimiento"].apply(calcular_estatus)

        # -------- PDF PROFESIONAL --------
        def generar_pdf(data, nombre):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # LOGO
            try:
                logo = Image("logo.png", width=120, height=60)
                elements.append(logo)
            except:
                pass

            # ENCABEZADO
            elements.append(Paragraph("<b>REPORTE DE CAPACITACIÓN</b>", styles["Title"]))
            elements.append(Spacer(1, 10))

            fecha_hoy = datetime.today().strftime("%Y-%m-%d")

            elements.append(Paragraph(f"<b>Empleado:</b> {nombre}", styles["Normal"]))
            elements.append(Paragraph(f"<b>Fecha:</b> {fecha_hoy}", styles["Normal"]))
            elements.append(Spacer(1, 15))

            # -------- RESUMEN --------
            resumen = data["estatus_calculado"].value_counts()

            vencidos = resumen.get("Vencido", 0)
            por_vencer = resumen.get("Por vencer", 0)
            vigentes = resumen.get("Vigente", 0)

            elements.append(Paragraph("<b>Resumen de Cursos</b>", styles["Heading2"]))
            elements.append(Spacer(1, 5))

            elements.append(Paragraph(f"🔴 Vencidos: {vencidos}", styles["Normal"]))
            elements.append(Paragraph(f"🟡 Por vencer: {por_vencer}", styles["Normal"]))
            elements.append(Paragraph(f"🟢 Vigentes: {vigentes}", styles["Normal"]))

            elements.append(Spacer(1, 15))

            # -------- TABLA --------
            tabla_data = [["Curso", "Estatus", "Vencimiento"]]

            for _, row in data.iterrows():
                tabla_data.append([
                    str(row["curso"]),
                    str(row["estatus_calculado"]),
                    str(row["vencimiento"])
                ])

            tabla = Table(tabla_data)

            # COLORES POR FILA
            style = [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]

            # Pintar estatus
            for i, row in enumerate(data.itertuples(), start=1):
                if row.estatus_calculado == "Vencido":
                    style.append(("TEXTCOLOR", (1, i), (1, i), colors.red))
                elif row.estatus_calculado == "Por vencer":
                    style.append(("TEXTCOLOR", (1, i), (1, i), colors.orange))
                elif row.estatus_calculado == "Vigente":
                    style.append(("TEXTCOLOR", (1, i), (1, i), colors.green))

            tabla.setStyle(TableStyle(style))

            elements.append(tabla)
            elements.append(Spacer(1, 30))

            # FIRMA
            elements.append(Paragraph("__________________________", styles["Normal"]))
            elements.append(Paragraph("Firma del empleado", styles["Normal"]))

            doc.build(elements)
            buffer.seek(0)
            return buffer

       def generar_pdf(data, nombre):
    import os
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # LOGO (seguro)
    if os.path.exists("logo.png"):
        logo = Image("logo.png", width=120, height=60)
        elements.append(logo)

    elements.append(Paragraph("<b>REPORTE DE CAPACITACIÓN</b>", styles["Title"]))
    elements.append(Spacer(1, 10))

    fecha_hoy = datetime.today().strftime("%Y-%m-%d")

    elements.append(Paragraph(f"<b>Empleado:</b> {nombre}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fecha:</b> {fecha_hoy}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    # -------- RESUMEN --------
    resumen = data["estatus_calculado"].value_counts()
    elements.append(Paragraph("<b>Resumen de Cursos</b>", styles["Heading2"]))
    elements.append(Paragraph(f"🔴 Vencidos: {resumen.get('Vencido', 0)}", styles["Normal"]))
    elements.append(Paragraph(f"🟡 Por vencer: {resumen.get('Por vencer', 0)}", styles["Normal"]))
    elements.append(Paragraph(f"🟢 Vigentes: {resumen.get('Vigente', 0)}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    # -------- FUNCIÓN PARA TABLAS POR SECCIÓN --------
    def agregar_seccion(titulo, filtro):
        seccion = data[data["tipodecurso"] == filtro]

        if seccion.empty:
            return

        elements.append(Paragraph(f"<b>{titulo}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 5))

        tabla_data = [["Curso", "Estatus", "Vencimiento"]]

        for _, row in seccion.iterrows():
            tabla_data.append([
                str(row["curso"]),
                str(row["estatus_calculado"]),
                str(row["vencimiento"])
            ])

        tabla = Table(tabla_data)

        style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]

        # Colores por estatus
        for i, row in enumerate(seccion.itertuples(), start=1):
            if row.estatus_calculado == "Vencido":
                style.append(("TEXTCOLOR", (1, i), (1, i), colors.red))
            elif row.estatus_calculado == "Por vencer":
                style.append(("TEXTCOLOR", (1, i), (1, i), colors.orange))
            elif row.estatus_calculado == "Vigente":
                style.append(("TEXTCOLOR", (1, i), (1, i), colors.green))

        tabla.setStyle(TableStyle(style))

        elements.append(tabla)
        elements.append(Spacer(1, 15))

    # -------- SECCIONES --------
    agregar_seccion("📘 Cursos Técnicos", "tecnico")
    agregar_seccion("🤝 Habilidades", "habilidades")
    agregar_seccion("🛡️ Seguridad", "seguridad")

    # FIRMA
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("__________________________", styles["Normal"]))
    elements.append(Paragraph("Firma del empleado", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer
