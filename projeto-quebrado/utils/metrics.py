import pandas as pd

def media_ponderada(df, valor, peso="peso_amostral"):
    base = df[[valor, peso]].dropna()

    if base.empty:
        return None

    return (
        (base[valor] * base[peso]).sum()
        / base[peso].sum()
    )

def prevalencia_ponderada(df, indicador, peso="peso_amostral"):
    base = df[[indicador, peso]].dropna()

    if base.empty:
        return None

    return (
        (base[indicador] * base[peso]).sum()
        / base[peso].sum()
    )