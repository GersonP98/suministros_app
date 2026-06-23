# =========================================================
# DASHBOARD CONTROL DE PÉRDIDAS A4351
# PARTE 1/2
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Control de Pérdidas A4351",
    layout="wide"
)


# =========================================================
# ESTILO PROFESIONAL
# =========================================================

st.markdown(
"""
<style>

.stApp {

background-color: #F5F7FA;

}


h1, h2, h3 {

color:#0B1F33;

}


[data-testid="metric-container"] {

background-color:white;

padding:15px;

border-radius:12px;

box-shadow:0px 2px 8px #cccccc;

}


div[data-testid="stDataFrame"] {

background:white;

}


</style>
""",
unsafe_allow_html=True
)



# =========================================================
# CARGA DE DATA
# =========================================================

archivo = "CONSUMO A4351 2 AÑOS.xlsx"


df = pd.read_excel(archivo)



# limpieza columnas

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)



col_suministro = df.columns[0]


meses = df.columns[1:]



# convertir consumos

for m in meses:

    df[m] = pd.to_numeric(
        df[m],
        errors="coerce"
    )



# eliminar registros vacíos

df = df.dropna(
    subset=[col_suministro]
)



# =========================================================
# ÚLTIMOS 12 MESES
# =========================================================


meses_12 = list(meses[-12:])


df["Promedio_12M"] = (
    df[meses_12]
    .mean(axis=1)
)



df["Ultimo_Mes"] = (
    df[meses_12[-1]]
)



df["Mes_Anterior"] = (
    df[meses_12[-2]]
)



# =========================================================
# VARIACIÓN %
# =========================================================


df["Diferencia_kWh"] = (

    df["Ultimo_Mes"]
    -
    df["Mes_Anterior"]

)



df["Variacion_%"] = (

    abs(

        df["Diferencia_kWh"]

        /

        df["Mes_Anterior"]
        .replace(0,np.nan)

    )

    *100

)



df["Tipo_Cambio"] = np.where(

    df["Diferencia_kWh"] < 0,

    "Caída",

    "Incremento"

)



# =========================================================
# ENERGÍA PERDIDA
# COMPARACIÓN CONTRA PROMEDIO 12 MESES
# =========================================================


df["Energia_Esperada"] = (
    df["Promedio_12M"]
)



df["Energia_Perdida_kWh"] = np.where(

    df["Ultimo_Mes"] < df["Promedio_12M"],

    df["Promedio_12M"]
    -
    df["Ultimo_Mes"],

    0

)



# =========================================================
# CLASIFICACIÓN
# =========================================================


def clasificar(row):


    consumo12 = row[meses_12].sum()


    consumo6 = row[meses_12[-6:]].sum()



    if consumo12 == 0:

        return "⚫ Consumo Cero 12 meses"



    elif consumo6 == 0:

        return "🟣 Aviso Consumo 6 meses"



    elif (
        row["Tipo_Cambio"]=="Caída"
        and row["Variacion_%"]>40
    ):

        return "🔴 Caída Crítica"



    elif (
        row["Tipo_Cambio"]=="Caída"
        and row["Variacion_%"]>20
    ):

        return "🟠 Caída Consumo"



    elif (
        row["Tipo_Cambio"]=="Incremento"
        and row["Variacion_%"]>50
    ):

        return "🔵 Incremento Alto"



    else:

        return "🟢 Consumo Normal"



df["Estado"] = df.apply(
    clasificar,
    axis=1
)



# =========================================================
# FUNCIONES DE UNIDADES
# =========================================================


def formato_energia(valor):


    if valor >= 1000000:

        return (
            f"{valor/1000000:.2f} GWh"
        )

    else:

        return (
            f"{valor:,.0f} kWh"
        )



# =========================================================
# TÍTULO
# =========================================================


st.title(
"⚡ Sistema de Control de Pérdidas - Alimentador A4351"
)


st.caption(
"Análisis automático de consumos, pérdidas energéticas y anomalías de suministro - Últimos 12 meses"
)



# =========================================================
# KPI GERENCIALES
# =========================================================


energia_perdida_total = (
    df["Energia_Perdida_kWh"]
    .sum()
)



caidas = len(
    df[
    df["Estado"]=="🔴 Caída Crítica"
    ]
)



cero = len(
    df[
    df["Estado"]=="⚫ Consumo Cero 12 meses"
    ]
)



avisos = len(
    df[
    df["Estado"]=="🟣 Aviso Consumo 6 meses"
    ]
)



consumo_total_actual = (
    df["Ultimo_Mes"]
    .sum()
)



a,b,c,d,e = st.columns(5)


a.metric(
"📌 Suministros",
len(df)
)


b.metric(
"🔴 Caídas críticas",
caidas
)


c.metric(
"⚫ Consumo cero",
cero
)


d.metric(
"🟣 Inspección",
avisos
)


e.metric(
"⚡ Energía perdida",
formato_energia(
energia_perdida_total
)
)
# =========================================================
# TENDENCIA ALIMENTADOR A4351
# SUMA TOTAL DE TODOS LOS SUMINISTROS
# =========================================================

