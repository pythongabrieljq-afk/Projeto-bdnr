from pymongo import MongoClient
import pandas as pd
import streamlit as st

@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

@st.cache_data(ttl=600)
def carregar_dados(nome_banco, nome_collection):
    client = init_connection()

    dados = list(client[nome_banco][nome_collection].find())

    if not dados:
        return pd.DataFrame()

    for item in dados:
        item["_id"] = str(item["_id"])

    return pd.DataFrame(dados)