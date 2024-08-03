import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pydeck as pdk

# Configuração da página
st.set_page_config(page_title="Dashboard Interativo", layout="wide")

# Título do dashboard
st.title("Dashboard Interativo com Streamlit")

# Dados fictícios para demonstração
np.random.seed(42)
data = pd.DataFrame({
    "cidade": ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre"],
    "latitude": [-23.5505, -22.9068, -19.9167, -25.4297, -30.0346],
    "longitude": [-46.6333, -43.1729, -43.9345, -49.2733, -51.2177],
    "população": np.random.randint(1000, 10000, size=5),
    "valor": np.random.rand(5) * 100
})

# Gráfico de Barras
st.subheader("Gráfico de Barras: População por Cidade")
fig_bar = px.bar(data, x="cidade", y="população", color="população", height=400)
st.plotly_chart(fig_bar)

# Gráfico de Pizza
st.subheader("Gráfico de Pizza: Distribuição de Valor")
fig_pie = px.pie(data, values="valor", names="cidade", height=400)
st.plotly_chart(fig_pie)

# Gráfico de Dispersão
st.subheader("Gráfico de Dispersão: Valor vs. População")
fig_scatter = px.scatter(data, x="população", y="valor", size="valor", color="cidade", hover_name="cidade", log_x=True, height=400)
st.plotly_chart(fig_scatter)

# Mapa do Brasil com PyDeck
st.subheader("Mapa Interativo do Brasil")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=data,
    get_position="[longitude, latitude]",
    get_color="[200, 30, 0, 160]",
    get_radius=100000,
)
view_state = pdk.ViewState(
    latitude=-15.7801,
    longitude=-47.9292,
    zoom=3,
    pitch=50,
)
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{cidade}\nPopulação: {população}"})
st.pydeck_chart(r)

# Conclusão
st.markdown("Este é um exemplo de dashboard interativo utilizando Streamlit, Plotly e PyDeck. Explore os gráficos e o mapa interativo para visualizar dados fictícios de cidades brasileiras.")
