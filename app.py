import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


# ==========================================
# CONFIGURACIÓN GENERAL
# ==========================================

st.set_page_config(
    page_title="Control de Pérdidas A4351",
    layout="wide"
)


# ==========================================
# CARGA DATA
# ==========================================

archivo = "CONSUMO A4351 2 AÑOS.xlsx"

df = pd.read_excel(archivo)


# limpiar columnas

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


# primera columna suministro

col_suministro = df.columns[0]


# meses

meses = df.columns[1:]


# convertir consumos

for m in meses:
    df[m] = pd.to_numeric(
        df[m],
        errors="coerce"
    )


# eliminar filas sin suministro

df = df.dropna(
    subset=[col_suministro]
)



# ==========================================
# ÚLTIMOS 12 MESES
# ==========================================

meses_12 = list(meses[-12:])


df["Promedio_12M"] = (
    df[meses_12]
    .mean(axis=1)
)


# último y anterior mes

df["Mes_Actual"] = df[meses_12[-1]]

df["Mes_Anterior"] = df[meses_12[-2]]



# ==========================================
# VARIACIÓN %
# ==========================================

df["Diferencia"] = (
    df["Mes_Actual"]
    -
    df["Mes_Anterior"]
)


df["Variacion_%"] = (
    abs(
        df["Diferencia"]
        /
        df["Mes_Anterior"].replace(0,np.nan)
    )
    *
    100
)



# dirección del cambio

df["Tipo_Cambio"] = np.where(
    df["Diferencia"] < 0,
    "Caída de consumo",
    "Incremento de consumo"
)



# ==========================================
# CONSUMO CERO Y ALERTAS
# ==========================================


def estado_consumo(row):


    consumo12 = row[meses_12].sum()


    consumo6 = row[meses_12[-6:]].sum()


    variacion = row["Variacion_%"]


    diferencia = row["Diferencia"]



    # cero últimos 12 meses

    if consumo12 == 0:

        return "⚫ Consumo Cero 12 meses"



    # cero últimos 6 meses

    elif consumo6 == 0:

        return "🟣 Aviso Consumo 6 meses"



    # caída crítica

    elif diferencia < 0 and variacion > 40:

        return "🔴 Caída Crítica"



    # caída moderada

    elif diferencia < 0 and variacion > 20:

        return "🟠 Caída Consumo"



    # incremento alto

    elif diferencia > 0 and variacion > 50:

        return "🔵 Incremento Alto"



    else:

        return "🟢 Consumo Normal"



df["Estado"] = df.apply(
    estado_consumo,
    axis=1
)



# ==========================================
# COLORES
# ==========================================


colores_estado = {

"⚫ Consumo Cero 12 meses":"black",

"🟣 Aviso Consumo 6 meses":"purple",

"🔴 Caída Crítica":"red",

"🟠 Caída Consumo":"orange",

"🔵 Incremento Alto":"blue",

"🟢 Consumo Normal":"green"

}



# ==========================================
# TÍTULO
# ==========================================


st.title(
    "⚡ Sistema Inteligente de Control de Pérdidas - Alimentador A4351"
)


st.success(
    "Análisis basado en últimos 12 meses de consumo"
)
# ==========================================
# FONDO CONTROL DE PÉRDIDAS
# ==========================================

st.markdown(
"""
<style>

[data-testid="stAppViewContainer"] {

background-image:
linear-gradient(
rgba(255,255,255,0.92),
rgba(255,255,255,0.92)
),
url("https://images.unsplash.com/photo-1473341304170-971dccb5ac1e");

background-size: cover;

}

</style>
""",
unsafe_allow_html=True
)



# ==========================================
# KPI GERENCIALES
# ==========================================

st.subheader("📊 Indicadores de Control de Pérdidas")


k1,k2,k3,k4,k5 = st.columns(5)


k1.metric(
    "Total Suministros",
    len(df)
)


k2.metric(
    "🔴 Caídas Críticas",
    len(
        df[
        df["Estado"]=="🔴 Caída Crítica"
        ]
    )
)


k3.metric(
    "⚫ Consumo Cero 12M",
    len(
        df[
        df["Estado"]=="⚫ Consumo Cero 12 meses"
        ]
    )
)


k4.metric(
    "🟣 Aviso 6 meses",
    len(
        df[
        df["Estado"]=="🟣 Aviso Consumo 6 meses"
        ]
    )
)


