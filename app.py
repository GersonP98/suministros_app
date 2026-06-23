# =====================================================
# DASHBOARD CONTROL DE PERDIDAS A4351
# VERSION GERENCIAL 12 MESES
# =====================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO


# =====================================================
# CONFIGURACION
# =====================================================

st.set_page_config(
    page_title="Control de Perdidas A4351",
    layout="wide"
)


# =====================================================
# ESTILO SIN FONDO
# =====================================================

st.markdown(
"""
<style>

.stApp{
background-color:white;
}


h1,h2,h3,h4{
color:#0B1F33;
font-family:Arial;
}


[data-testid="metric-container"]{

background-color:#F7F9FC;

border-radius:10px;

padding:15px;

border:1px solid #D9E2F3;

}


</style>

""",
unsafe_allow_html=True
)



# =====================================================
# TITULO
# =====================================================


st.title(
"⚡ Sistema de Control de Pérdidas - Alimentador A4351"
)


st.write(
"Análisis de consumo, anomalías y energía dejada de consumir basado en últimos 12 meses"
)



# =====================================================
# CARGA EXCEL
# =====================================================


archivo = "CONSUMO A4351 2 AÑOS.xlsx"


df = pd.read_excel(
    archivo
)



# limpiar nombres

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



# quitar vacíos

df = df.dropna(
    subset=[col_suministro]
)



# =====================================================
# ULTIMOS 12 MESES
# =====================================================


meses_12 = list(
    meses[-12:]
)



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



# =====================================================
# VARIACION %
# =====================================================


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

    "Caída de consumo",

    "Incremento de consumo"

)



# =====================================================
# ENERGIA PERDIDA
# CONTRA PROMEDIO 12 MESES
# =====================================================


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



# =====================================================
# CLASIFICACION
# =====================================================


def clasificar(row):


    consumo12 = row[meses_12].sum()


    consumo6 = row[meses_12[-6:]].sum()



    if consumo12 == 0:

        return "⚫ Consumo Cero 12 meses"


    elif consumo6 == 0:

        return "🟣 Aviso Consumo 6 meses"


    elif (
        row["Tipo_Cambio"]=="Caída de consumo"
        and row["Variacion_%"]>40
    ):

        return "🔴 Caída Crítica"


    elif (
        row["Tipo_Cambio"]=="Caída de consumo"
        and row["Variacion_%"]>20
    ):

        return "🟠 Caída Consumo"


    elif (
        row["Tipo_Cambio"]=="Incremento de consumo"
        and row["Variacion_%"]>50
    ):

        return "🔵 Incremento Alto"


    else:

        return "🟢 Consumo Normal"



df["Estado"] = df.apply(
    clasificar,
    axis=1
)



# =====================================================
# FORMATO ENERGIA
# =====================================================


def energia(valor):

    if valor >= 1000000:

        return (
            f"{valor/1000000:.2f} GWh"
        )

    else:

        return (
            f"{valor:,.0f} kWh"
        )
        # =====================================================
# KPI GERENCIALES
# =====================================================


st.subheader(
    "📊 Indicadores Gerenciales de Control de Pérdidas"
)



energia_perdida_total = (
    df["Energia_Perdida_kWh"]
    .sum()
)



consumo_actual_total = (
    df["Ultimo_Mes"]
    .sum()
)



consumo_promedio_total = (
    df["Promedio_12M"]
    .sum()
)



porcentaje_caida_global = (

    abs(
        (consumo_actual_total -
         consumo_promedio_total)

        /

        consumo_promedio_total
    )

    *100

)



criticos = len(
    df[
        df["Estado"]=="🔴 Caída Crítica"
    ]
)



consumo_cero = len(
    df[
        df["Estado"]=="⚫ Consumo Cero 12 meses"
    ]
)



inspeccion = len(
    df[
        df["Estado"]=="🟣 Aviso Consumo 6 meses"
    ]
)



a,b,c,d,e,f = st.columns(6)



a.metric(
    "📌 Suministros",
    len(df)
)



b.metric(
    "🔴 Caídas críticas",
    criticos
)



c.metric(
    "⚫ Consumo cero 12M",
    consumo_cero
)



d.metric(
    "🟣 Inspección",
    inspeccion
)



e.metric(
    "⚡ Energía perdida",
    energia(energia_perdida_total)
)



f.metric(
    "📉 Caída global",
    f"{porcentaje_caida_global:.1f}%"
)





# =====================================================
# TABLA DE SUMINISTROS OBSERVADOS
# =====================================================


st.subheader(
    "🚨 Suministros Observados"
)



observados = df[
    df["Estado"]!="🟢 Consumo Normal"
]



st.dataframe(

    observados[
        [
        col_suministro,
        "Ultimo_Mes",
        "Promedio_12M",
        "Variacion_%",
        "Energia_Perdida_kWh",
        "Tipo_Cambio",
        "Estado"
        ]
    ],

    use_container_width=True

)





# =====================================================
# TENDENCIA DEL ALIMENTADOR A4351
# SUMA TOTAL MENSUAL
# =====================================================


st.subheader(
    "📈 Tendencia del Alimentador A4351 - Últimos 12 meses"
)



tendencia = pd.DataFrame()



tendencia["Mes"] = meses_12



tendencia["Consumo_kWh"] = [

    df[m].sum()

    for m in meses_12

]



