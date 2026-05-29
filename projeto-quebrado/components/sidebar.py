import streamlit as st

def render_sidebar(df):

    st.sidebar.title("Vigitel Explorer")

    anos = sorted(df["ano"].dropna().unique())

    ano_sel = st.sidebar.multiselect(
        "Ano",
        anos,
        default=anos
    )

    filtrado = df[df["ano"].isin(ano_sel)]

    ponderado = st.sidebar.toggle(
        "Usar peso amostral",
        value=True
    )

    return filtrado, ponderado