st.subheader(
"📈 Tendencia Global del Alimentador A4351"
)


tendencia = pd.DataFrame()


tendencia["Mes"] = meses_12


# suma de todos los suministros por mes

tendencia["Consumo_kWh"] = [

    df[m].sum()

    for m in meses_12

]



# conversión unidad

def convertir_unidad(valor):

    if valor >= 1000000:

        return f"{valor/1000000:.2f} GWh"

    else:

        return f"{valor:,.0f} kWh"



tendencia["Unidad"] = tendencia["Consumo_kWh"].apply(
    convertir_unidad
)



# cálculo variación mensual

tendencia["Variacion_%"] = (

    tendencia["Consumo_kWh"]
    .pct_change()
    .abs()
    *
    100

)



tendencia["Tipo"] = np.where(

    tendencia["Consumo_kWh"]
    <
    tendencia["Consumo_kWh"].shift(1),

    "Caída",

    "Incremento"

)



st.dataframe(
    tendencia,
    use_container_width=True
)



# =========================================================
# GRÁFICO DISPERSIÓN ALIMENTADOR
# =========================================================


fig_tendencia = go.Figure()



fig_tendencia.add_trace(

    go.Scatter(

        x=tendencia["Mes"],

        y=tendencia["Consumo_kWh"],

        mode="lines+markers",

        name="Consumo A4351",

        marker=dict(
            size=10
        )

    )

)



fig_tendencia.update_layout(

    title="Consumo mensual acumulado del Alimentador A4351",

    xaxis_title="Mes",

    yaxis_title="Consumo",

    height=500

)



st.plotly_chart(
    fig_tendencia,
    use_container_width=True
)




# =========================================================
# VARIACIÓN MENSUAL %
# =========================================================


st.subheader(
"📉 Variación mensual del Alimentador"
)



fig_var = px.bar(

    tendencia,

    x="Mes",

    y="Variacion_%",

    color="Tipo",

    title="Variación porcentual mensual"

)


fig_var.update_layout(
height=400
)


st.plotly_chart(
fig_var,
use_container_width=True
)





# =========================================================
# TOP 100 SUMINISTROS CRÍTICOS
# =========================================================


st.subheader(
"🔴 Top 100 Suministros con Mayor Impacto"
)



top100 = (

df

.sort_values(

"Energia_Perdida_kWh",

ascending=False

)

.head(100)

)



st.dataframe(

top100[

[

col_suministro,

"Ultimo_Mes",

"Promedio_12M",

"Energia_Perdida_kWh",

"Variacion_%",

"Estado"

]

],

use_container_width=True

)



# gráfico top 20

top20 = top100.head(20)



fig_top = px.bar(

top20,

x=col_suministro,

y="Energia_Perdida_kWh",

color="Estado",

title="Top 20 suministros con mayor energía dejada de consumir"

)


fig_top.update_layout(
height=500
)



st.plotly_chart(

fig_top,

use_container_width=True

)




# =========================================================
# PARETO DE PÉRDIDAS
# =========================================================


st.subheader(
"📊 Pareto 80/20 de Energía Perdida"
)



pareto = (

df

.sort_values(

"Energia_Perdida_kWh",

ascending=False

)

)



pareto["Acumulado_%"]=(

pareto["Energia_Perdida_kWh"]
.cumsum()

/

pareto["Energia_Perdida_kWh"]
.sum()

*

100

)



fig_pareto = go.Figure()



fig_pareto.add_trace(

go.Bar(

x=pareto.head(50)[col_suministro],

y=pareto.head(50)["Energia_Perdida_kWh"],

name="kWh perdido"

)

)



fig_pareto.add_trace(

go.Scatter(

x=pareto.head(50)[col_suministro],

y=pareto.head(50)["Acumulado_%"],

mode="lines+markers",

name="Acumulado %"

)

)



fig_pareto.update_layout(

title="Pareto principales pérdidas",

height=500

)



st.plotly_chart(

fig_pareto,

use_container_width=True

)




# =========================================================
# ANÁLISIS INDIVIDUAL
# =========================================================


st.subheader(
"🔎 Análisis Individual del Suministro"
)



suministro = st.selectbox(

"Seleccione suministro",

df[col_suministro].astype(str)

)



dato = df[

df[col_suministro].astype(str)

==

suministro

].iloc[0]



grafico12 = pd.DataFrame({

"Mes":meses_12,

"Consumo":[

dato[m]

for m in meses_12

]

})



fig_individual = go.Figure()



fig_individual.add_trace(

go.Bar(

x=grafico12["Mes"],

y=grafico12["Consumo"],

name="Consumo mensual"

)

)



fig_individual.add_trace(

go.Scatter(

x=grafico12["Mes"],

y=[dato["Promedio_12M"]]*12,

mode="lines",

name="Promedio 12 meses"

)

)



fig_individual.update_layout(

title=f"Tendencia suministro {suministro}",

height=500

)



st.plotly_chart(

fig_individual,

use_container_width=True

)



# =========================================================
# EXPORTACIÓN
# =========================================================


st.subheader(
"📤 Exportar análisis"
)



excel = df.to_excel(
index=False,
engine="openpyxl"
)
