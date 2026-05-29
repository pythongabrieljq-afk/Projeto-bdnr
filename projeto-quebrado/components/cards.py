import streamlit as st
from utils.metrics import media_ponderada
from utils.formatters import resumo_texto

def render_metricas(df, ponderado):

    imc = media_ponderada(df, "imc")

    c1, c2 = st.columns(2)

    c1.metric(
        "Registros",
        resumo_texto(len(df))
    )

    c2.metric(
        "IMC Médio",
        resumo_texto(imc, "imc")
    )