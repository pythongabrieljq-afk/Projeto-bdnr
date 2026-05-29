import streamlit as st
from database.mongo import carregar_dados
from components.sidebar import render_sidebar
from components.cards import render_metricas
from pages.overview import render_overview
from pages.sexo import render_sexo
from pages.faixa_etaria import render_faixa
from pages.escolaridade import render_escolaridade
from pages.microdados import render_microdados

st.set_page_config(
    page_title="Vigitel Dashboard",
    page_icon="📊",
    layout="wide"
)

df = carregar_dados("CD-IA", "Bdnr")

filtrado, ponderado = render_sidebar(df)

render_metricas(filtrado, ponderado)

aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "Visão geral",
    "Sexo",
    "Faixa etária",
    "Escolaridade",
    "Microdados"
])

with aba1:
    render_overview(filtrado, ponderado)

with aba2:
    render_sexo(filtrado, ponderado)

with aba3:
    render_faixa(filtrado, ponderado)

with aba4:
    render_escolaridade(filtrado, ponderado)

with aba5:
    render_microdados(filtrado)