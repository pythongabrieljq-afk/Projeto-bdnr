import pandas as pd

def resumo_texto(valor, kind="num"):

    if valor is None or pd.isna(valor):
        return "N/D"

    if kind == "pct":
        return f"{valor * 100:.1f}%"

    if kind == "imc":
        return f"{valor:.2f}"

    if kind == "kg":
        return f"{valor:.1f} kg"

    return f"{valor:,.0f}".replace(",", ".")