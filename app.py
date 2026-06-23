import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Consumo A4351", layout="wide")

st.title("⚡ Análisis Gerencial de Consumo – A4351")

# =========================
# 📂 CARGA EXCEL
# =========================
file_path = "CONSUMO A4351 2 AÑOS.xlsx"
df = pd.read_excel(file_path)

# limpieza de columnas
df.columns = df.columns.astype(str).str.strip()

suministro_col = df.columns[0]
meses = df.columns[1:]

# convertir a numérico seguro
for col in meses:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# 📉 SOLO ÚLTIMOS 2 MESES
# =========================
df["Mes_Anterior"] = df[meses[-2]]
df["Ultimo_Mes"] = df[meses[-1]]

# variación %
df["Variacion_%"] = (
    (df["Ultimo_Mes"] - df["Mes_Anterior"]) /
    df["Mes_Anterior"].replace(0, np.nan)
) * 100

# porcentaje absoluto (sin signo)
df["Variacion_%"] = df["Variacion_%"].abs()

# =========================
# 🚨 CLASIFICACIÓN
# =========================
def clasificar(row):
    if pd.isna(row["Ultimo_Mes"]) or row["Ultimo_Mes"] == 0:
        return "Consumo Cero"

    cambio = row["Ultimo_Mes"] - row["Mes_Anterior"]

    if row["Variacion_%"] <= 20:
        return "Consumo Normal"
    elif row["Variacion_%"] <= 50:
        return "Variación Moderada"
    else:
        if cambio < 0:
            return "Caída Crítica"
        else:
            return "Incremento Alto"

df["Estado"] = df.apply(clasificar, axis=1)

# =========================
# 🎨 COLORES
# =========================
color_map = {
    "Consumo Cero": "black",
    "Consumo Normal": "green",
    "Variación Moderada": "orange",
    "Caída Crítica": "red",
    "Incremento Alto": "blue"
}

# =========================
# 📊 RESUMEN GERENCIAL
# =========================
st.subheader("📌 Resumen Gerencial")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("⚫ Cero", len(df[df["Estado"] == "Consumo Cero"]))
col2.metric("🟢 Normal", len(df[df["Estado"] == "Consumo Normal"]))
col3.metric("🟡 Moderado", len(df[df["Estado"] == "Variación Moderada"]))
col4.metric("🔴 Caída Crítica", len(df[df["Estado"] == "Caída Crítica"]))
col5.metric("🔵 Incremento Alto", len(df[df["Estado"] == "Incremento Alto"]))

# =========================
# 📋 TABLA DE ALERTAS
# =========================
st.subheader("📋 Alertas de Consumo")

alertas = df[df["Estado"] != "Consumo Normal"][
    [suministro_col, "Mes_Anterior", "Ultimo_Mes", "Variacion_%", "Estado"]
]

st.dataframe(alertas, use_container_width=True)

# =========================
# 🔍 SELECCIÓN
# =========================
st.subheader("📊 Análisis por Suministro")

suministro_sel = st.selectbox(
    "Selecciona suministro",
    df[suministro_col].astype(str)
)

fila = df[df[suministro_col].astype(str) == suministro_sel].iloc[0]

# =========================
# 📊 GRÁFICO ÚLTIMOS MESES
# =========================
ultimos_meses = list(meses[-12:])

values = []
colors = []

for col in ultimos_meses:
    v = pd.to_numeric(fila[col], errors="coerce")
    values.append(v)

    if pd.isna(v):
        colors.append("gray")
    elif v == 0:
        colors.append("black")
    elif v < np.nanmean(values) * 0.6:
        colors.append("red")
    else:
        colors.append("steelblue")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=ultimos_meses,
    y=values,
    marker_color=colors
))

fig.update_layout(
    title=f"Consumo histórico últimos meses – {suministro_sel}",
    xaxis_title="Meses",
    yaxis_title="Consumo",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# 📉 RANKING
# =========================
st.subheader("📉 Ranking de Variación")

ranking = df.sort_values("Variacion_%", ascending=False)

st.dataframe(
    ranking[[suministro_col, "Mes_Anterior", "Ultimo_Mes", "Variacion_%", "Estado"]],
    use_container_width=True
)

# =========================
# 📌 NOTA
# =========================
st.info("🟢 Normal: ≤20% | 🟡 Moderado: 20–50% | 🔴 Crítico: caída >40% | 🔵 Incremento alto: >50%")
