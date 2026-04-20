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

st.write(df.columns.tolist())
st.stop()

# limpiar nombres de columnas
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

# =========================
# 🔥 DEFINICIÓN DE BLOQUES
# (AJUSTA AQUÍ SEGÚN TU EXCEL)
# =========================
bloques = [

    # ===== SEGURIDAD =====
    {
        "curso": "anexosspa",          # nombre de columna del curso
        "vencimiento": "vigenciasspa", # columna fecha vigencia
        "estatus": "estatussspa",      # columna estatus (si no existe se calcula)
        "tipo": "seguridad"
    },

    # ===== EJEMPLOS (AGREGA MÁS IGUAL) =====
    # {
    #     "curso": "trabajoenalturas",
    #     "vencimiento": "vigenciaalturas",
    #     "estatus": "estatusalturas",
    #     "tipo": "seguridad"
    # },

    # {
    #     "curso": "equipos",
    #     "vencimiento": "vigenciaequipos",
    #     "estatus": "estatusequipos",
    #     "tipo": "tecnico"
    # },

]

# =========================
# TRANSFORMAR A FORMATO VERTICAL
# =========================
cursos = []

for b in bloques:
    if b["curso"] in df.columns:

        temp = df[["nomina", "nombre", "proceso"]].copy()

        temp["curso"] = df[b["curso"]]
        temp["vencimiento"] = df[b["vencimiento"]]

        # usar estatus si existe, si no calcularlo después
        if b["estatus"] in df.columns:
            temp["Estatus"] = df[b["estatus"]]
        else:
            temp["Estatus"] = None

        temp["tipodecurso"] = b["tipo"]

        cursos.append(temp)

if len(cursos) == 0:
    st.error("❌ No se pudieron generar cursos.")
    st.write("Columnas disponibles:", df.columns.tolist())
    st.stop()

df_final = pd.concat(cursos, ignore_index=True)

# =========================
# 🔥 BLOQUES (POR ÍNDICE)
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
# 🔥 EXTRACCIÓN (NO TOCA UI NI PDF)
# =========================
cursos = []

for b in bloques:

    # base mínima (NO modificar estructura global)
    base = df.iloc[:, [0, 1]].copy()
    base.columns = ["nomina", "nombre"]

    temp = base.copy()

    temp["curso"] = df.iloc[:, b["inicio"]]
    temp["vencimiento"] = df.iloc[:, b["inicio"] + 2]

    # si existe estatus lo respeta, si no lo deja vacío
    temp["estatus"] = df.iloc[:, b["inicio"] + 3] if df.shape[1] > b["inicio"] + 3 else None

    temp["tipodecurso"] = b["tipo"]
    temp["categoria"] = b["nombre"]

    cursos.append(temp)

# unir todo
df_final = pd.concat(cursos, ignore_index=True)

# limpiar vacíos sin afectar lógica posterior
df_final = df_final[df_final["curso"].notna()]

# eliminar vacíos
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
        # BOTONES
        # =========================
        colA, colB = st.columns([1, 2])

        with colA:
            descargar = st.button("📄 Descargar Kardex PDF")

        with colB:
            filtro = st.toggle("🚀 Solo pendientes o por vencer")

        # =========================
        # LIMPIEZA FECHAS
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

        # calcular solo si no venía definido
        empleado["Estatus"] = empleado.apply(
            lambda row: calcular_estatus(row["vencimiento"])
            if pd.isna(row["Estatus"]) else row["Estatus"],
            axis=1
        )

        # =========================
        # FILTRO
        # =========================
        if filtro:
            empleado = empleado[
                empleado["Estatus"].isin(["Vencido", "Por vencer", "Pendiente"])
            ]

        # =========================
        # COLORES
        # =========================
        def color_fila(row):
            if row["Estatus"] == "Vigente":
                return ['background-color: #c8e6c9'] * len(row)
            elif row["Estatus"] == "Vencido":
                return ['background-color: #ffcdd2'] * len(row)
            elif row["Estatus"] == "Por vencer":
                return ['background-color: #fff3cd'] * len(row)
            else:
                return ['background-color: #eeeeee'] * len(row)

        # =========================
        # TABLAS
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
        # SECCIONES
        # =========================
        mostrar_cursos(
            "CURSOS DE SEGURIDAD",
            empleado[empleado["tipodecurso"] == "seguridad"]
        )

        mostrar_cursos(
            "CURSOS TÉCNICOS",
            empleado[empleado["tipodecurso"] == "tecnico"]
        )

        # =========================
        # PDF (BÁSICO)
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
