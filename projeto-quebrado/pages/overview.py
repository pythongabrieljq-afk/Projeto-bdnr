import streamlit as st
from components.charts import grafico_obesidade_ano

def render_overview(df, ponderado):

    st.subheader("Visão Geral")

    grafico_obesidade_ano(df)