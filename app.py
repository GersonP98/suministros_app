import streamlit as st
import pandas as pd

st.set_page_config(page_title="SIGEPER", layout="wide")

st.title("SIGEPER - Sistema de Gestión y Evaluación de Pérdidas Eléctricas")
st.subheader("Analizador de caída de consumos A4351")

archivo = st.file_uploader("Cargar Excel de consumos", type="xlsx")

if archivo:
    df = pd.read_excel(archivo)
    st.dataframe(df.head())

    meses = [c for c in df.columns if "-" in str(c)]

    if len(meses) >= 12:
        ultimo = meses[-1]
        historico = meses[-13:-1]

        df["PROM_12_MESES"] = df[historico].mean(axis=1)
        df["CAIDA_%"] = ((df["PROM_12_MESES"]-df[ultimo]) / df["PROM_12_MESES"])*100

        df["DIAGNOSTICO"] = "NORMAL"
        df.loc[df["CAIDA_%"]>=40,"DIAGNOSTICO"]="RIESGO"
        df.loc[df["CAIDA_%"]>=70,"DIAGNOSTICO"]="CRITICO"

        st.metric("Suministros analizados", len(df))
        st.metric("Casos críticos", len(df[df["DIAGNOSTICO"]=="CRITICO"]))

        columnas=[x for x in ["SUMINISTRO","SED","PROM_12_MESES",ultimo,"CAIDA_%","DIAGNOSTICO"] if x in df.columns]

        resultado=df[columnas].sort_values("CAIDA_%",ascending=False)

        st.subheader("Ranking crítico")
        st.dataframe(resultado.head(50))

        st.subheader("Gráfico de barras")
        if "SUMINISTRO" in resultado.columns:
            st.bar_chart(resultado.head(10).set_index("SUMINISTRO")["CAIDA_%"])

        st.subheader("Diagnóstico")
        st.write("Los suministros con caída elevada deben pasar a validación técnica y comercial.")
    else:
        st.warning("Se requieren 12 meses históricos.")
