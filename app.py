import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Análisis de Consumos A4351", layout="wide")

st.title("⚡ Dashboard de Consumo – Alimentador A4351")

# =========================
# 📂 CARGA EXCEL (ROBUSTO)
# =========================
file_path = "CONSUMO A4351 2 AÑOS.xlsx"

df = pd.read_excel(file_path)

# Limpieza de columnas
df.columns = df.columns.astype(str).str.strip()

# =========================
# 🔎 IDENTIFICACIÓN COLUMNAS
# =========================
suministro_col = df.columns[0]
meses = df.columns[1:]

# =========================
# 🧹 CONVERSIÓN SEGURA
# =========================
for col in meses:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# 📉 VARIABLES BASE
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
    if pd.isna(row["Ultimo_Mes"]) or row["Ultimo_Mes"] == 0:
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
color_map = {
    "Consumo Cero": "black",
    "Caída Crítica": "red",
    "Caída de Consumo": "orange",
    "Normal": "green"
}

# =========================
# 📋 ALERTAS
# =========================
st.subheader("📋 Suministros con Alertas")

alertas = df[df["Estado"] != "Normal"][
    [suministro_col, "Ultimo_Mes", "Variacion_%", "Estado"]
]

st.dataframe(alertas, use_container_width=True)

# =========================
# 🔍 SELECTOR SUMINISTRO
# =========================
st.subheader("📊 Análisis por Suministro")

suministro_sel = st.selectbox(
    "Selecciona suministro",
    df[suministro_col].astype(str)
)

fila = df[df[suministro_col].astype(str) == suministro_sel].iloc[0]

# =========================
# 📊 GRÁFICO
# =========================
fig = go.Figure()

colores = []
for v in fila[meses]:
    if pd.isna(v):
        colores.append("gray")
    elif v == 0:
        colores.append("black")
    elif v < fila["Ultimo_Mes"] * 0.6:
        colores.append("red")
    else:
        colores.append("steelblue")

fig.add_trace(go.Bar(
    x=meses,
    y=fila[meses],
    marker_color=colores
))

fig.update_layout(
    title=f"Consumo histórico – {suministro_sel}",
    xaxis_title="Meses",
    yaxis_title="Consumo",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📌 RESUMEN GERENCIAL
# =========================
st.subheader("📌 Resumen Gerencial")

col1, col2, col3, col4 = st.columns(4)

col1.metric("🔴 Críticos", len(df[df["Estado"] == "Caída Crítica"]))
col2.metric("⚠️ Caídas", len(df[df["Estado"] == "Caída de Consumo"]))
col3.metric("⛔ Cero", len(df[df["Estado"] == "Consumo Cero"]))
col4.metric("📊 Total Suministros", len(df))

# =========================
# 📉 LISTA CAÍDAS
# =========================
st.subheader("📉 Ranking de Caídas")

caidas = df[df["Variacion_%"] < 0].copy()
caidas = caidas.sort_values("Variacion_%")

st.dataframe(
    caidas[[suministro_col, "Variacion_%", "Estado"]],
    use_container_width=True
)

# =========================
# 📌 MENSAJE GERENCIAL
# =========================
st.info("🔎 Los valores en rojo indican caídas críticas (>40%). Negro indica consumo cero.")
