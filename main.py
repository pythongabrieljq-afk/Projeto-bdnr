import io
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pymongo import MongoClient

st.set_page_config(
    page_title="Vigitel Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 1.2rem;}
    .metric-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(148,163,184,.18);
        border-radius: 16px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 10px 30px rgba(2,6,23,.18);
    }
    .section-title {font-size: 1.05rem; font-weight: 700; margin-bottom: .35rem;}
    .small-note {color: #94a3b8; font-size: .88rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

MAPA_CIDADES = {
    1: "Aracaju", 2: "Belém", 3: "Belo Horizonte", 4: "Boa Vista", 5: "Campo Grande",
    6: "Cuiabá", 7: "Curitiba", 8: "Florianópolis", 9: "Fortaleza", 10: "Goiânia",
    11: "João Pessoa", 12: "Macapá", 13: "Maceió", 14: "Manaus", 15: "Natal",
    16: "Palmas", 17: "Porto Alegre", 18: "Porto Velho", 19: "Recife", 20: "Rio Branco",
    21: "Rio de Janeiro", 22: "Salvador", 23: "São Luís", 24: "São Paulo", 25: "Teresina",
    26: "Vitória", 27: "Distrito Federal"
}

COORDS_VIGITEL = {

    "Aracaju": (-10.9472,-37.0731),
    "Belém": (-1.4558,-48.4902),
    "Belo Horizonte": (-19.9167,-43.9345),
    "Boa Vista": (2.8235,-60.6758),
    "Campo Grande": (-20.4697,-54.6201),
    "Cuiabá": (-15.6014,-56.0979),
    "Curitiba": (-25.4284,-49.2733),
    "Florianópolis": (-27.5949,-48.5482),
    "Fortaleza": (-3.7319,-38.5267),
    "Goiânia": (-16.6869,-49.2648),
    "João Pessoa": (-7.1195,-34.8450),
    "Macapá": (0.0349,-51.0694),
    "Maceió": (-9.6498,-35.7089),
    "Manaus": (-3.1190,-60.0217),
    "Natal": (-5.7945,-35.2110),
    "Palmas": (-10.1840,-48.3336),
    "Porto Alegre": (-30.0346,-51.2177),
    "Porto Velho": (-8.7608,-63.8999),
    "Recife": (-8.0476,-34.8770),
    "Rio Branco": (-9.9747,-67.8243),
    "Rio de Janeiro": (-22.9068,-43.1729),
    "Salvador": (-12.9714,-38.5014),
    "São Luís": (-2.5387,-44.2825),
    "São Paulo": (-23.5505,-46.6333),
    "Teresina": (-5.0892,-42.8019),
    "Vitória": (-20.3155,-40.3128),

    "Distrito Federal": (-15.7939,-47.8828)

}

ORDENS_FAIXA = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
ORDENS_ESC = ["0-8 anos", "9-11 anos", "12+ anos"]


@st.cache_resource
def init_connection():
    return MongoClient(st.secrets["mongo"]["uri"])


@st.cache_data(ttl=600)
def carregar_dados(nome_banco: str, nome_collection: str) -> pd.DataFrame:
    client = init_connection()
    dados = list(client[nome_banco][nome_collection].find())
    if not dados:
        return pd.DataFrame()

    for item in dados:
        item["_id"] = str(item["_id"])

    df = pd.DataFrame(dados)

    if "cidade" in df.columns:
        df["cidade_nome"] = df["cidade"].map(MAPA_CIDADES).fillna("Código " + df["cidade"].astype(str))

    if "sexo_cod" in df.columns and "sexo" not in df.columns:
        df["sexo"] = df["sexo_cod"].map({1: "Masculino", 2: "Feminino"}).fillna("Não informado")

    if "faixa_idade" in df.columns:
        df["faixa_idade"] = pd.Categorical(df["faixa_idade"], categories=ORDENS_FAIXA, ordered=True)

    if "esc_grupo" in df.columns:
        presentes = [x for x in ORDENS_ESC if x in df["esc_grupo"].dropna().unique().tolist()]
        extras = [x for x in df["esc_grupo"].dropna().unique().tolist() if x not in presentes]
        df["esc_grupo"] = pd.Categorical(df["esc_grupo"], categories=presentes + extras, ordered=True)

    numeric_cols = [
        "ano", "cidade", "peso_amostral", "idade", "esc_anos", "peso_kg",
        "altura_cm", "altura_m", "imc", "sobrepeso", "obeso"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def media_ponderada(df: pd.DataFrame, valor: str, peso: str = "peso_amostral") -> Optional[float]:
    base = df[[valor, peso]].dropna()
    if base.empty or base[peso].sum() == 0:
        return None
    return float((base[valor] * base[peso]).sum() / base[peso].sum())


def prevalencia_ponderada(df: pd.DataFrame, indicador: str, peso: str = "peso_amostral") -> Optional[float]:
    base = df[[indicador, peso]].dropna()
    if base.empty or base[peso].sum() == 0:
        return None
    return float((base[indicador] * base[peso]).sum() / base[peso].sum())


def resumo_texto(valor: Optional[float], kind: str = "num") -> str:
    if valor is None or pd.isna(valor):
        return "N/D"
    if kind == "pct":
        return f"{valor * 100:.1f}%"
    if kind == "imc":
        return f"{valor:.2f}"
    if kind == "kg":
        return f"{valor:.1f} kg"
    if kind == "cm":
        return f"{valor:.1f} cm"
    return f"{valor:,.0f}".replace(",", ".")


def agregar_ponderado(df: pd.DataFrame, grupo: list[str], indicador: str) -> pd.DataFrame:
    if any(col not in df.columns for col in grupo + [indicador, "peso_amostral"]):
        return pd.DataFrame()
    base = df[grupo + [indicador, "peso_amostral"]].dropna()
    if base.empty:
        return pd.DataFrame()
    agg = (
        base.groupby(grupo, observed=False)
        .apply(lambda x: (x[indicador] * x["peso_amostral"]).sum() / x["peso_amostral"].sum())
        .reset_index(name="valor")
    )
    agg["valor_pct"] = agg["valor"] * 100
    return agg


st.sidebar.title("Vigitel Explorer")
st.sidebar.caption("Projeto exploratório com Streamlit + MongoDB")

nome_banco = st.sidebar.text_input("Banco", value="CD-IA")
nome_collection = st.sidebar.text_input("Collection", value="Bdnr")

with st.sidebar.expander("Sobre o dashboard", expanded=False):
    st.write(
        "Este painel explora microdados do Vigitel com filtros dinâmicos e indicadores descritivos. "
        "As prevalências podem ser calculadas com ponderação por peso amostral."
    )

df = carregar_dados(nome_banco, nome_collection)

if df.empty:
    st.error("Nenhum dado encontrado. Verifique o nome do banco e da collection.")
    st.stop()

st.title("📊 Dashboard Exploratório — Vigitel")
st.caption("Filtros dinâmicos, indicadores descritivos e comparações por sexo, faixa etária, cidade e escolaridade.")

anos = sorted([int(x) for x in df["ano"].dropna().unique().tolist()]) if "ano" in df.columns else []
cidades = sorted(df["cidade_nome"].dropna().astype(str).unique().tolist()) if "cidade_nome" in df.columns else []
sexos = sorted(df["sexo"].dropna().astype(str).unique().tolist()) if "sexo" in df.columns else []
faixas = [x for x in ORDENS_FAIXA if "faixa_idade" in df.columns and x in df["faixa_idade"].astype(str).unique().tolist()]
escolaridades = [x for x in ORDENS_ESC if "esc_grupo" in df.columns and x in df["esc_grupo"].astype(str).unique().tolist()]
cat_imc_vals = sorted(df["cat_imc"].dropna().astype(str).unique().tolist()) if "cat_imc" in df.columns else []

st.sidebar.markdown("---")
ano_sel = st.sidebar.multiselect("Ano", anos, default=anos)
cidade_sel = st.sidebar.multiselect("Cidade", cidades, default=cidades[:8] if len(cidades) > 8 else cidades)
sexo_sel = st.sidebar.multiselect("Sexo", sexos, default=sexos)
faixa_sel = st.sidebar.multiselect("Faixa etária", faixas, default=faixas)
esc_sel = st.sidebar.multiselect("Escolaridade", escolaridades, default=escolaridades)
cat_imc_sel = st.sidebar.multiselect("Categoria IMC", cat_imc_vals, default=cat_imc_vals)
ponderado = st.sidebar.toggle("Usar peso amostral nos indicadores", value=True)

filtrado = df.copy()
if ano_sel and "ano" in filtrado.columns:
    filtrado = filtrado[filtrado["ano"].isin(ano_sel)]
if cidade_sel and "cidade_nome" in filtrado.columns:
    filtrado = filtrado[filtrado["cidade_nome"].isin(cidade_sel)]
if sexo_sel and "sexo" in filtrado.columns:
    filtrado = filtrado[filtrado["sexo"].isin(sexo_sel)]
if faixa_sel and "faixa_idade" in filtrado.columns:
    filtrado = filtrado[filtrado["faixa_idade"].astype(str).isin(faixa_sel)]
if esc_sel and "esc_grupo" in filtrado.columns:
    filtrado = filtrado[filtrado["esc_grupo"].astype(str).isin(esc_sel)]
if cat_imc_sel and "cat_imc" in filtrado.columns:
    filtrado = filtrado[filtrado["cat_imc"].astype(str).isin(cat_imc_sel)]

if filtrado.empty:
    st.warning("Os filtros atuais não retornaram registros.")
    st.stop()

if ponderado:
    imc_medio = media_ponderada(filtrado, "imc") if "imc" in filtrado.columns else None
    prev_sobrepeso = prevalencia_ponderada(filtrado, "sobrepeso") if "sobrepeso" in filtrado.columns else None
    prev_obesidade = prevalencia_ponderada(filtrado, "obeso") if "obeso" in filtrado.columns else None
    peso_medio = media_ponderada(filtrado, "peso_kg") if "peso_kg" in filtrado.columns else None
else:
    imc_medio = float(filtrado["imc"].mean()) if "imc" in filtrado.columns else None
    prev_sobrepeso = float(filtrado["sobrepeso"].mean()) if "sobrepeso" in filtrado.columns else None
    prev_obesidade = float(filtrado["obeso"].mean()) if "obeso" in filtrado.columns else None
    peso_medio = float(filtrado["peso_kg"].mean()) if "peso_kg" in filtrado.columns else None

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Registros", resumo_texto(len(filtrado)))
c2.metric("IMC médio", resumo_texto(imc_medio, "imc"))
c3.metric("Sobrepeso", resumo_texto(prev_sobrepeso, "pct"))
c4.metric("Obesidade", resumo_texto(prev_obesidade, "pct"))
c5.metric("Peso médio", resumo_texto(peso_medio, "kg"))

aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([

    "Visão geral",
    "Sexo",
    "Faixa etária",
    "Escolaridade",
    "Microdados",
    "Rede Vigitel"

])

with aba1:
    col1, col2 = st.columns(2)

    with col1:
        if all(col in filtrado.columns for col in ["ano", "obeso"]):
            serie = agregar_ponderado(filtrado, ["ano"], "obeso") if ponderado else filtrado.groupby("ano", as_index=False)["obeso"].mean().rename(columns={"obeso": "valor"})
            if not serie.empty:
                if "valor_pct" not in serie.columns:
                    serie["valor_pct"] = serie["valor"] * 100
                fig = px.line(
                    serie.sort_values("ano"),
                    x="ano",
                    y="valor_pct",
                    markers=True,
                    title="Prevalência de obesidade por ano",
                    labels={"ano": "Ano", "valor_pct": "%"},
                    template="plotly_dark",
                )
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        if all(col in filtrado.columns for col in ["cidade_nome", "sobrepeso"]):
            cidade_prev = agregar_ponderado(filtrado, ["cidade_nome"], "sobrepeso") if ponderado else filtrado.groupby("cidade_nome", as_index=False)["sobrepeso"].mean().rename(columns={"sobrepeso": "valor"})
            if not cidade_prev.empty:
                if "valor_pct" not in cidade_prev.columns:
                    cidade_prev["valor_pct"] = cidade_prev["valor"] * 100
                cidade_prev = cidade_prev.sort_values("valor_pct", ascending=False).head(10)
                fig = px.bar(
                    cidade_prev,
                    x="valor_pct",
                    y="cidade_nome",
                    orientation="h",
                    color="valor_pct",
                    color_continuous_scale="Tealgrn",
                    title="Top 10 cidades por prevalência de sobrepeso",
                    labels={"valor_pct": "%", "cidade_nome": "Cidade"},
                    template="plotly_dark",
                )
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

with aba2:
    if all(col in filtrado.columns for col in ["sexo", "obeso"]):
        sexo_prev = agregar_ponderado(filtrado, ["sexo"], "obeso") if ponderado else filtrado.groupby("sexo", as_index=False)["obeso"].mean().rename(columns={"obeso": "valor"})
        if not sexo_prev.empty:
            if "valor_pct" not in sexo_prev.columns:
                sexo_prev["valor_pct"] = sexo_prev["valor"] * 100
            fig = px.bar(
                sexo_prev,
                x="sexo",
                y="valor_pct",
                color="sexo",
                title="Obesidade por sexo",
                labels={"valor_pct": "%"},
                template="plotly_dark",
            )
            st.plotly_chart(fig, use_container_width=True)

with aba3:
    if all(col in filtrado.columns for col in ["faixa_idade", "sobrepeso"]):
        faixa_prev = agregar_ponderado(filtrado, ["faixa_idade"], "sobrepeso") if ponderado else filtrado.groupby("faixa_idade", as_index=False, observed=False)["sobrepeso"].mean().rename(columns={"sobrepeso": "valor"})
        if not faixa_prev.empty:
            if "valor_pct" not in faixa_prev.columns:
                faixa_prev["valor_pct"] = faixa_prev["valor"] * 100
            fig = px.bar(
                faixa_prev,
                x="faixa_idade",
                y="valor_pct",
                color="valor_pct",
                color_continuous_scale="Blues",
                title="Sobrepeso por faixa etária",
                labels={"valor_pct": "%", "faixa_idade": "Faixa etária"},
                template="plotly_dark",
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

with aba4:
    if all(col in filtrado.columns for col in ["esc_grupo", "obeso"]):
        esc_prev = agregar_ponderado(filtrado, ["esc_grupo"], "obeso") if ponderado else filtrado.groupby("esc_grupo", as_index=False, observed=False)["obeso"].mean().rename(columns={"obeso": "valor"})
        if not esc_prev.empty:
            if "valor_pct" not in esc_prev.columns:
                esc_prev["valor_pct"] = esc_prev["valor"] * 100
            fig = px.bar(
                esc_prev,
                x="esc_grupo",
                y="valor_pct",
                color="esc_grupo",
                title="Obesidade por escolaridade",
                labels={"valor_pct": "%", "esc_grupo": "Escolaridade"},
                template="plotly_dark",
            )
            st.plotly_chart(fig, use_container_width=True)

with aba5:
    st.subheader("Base filtrada")
    colunas_prioritarias = [
        "ano", "cidade_nome", "sexo", "idade", "faixa_idade", "esc_grupo",
        "peso_kg", "altura_cm", "imc", "cat_imc", "sobrepeso", "obeso", "peso_amostral"
    ]
    colunas_visiveis = [c for c in colunas_prioritarias if c in filtrado.columns]
    st.dataframe(filtrado[colunas_visiveis], use_container_width=True, height=420)

    csv_bytes = filtrado[colunas_visiveis].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Baixar CSV filtrado",
        data=csv_bytes,
        file_name="vigitel_filtrado.csv",
        mime="text/csv",
    )
with aba6:

    st.subheader("🌐 Rede Nacional do Vigitel")

    df_mapa = pd.DataFrame([
        {
            "cidade": cidade,
            "lat": coord[0],
            "lon": coord[1]
        }

        for cidade, coord in COORDS_VIGITEL.items()
    ])

    fig = go.Figure()

    # Brasília

    lat_df = COORDS_VIGITEL["Distrito Federal"][0]
    lon_df = COORDS_VIGITEL["Distrito Federal"][1]


    # ARESTAS

    for cidade, (lat, lon) in COORDS_VIGITEL.items():

        if cidade == "Distrito Federal":
            continue

        fig.add_trace(

            go.Scattermap(

                mode="lines",

                lat=[lat_df, lat],

                lon=[lon_df, lon],

                line=dict(
                    width=1,
                    color="rgba(0,212,255,0.5)"
                ),

                hoverinfo='skip',

                showlegend=False

            )

        )


    # NÓS

    fig.add_trace(

        go.Scattermap(

            mode="markers+text",

            lat=df_mapa["lat"],

            lon=df_mapa["lon"],

            text=df_mapa["cidade"],

            textposition="top center",

            hovertext=df_mapa["cidade"],

            hoverinfo="text",

            marker=dict(

                size=[
                    18 if x=="Distrito Federal" else 10
                    for x in df_mapa["cidade"]
                ],

                color=[

                    "#FF4B4B"
                    if x=="Distrito Federal"

                    else "#00D4FF"

                    for x in df_mapa["cidade"]
                ]

            ),

            showlegend=False

        )

    )


    fig.update_layout(

        map_style="carto-darkmatter",

        margin={"l":0,"r":0,"t":0,"b":0},

        height=700,

        title="Cobertura Nacional do Vigitel"

    )


    fig.update_layout(

        map=dict(

            center=dict(

                lat=-14,

                lon=-54

            ),

            zoom=3.2

        )

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