tendencia["Consumo"] = (
    tendencia["Consumo_kWh"]
    .apply(energia)
)



# variación mensual

tendencia["Variacion_%"] = (

    tendencia["Consumo_kWh"]
    .pct_change()
    .abs()
    *
    100

)



tendencia["Cambio"] = np.where(

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




# =====================================================
# GRAFICO TENDENCIA DISPERSION
# =====================================================


fig_tendencia = go.Figure()



fig_tendencia.add_trace(

    go.Scatter(

        x=tendencia["Mes"],

        y=tendencia["Consumo_kWh"],

        mode="lines+markers",

        name="Consumo A4351",

        marker=dict(
            size=12
        )

    )

)



fig_tendencia.update_layout(

    title=
    "Comportamiento energético del Alimentador A4351",

    xaxis_title="Mes",

    yaxis_title="kWh",

    height=500

)



st.plotly_chart(

    fig_tendencia,

    use_container_width=True

)





# =====================================================
# VARIACION MENSUAL ALIMENTADOR
# =====================================================


st.subheader(
    "📉 Variación mensual del Alimentador"
)



fig_variacion = px.bar(

    tendencia,

    x="Mes",

    y="Variacion_%",

    color="Cambio",

    text="Variacion_%",

    title="Variación porcentual mensual A4351"

)



fig_variacion.update_traces(
texttemplate="%{text:.1f}%"
)



fig_variacion.update_layout(
height=450
)



st.plotly_chart(

    fig_variacion,

    use_container_width=True

)





# =====================================================
# TOP 100 SUMINISTROS POR ENERGIA PERDIDA
# =====================================================


st.subheader(
"🔴 Top 100 Suministros con Mayor Energía No Consumida"
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
        "Promedio_12M",
        "Ultimo_Mes",
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

    title=
    "Top 20 suministros con mayor energía perdida"

)



fig_top.update_layout(
height=500
)



st.plotly_chart(

    fig_top,

    use_container_width=True

)
# ==============================
# PARTE 3: KPIs AVANZADOS + ANÁLISIS DE PÉRDIDAS + GWH
# ==============================

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.header("📊 Análisis Avanzado de Energía y Pérdidas")

# ------------------------------
# 1. PREPARACIÓN DE DATOS
# ------------------------------
df["Fecha"] = pd.to_datetime(df["Fecha"])

# Ajusta el nombre de tu columna de consumo si es diferente
col_consumo = [c for c in df.columns if "kwh" in c.lower()][0]

df = df.sort_values("Fecha")

# Agrupar por mes
df["Mes"] = df["Fecha"].dt.to_period("M").astype(str)
consumo_mensual = df.groupby("Mes")[col_consumo].sum().reset_index()

# Convertir kWh a GWh
consumo_mensual["GWh"] = consumo_mensual[col_consumo] / 1_000_000

# ------------------------------
# 2. KPI PRINCIPAL
# ------------------------------
total_kwh = df[col_consumo].sum()
total_gwh = total_kwh / 1_000_000

st.subheader("⚡ KPIs Generales")

col1, col2, col3 = st.columns(3)

col1.metric("Consumo Total (kWh)", f"{total_kwh:,.0f}")
col2.metric("Consumo Total (GWh)", f"{total_gwh:.2f}")
col3.metric("Meses analizados", df["Mes"].nunique())

# ------------------------------
# 3. ESTIMACIÓN DE PÉRDIDAS
# ------------------------------
# Supuesto: pérdidas técnicas promedio 8% (ajustable)
perdida_pct = 0.08

df["Perdida_kWh"] = df[col_consumo] * perdida_pct

total_perdidas_kwh = df["Perdida_kWh"].sum()
total_perdidas_gwh = total_perdidas_kwh / 1_000_000

st.subheader("⚠️ Pérdidas de Energía Estimadas")

col4, col5 = st.columns(2)

col4.metric("Pérdidas (kWh)", f"{total_perdidas_kwh:,.0f}")
col5.metric("Pérdidas (GWh)", f"{total_perdidas_gwh:.2f}")

# ------------------------------
# 4. TENDENCIA MENSUAL EN GWh
# ------------------------------
st.subheader("📈 Tendencia mensual de consumo (GWh)")

fig, ax = plt.subplots()
ax.plot(consumo_mensual["Mes"], consumo_mensual["GWh"], marker="o")
ax.set_title("Consumo energético mensual")
ax.set_xlabel("Mes")
ax.set_ylabel("GWh")
plt.xticks(rotation=45)

st.pyplot(fig)

# ------------------------------
# 5. CAÍDA O VARIACIÓN DE CONSUMO
# ------------------------------
consumo_mensual["Variacion_%"] = consumo_mensual["GWh"].pct_change() * 100

caida_total = consumo_mensual["GWh"].iloc[-1] - consumo_mensual["GWh"].iloc[0]

st.subheader("📉 Variación de consumo")

st.metric("Cambio total (GWh)", f"{caida_total:.2f}")

# ------------------------------
# 6. EXPORTAR RESULTADOS
# ------------------------------
st.subheader("⬇️ Exportar datos")

export = consumo_mensual.copy()
export["Perdidas_GWh"] = export["GWh"] * perdida_pct

csv = export.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar análisis en CSV",
    data=csv,
    file_name="analisis_energia.csv",
    mime="text/csv"
)
