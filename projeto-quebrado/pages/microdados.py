import streamlit as st

def render_microdados(df):

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Baixar CSV",
        csv,
        "dados.csv",
        "text/csv"
    )