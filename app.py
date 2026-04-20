import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# CSS personalizado
st.markdown("""
<style>
.header {
    display: flex;
    align-items: center;
    gap: 15px;
}

.nombre {
    font-size: 28px;
    font-weight: bold;
}

.section-title {
    font-size: 24px;
    font-weight: bold;
    margin-top: 30px;
}

.card {
    border-radius: 10px;
    padding: 10px;
}

.vigente {
    background-color: #c8e6c9;
}

.vencido {
    background-color: #ffcdd2;
}

.porvencer {
    background-color: #fff3cd;
}
</style>
""", unsafe_allow_html=True)
