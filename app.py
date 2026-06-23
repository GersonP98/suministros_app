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

df.columns = df.columns.astype(str).str.strip()

suministro_col = df.columns[0]
meses = df.columns[1:]

# convertir a numérico seguro
for col in meses:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# =========================
# 📊 SOLO ÚLTIMOS 2 MESES (VARIACIÓN)
# =========================
df["Mes_Anterior"] = df[meses[-2]]
df["Ultimo_Mes"] = df[meses[-1]]

df["Variacion_%"] = (
    (df["Ultimo_Mes"] - df["Mes_Anterior"]) /
    df["Mes_Anterior"].replace(0, np.nan)
) * 100

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
# 📊 🔥 NUEVO: ÚLTIMOS 6 MESES + PROMEDIO
# =========================
ultimos_6 = meses[-6:]

df["Promedio_6M"] = df[ultimos_6].mean(axis=1)

# =========================
# 📌 RESUMEN GERENCIAL
# =========================
st.subheader("📌 Resumen Gerencial")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("⚫ Cero", len(df[df["Estado"] == "Consumo Cero"]))
col2.metric("🟢 Normal", len(df[df["Estado"] == "Consumo Normal"]))
col3.metric("🟡 Moderado", len(df[df["Estado"] == "Variación Moderada"]))
col4.metric("🔴 Crítico", len(df[df["Estado"] == "Caída Crítica"]))
col5.metric("🔵 Alto", len(df[df["Estado"] == "Incremento Alto"]))

# =========================
# 📋 TABLA GERENCIAL (CON PROMEDIO)
# =========================
st.subheader("📋 Tabla de Consumos (Últimos 6 meses)")

tabla = df[[suministro_col] + list(ultimos_6) + ["Promedio_6M", "Estado"]]

st.dataframe(tabla, use_container_width=True)

# =========================
# 🔍 SELECCIÓN SUMINISTRO
# =========================
st.subheader("📊 Análisis por Suministro")

suministro_sel = st.selectbox(
    "Selecciona suministro",
    df[suministro_col].astype(str)
)

fila = df[df[suministro_col].astype(str) == suministro_sel].iloc[0]

# =========================
# 📊 GRÁFICO ÚLTIMOS 6 MESES + PROMEDIO
# =========================
values = []
colors = []

for col in ultimos_6:
    v = pd.to_numeric(fila[col], errors="coerce")
    values.append(v)

    if pd.isna(v):
        colors.append("gray")
    elif v == 0:
        colors.append("black")
    elif v < fila["Promedio_6M"] * 0.8:
        colors.append("red")
    else:
        colors.append("steelblue")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=ultimos_6,
    y=values,
    marker_color=colors,
    name="Consumo mensual"
))

# línea de promedio
fig.add_trace(go.Scatter(
    x=ultimos_6,
    y=[fila["Promedio_6M"]] * len(ultimos_6),
    mode="lines",
    name="Promedio 6M",
    line=dict(color="green", width=3)
))

fig.update_layout(
    title=f"Consumo últimos 6 meses – {suministro_sel}",
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
    ranking[[suministro_col, "Mes_Anterior", "Ultimo_Mes", "Variacion_%", "Promedio_6M", "Estado"]],
    use_container_width=True
)

# =========================
# 📌 NOTA
# =========================
st.info("📊 Se muestran los últimos 6 meses + promedio como referencia gerencial.")
