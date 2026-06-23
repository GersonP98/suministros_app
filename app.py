import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Análisis de Consumos A4351", layout="wide")

st.title("⚡ Análisis de Consumo – Alimentador A4351")

# =========================
# 📂 CARGA DE ARCHIVO
# =========================
file_path = "CONSUMO A4351 2 AÑOS.xlsx"
df = pd.read_excel(file_path)

# =========================
# 🧹 LIMPIEZA BÁSICA
# =========================
df.columns = df.columns.str.strip()

# Suponemos formato típico:
# Columna 0 = Suministro
# resto = meses

suministro_col = df.columns[0]
meses = df.columns[1:]

df[meses] = df[meses].apply(pd.to_numeric, errors="coerce")

# =========================
# 📉 CÁLCULO VARIACIÓN
# =========================
df["Ultimo_Mes"] = df[meses[-1]]
df["Mes_Anterior"] = df[meses[-2]]

df["Variacion_%"] = (
    (df["Ultimo_Mes"] - df["Mes_Anterior"]) /
    df["Mes_Anterior"].replace(0, np.nan)
) * 100

# =========================
# 🚨 CLASIFICACIÓN
# =========================
def clasificar(row):
    if row["Ultimo_Mes"] == 0:
        return "Consumo Cero"
    elif row["Variacion_%"] <= -40:
        return "Caída Crítica"
    elif row["Variacion_%"] < 0:
        return "Caída de Consumo"
    else:
        return "Normal"

df["Estado"] = df.apply(clasificar, axis=1)

# =========================
# 🎨 COLORES
# =========================
colores = {
    "Consumo Cero": "black",
    "Caída Crítica": "red",
    "Caída de Consumo": "orange",
    "Normal": "green"
}

# =========================
# 📋 TABLA DE ALERTAS
# =========================
st.subheader("📋 Lista de Suministros con Alertas")

alertas = df[df["Estado"] != "Normal"][
    [suministro_col, "Ultimo_Mes", "Variacion_%", "Estado"]
]

st.dataframe(alertas, use_container_width=True)

# =========================
# 🔍 SELECTOR DE SUMINISTRO
# =========================
st.subheader("📊 Análisis por Suministro")

suministro_sel = st.selectbox(
    "Selecciona un suministro",
    df[suministro_col]
)

fila = df[df[suministro_col] == suministro_sel].iloc[0]

# =========================
# 📊 GRÁFICO DE BARRAS
# =========================
fig = go.Figure()

colores_barras = []
for v in fila[meses]:
    if v == 0:
        colores_barras.append("black")
    elif v < fila["Ultimo_Mes"] * 0.6:
        colores_barras.append("red")
    else:
        colores_barras.append("steelblue")

fig.add_trace(go.Bar(
    x=meses,
    y=fila[meses],
    marker_color=colores_barras
))

fig.update_layout(
    title=f"Consumo histórico – {suministro_sel}",
    xaxis_title="Mes",
    yaxis_title="Consumo",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📌 RESUMEN GERENCIAL
# =========================
st.subheader("📌 Resumen Gerencial")

col1, col2, col3 = st.columns(3)

col1.metric("🔴 Críticos", len(df[df["Estado"] == "Caída Crítica"]))
col2.metric("⚠️ Caídas", len(df[df["Estado"] == "Caída de Consumo"]))
col3.metric("⛔ Consumo Cero", len(df[df["Estado"] == "Consumo Cero"]))

# =========================
# 📉 LISTA DETALLADA CAÍDAS
# =========================
st.subheader("📉 Caídas de Consumo (1% - 100%)")

caidas = df[df["Variacion_%"] < 0].copy()
caidas = caidas.sort_values("Variacion_%")

st.dataframe(caidas[[suministro_col, "Variacion_%", "Estado"]])
