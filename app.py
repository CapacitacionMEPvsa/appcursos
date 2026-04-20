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
# CARGAR EXCEL
# =========================
df = pd.read_excel("BASE DE DATOS DE CURSOS DE CAPACITACION VSA.xlsx")

# ⚠️ IMPORTANTE: NO limpiar columnas agresivamente aquí
# porque tu archivo no es estructurado

# =========================
# 🔥 DEFINICIÓN DE BLOQUES (POR ÍNDICE)
# =========================
bloques = [

    {
        "nombre": "CERTIFICACIONES TECNICAS",
        "inicio": 20,
        "tipo": "tecnico"
    },

    {
        "nombre": "ANEXO SSPA",
        "inicio": 88,
        "tipo": "seguridad"
    },

    {
        "nombre": "COMPETENCIAS TECNICAS BASICAS",
        "inicio": 200,
        "tipo": "tecnico"
    }

]

# =========================
# 🔥 EXTRACCIÓN CORRECTA (CLAVE)
# =========================
cursos = []

for b in bloques:

    # columnas base (ajusta si cambia tu archivo)
    base = df.iloc[:, [0, 1]].copy()
    base.columns = ["nomina", "nombre"]

    temp = base.copy()

    temp["curso"] = df.iloc[:, b["inicio"]]
    temp["vencimiento"] = df.iloc[:, b["inicio"] + 2]
    temp["estatus"] = df.iloc[:, b["inicio"] + 3]

    temp["tipodecurso"] = b["tipo"]
    temp["categoria"] = b["nombre"]

    cursos.append(temp)

# unir todo
df_final = pd.concat(cursos, ignore_index=True)

# limpiar vacíos
df_final = df_final[df_final["curso"].notna()]

# =========================
# INPUT
# =========================
nomina = st.text_input("Ingresa tu número de nómina")

if nomina:

    empleado = df_final[
        df_final["nomina"].astype(str).str.strip() == nomina.strip()
    ].copy()

    if empleado.empty:
        st.error("No se encontraron registros")
    else:

        nombre = empleado.iloc[0]["nombre"]

        # =========================
        # HEADER
        # =========================
        col1, col2 = st.columns([1, 6])

        with col1:
            st.image("logo.png", width=120)

        with col2:
            st.markdown(f"## 👤 {nombre}")

        # =========================
        # FILTRO
        # =========================
        filtro = st.toggle("🚀 Solo pendientes o por vencer")

        # =========================
        # ESTATUS CALCULADO (si viene vacío)
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

        empleado["estatus"] = empleado["estatus"].fillna(
            empleado["vencimiento"].apply(calcular_estatus)
        )

        # =========================
        # FILTRO
        # =========================
        if filtro:
            empleado = empleado[
                empleado["estatus"].isin(["Vencido", "Por vencer", "Pendiente"])
            ]

        # =========================
        # MOSTRAR TABLA
        # =========================
        st.markdown("## 📋 Cursos del trabajador")

        st.dataframe(
            empleado[[
                "categoria",
                "curso",
                "vencimiento",
                "estatus"
            ]],
            use_container_width=True
        )

        # =========================
        # PDF (BASE)
        # =========================
        def generar_pdf(data, nombre):
            buffer = io.BytesIO()
            buffer.write(f"Kardex de {nombre}".encode())
            buffer.seek(0)
            return buffer

        if st.button("📄 Descargar PDF"):
            pdf = generar_pdf(empleado, nombre)

            st.download_button(
                label="Descargar",
                data=pdf,
                file_name="kardex.pdf",
                mime="application/pdf"
            )
