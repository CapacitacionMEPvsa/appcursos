import streamlit as st
import pandas as pd
from datetime import datetime
import io

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(layout="wide")

st.title("Consulta de Cursos")

# =========================
# CSS (ESTILO)
# =========================
st.markdown("""
<style>
.nombre {
    font-size: 28px;
    font-weight: bold;
}

.section-title {
    font-size: 22px;
    font-weight: bold;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CARGAR EXCEL
# =========================
df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx")

# Limpiar columnas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

# =========================
# TRANSFORMAR A FORMATO VERTICAL
# =========================
cursos = []

for i in range(1, 20):  # ajusta si tienes más cursos
    curso_col = f"curso{i}"
    venc_col = f"vencimiento{i}"

    if curso_col in df.columns:
        temp = df[["nomina", "nombre", "proceso"]].copy()
        temp["curso"] = df[curso_col]
        temp["vencimiento"] = df[venc_col]

        # tipo de curso (puedes mejorar esta lógica)
        temp["tipodecurso"] = "tecnico"

        cursos.append(temp)

df = pd.concat(cursos, ignore_index=True)

# eliminar vacíos
df = df[df["curso"].notna()]

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

        # =========================
        # HEADER
        # =========================
        col1, col2 = st.columns([1, 6])

        with col1:
            st.image("logo.png", width=120)  # opcional

        with col2:
            st.markdown(f'<div class="nombre">👤 {nombre}</div>', unsafe_allow_html=True)

        # =========================
        # BOTONES
        # =========================
        colA, colB = st.columns([1, 2])

        with colA:
            descargar = st.button("📄 Descargar Kardex PDF")

        with colB:
            filtro = st.toggle("🚀 Solo pendientes o por vencer")

        # =========================
        # LIMPIEZA
        # =========================
        empleado["vencimiento"] = pd.to_datetime(
            empleado["vencimiento"], errors="coerce"
        ).dt.date

        hoy = datetime.today().date()

        def calcular_estatus(fecha):
            if pd.isna(fecha):
                return "Pendiente"
            dias = (fecha - hoy).days
            if dias < 0:
                return "Vencido"
            elif dias <= 30:
                return "Por vencer"
            else:
                return "Vigente"

        empleado["Estatus"] = empleado["vencimiento"].apply(calcular_estatus)

        # =========================
        # FILTRO
        # =========================
        if filtro:
            empleado = empleado[
                empleado["Estatus"].isin(["Vencido", "Por vencer"])
            ]

        # =========================
        # COLORES
        # =========================
        def color_fila(row):
            if row["Estatus"] == "Vigente":
                return ['background-color: #c8e6c9'] * len(row)
            elif row["Estatus"] == "Vencido":
                return ['background-color: #ffcdd2'] * len(row)
            else:
                return ['background-color: #fff3cd'] * len(row)

        # =========================
        # FUNCIÓN PARA TABLAS
        # =========================
        def mostrar_cursos(titulo, data):

            if data.empty:
                return

            st.markdown(f"## 📁 {titulo}")

            tabla = data[["curso", "vencimiento", "Estatus"]].copy()
            tabla.columns = ["Curso", "Vencimiento", "Estatus"]

            tabla["Observaciones"] = ""
            tabla["Capacitación"] = tabla["Estatus"].apply(
                lambda x: "Tomar Curso" if x != "Vigente" else ""
            )

            styled = tabla.style.apply(color_fila, axis=1)

            st.dataframe(
                styled,
                use_container_width=True,
                hide_index=True
            )

        # =========================
        # MOSTRAR SECCIONES
        # =========================
        mostrar_cursos("CURSOS TÉCNICOS", empleado)
        # si tienes clasificación real, separa aquí:
        # mostrar_cursos("CURSOS DE SEGURIDAD", empleado[empleado["tipodecurso"]=="seguridad"])

        # =========================
        # PDF
        # =========================
        def generar_pdf(data, nombre):
            buffer = io.BytesIO()
            buffer.write(f"Kardex de {nombre}".encode())
            buffer.seek(0)
            return buffer

        if descargar:
            pdf = generar_pdf(empleado, nombre)

            st.download_button(
                label="Descargar PDF",
                data=pdf,
                file_name="kardex.pdf",
                mime="application/pdf"
            )