k5.metric(
    "🔵 Incrementos >50%",
    len(
        df[
        df["Estado"]=="🔵 Incremento Alto"
        ]
    )
)



# ==========================================
# TABLA ALERTAS
# ==========================================


st.subheader(
"🚨 Suministros Observados"
)


alertas = df[
df["Estado"]!="🟢 Consumo Normal"
]


st.dataframe(
alertas[
[
col_suministro,
"Mes_Anterior",
"Mes_Actual",
"Variacion_%",
"Tipo_Cambio",
"Estado"
]
],
use_container_width=True
)




# ==========================================
# TOP 100 CRÍTICOS
# ==========================================


st.subheader(
"🔴 Top 100 Suministros con Mayor Variación"
)


top100 = (
df
.sort_values(
"Variacion_%",
ascending=False
)
.head(100)
)


st.dataframe(
top100[
[
col_suministro,
"Variacion_%",
"Tipo_Cambio",
"Estado"
]
],
use_container_width=True
)



# gráfico top 20 visual

top20 = top100.head(20)


fig_top = px.bar(
top20,
x=col_suministro,
y="Variacion_%",
color="Estado",
title="Top 20 Variaciones de Consumo"
)


fig_top.update_layout(
height=500
)


st.plotly_chart(
fig_top,
use_container_width=True
)




# ==========================================
# TENDENCIA ALIMENTADOR A4351
# SUMA TOTAL MENSUAL
# ==========================================


st.subheader(
"📈 Tendencia Global del Alimentador A4351"
)


consumo_alimentador = pd.DataFrame()


consumo_alimentador["Mes"] = meses_12


consumo_alimentador["Consumo_Total"] = [
df[m].sum()
for m in meses_12
]



# cálculo variación mensual

consumo_alimentador["Variacion_%"] = (
consumo_alimentador["Consumo_Total"]
.diff()
/
consumo_alimentador["Consumo_Total"].shift(1)
*
100
)



consumo_alimentador["Variacion_%"] = (
consumo_alimentador["Variacion_%"]
.abs()
)



st.dataframe(
consumo_alimentador,
use_container_width=True
)



# gráfico dispersión


fig_tendencia = go.Figure()


fig_tendencia.add_trace(
go.Scatter(
x=consumo_alimentador["Mes"],
y=consumo_alimentador["Consumo_Total"],
mode="lines+markers",
name="Consumo Alimentador"
)
)



fig_tendencia.update_layout(

title="Consumo mensual acumulado A4351",

xaxis_title="Mes",

yaxis_title="kWh",

height=500

)


st.plotly_chart(
fig_tendencia,
use_container_width=True
)




# ==========================================
# PARETO 80/20
# ==========================================


st.subheader(
"📊 Pareto de Variaciones"
)


pareto = (
df
.sort_values(
"Variacion_%",
ascending=False
)
)


pareto["Acumulado_%"] = (
pareto["Variacion_%"]
.cumsum()
/
pareto["Variacion_%"]
.sum()
*
100
)



fig_pareto = go.Figure()


fig_pareto.add_trace(
go.Bar(
x=pareto.head(30)[col_suministro],
y=pareto.head(30)["Variacion_%"],
name="Variación"
)
)


fig_pareto.add_trace(
go.Scatter(
x=pareto.head(30)[col_suministro],
y=pareto.head(30)["Acumulado_%"],
mode="lines+markers",
name="Acumulado %"
)
)


fig_pareto.update_layout(
title="Pareto primeros 30 suministros",
height=500
)


st.plotly_chart(
fig_pareto,
use_container_width=True
)




# ==========================================
# ANALISIS INDIVIDUAL
# ==========================================


st.subheader(
"🔎 Análisis Individual del Suministro"
)


seleccion = st.selectbox(
"Seleccione suministro",
df[col_suministro].astype(str)
)


dato = df[
df[col_suministro].astype(str)
==
seleccion
].iloc[0]



meses_graf = meses_12


valores = [
dato[m]
for m in meses_graf
]



fig_ind = go.Figure()


fig_ind.add_trace(
go.Bar(
x=meses_graf,
y=valores,
name="Consumo mensual"
)
)



fig_ind.add_trace(
go.Scatter(
x=meses_graf,
y=[dato["Promedio_12M"]]*12,
mode="lines",
name="Promedio 12 meses"
)
)



fig_ind.update_layout(
title=f"Tendencia suministro {seleccion}",
height=500
)



st.plotly_chart(
fig_ind,
use_container_width=True
)
