import plotly.express as px
import streamlit as st

def grafico_obesidade_ano(df):

    fig = px.line(
        df,
        x="ano",
        y="valor_pct",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )