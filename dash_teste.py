import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Título do dashboard
st.title("Dashboard Exemplo com Streamlit")

# Descrição
st.write("Este é um exemplo de dashboard criado com Streamlit.")

# Dados de exemplo
data = {
    'Ano': [2020, 2021, 2022, 2023],
    'Vendas': [1500, 2300, 1800, 2000],
    'Despesas': [500, 700, 800, 600],
    'Lucro': [1000, 1600, 1000, 1400]
}

df = pd.DataFrame(data)

# Exibir tabela
st.subheader("Tabela de Dados")
st.table(df)

# Gráfico de linha
st.subheader("Gráfico de Linha")
fig, ax = plt.subplots()
ax.plot(df['Ano'], df['Vendas'], label='Vendas')
ax.plot(df['Ano'], df['Despesas'], label='Despesas')
ax.plot(df['Ano'], df['Lucro'], label='Lucro')
ax.set_xlabel('Ano')
ax.set_ylabel('Valores')
ax.set_title('Vendas, Despesas e Lucro ao longo dos anos')
ax.legend()
st.pyplot(fig)

# Seletor de ano
ano_selecionado = st.selectbox("Selecione um ano para ver os detalhes:", df['Ano'])

# Detalhes do ano selecionado
st.subheader(f"Detalhes para o ano {ano_selecionado}")
ano_df = df[df['Ano'] == ano_selecionado]
st.write(ano_df)

# Calcular métricas
vendas_total = df['Vendas'].sum()
despesas_total = df['Despesas'].sum()
lucro_total = df['Lucro'].sum()

# Exibir métricas
st.subheader("Métricas Totais")
st.metric("Vendas Totais", f"${vendas_total}")
st.metric("Despesas Totais", f"${despesas_total}")
st.metric("Lucro Total", f"${lucro_total}")

# Seção de barra lateral
st.sidebar.header("Configurações")
vendas_min = st.sidebar.slider("Filtrar Vendas Mínimas", min_value=int(df['Vendas'].min()), max_value=int(df['Vendas'].max()), value=int(df['Vendas'].min()))
filtrado_df = df[df['Vendas'] >= vendas_min]

st.sidebar.subheader("Tabela Filtrada")
st.sidebar.table(filtrado_df)
