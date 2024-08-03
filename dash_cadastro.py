import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração do Pandas para exibir mais elementos
pd.set_option("styler.render.max_elements", 2000000)

# Leitura do arquivo Excel
file_path = 'Fonte - Dash Financeiro Backgroundcheck.xlsx'
df_receita = pd.read_excel(file_path, sheet_name='Receita Geral', engine='openpyxl')
df_faturamento = pd.read_excel(file_path, sheet_name='Faturamento por Cliente', engine='openpyxl')

# Converter a coluna 'Data' para o tipo datetime
df_receita['Data'] = pd.to_datetime(df_receita['Data'])
df_faturamento['Data'] = pd.to_datetime(df_faturamento['Data'])

# Criar colunas de Ano e Mês para agrupamentos
df_receita['Ano'] = df_receita['Data'].dt.year
df_receita['Mes'] = df_receita['Data'].dt.to_period('M').astype(str)
df_faturamento['Ano'] = df_faturamento['Data'].dt.year
df_faturamento['Mes'] = df_faturamento['Data'].dt.to_period('M').astype(str)

# Função para calcular o acumulado total
def calculate_total(df, value_col):
    total = df[value_col].sum()
    df['Acumulado_' + value_col] = total
    return df

# Layout da Página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# Barra Superior
st.markdown("""
    <style>
    .title-bar {
        background-color: #FF3F03; /* Laranja escuro */
        color: white;
        padding: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    <div class="title-bar">
        DASHBOARD CADASTRO NSTECH
    </div>
""", unsafe_allow_html=True)

# Filtros Gerais
st.sidebar.title("Filtros")
page = st.sidebar.selectbox("Escolha a Página", ["Receita", "Faturamento por Cliente"])

# Definir intervalos de datas padrão
default_start_date = pd.Timestamp('2024-01-01')
default_end_date = pd.Timestamp.now() - pd.DateOffset(months=1)
default_end_date = default_end_date.replace(day=1) - pd.DateOffset(days=1)

if page == "Receita":
    min_date, max_date = st.sidebar.date_input(
        "Selecionar intervalo de datas",
        [default_start_date, default_end_date]
    )

    selected_company = st.sidebar.selectbox(
        "Selecionar empresa",
        options=['Todas'] + list(df_receita['Empresa'].unique()),
        index=0
    )

elif page == "Faturamento por Cliente":
    min_date, max_date = st.sidebar.date_input(
        "Selecionar intervalo de datas",
        [default_start_date, default_end_date]
    )

    selected_company = st.sidebar.selectbox(
        "Selecionar empresa",
        options=['Todas'] + list(df_faturamento['Empresa'].unique()),
        index=0
    )
    
    client_options = list(df_faturamento['Cliente'].unique())
    selected_clients = st.sidebar.multiselect(
        "Selecionar cliente(s)",
        options=['Selecionar Todos'] + client_options,
        default=['Selecionar Todos']
    )
    
    # Filtro por Classe de Cliente
    class_options = list(df_faturamento['Classe Cliente'].unique())
    selected_class = st.sidebar.multiselect(
        "Selecionar classe(s) de cliente(s)",
        options=['Selecionar Todas'] + class_options,
        default=['Selecionar Todas']
    )

    # Lógica para "Selecionar Todos" e "Selecionar Todas"
    if 'Selecionar Todos' in selected_clients:
        selected_clients = client_options
    if 'Selecionar Todas' in selected_class:
        selected_class = class_options

# Página de Receita
if page == "Receita":
    # Aplicando filtros
    if selected_company != 'Todas':
        df_receita = df_receita[df_receita['Empresa'] == selected_company]

    df_receita_filtered = df_receita[(df_receita['Data'] >= pd.to_datetime(min_date)) & (df_receita['Data'] <= pd.to_datetime(max_date))]

    # Gráficos por Empresa
    companies = df_receita_filtered['Empresa'].unique()
    for company in companies:
        company_data = df_receita_filtered[df_receita_filtered['Empresa'] == company]

        # Gráfico de coluna Real vs Orçado por Mês
        st.subheader(f'Real vs Orçado - {company}')
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=company_data['Mes'],
            y=company_data['Real'],
            name='Real',
            marker_color='#FF3F03',  # Laranja escuro
            text=company_data['Real'].map('R$ {:,.0f}'.format),
            textposition='outside'
        ))
        fig.add_trace(go.Bar(
            x=company_data['Mes'],
            y=company_data['Orçado'],
            name='Orçado',
            marker_color='black',
            text=company_data['Orçado'].map('R$ {:,.0f}'.format),
            textposition='outside'
        ))
        fig.update_layout(
            title=f'{company}: Real vs Orçado',
            xaxis_title='Ano/Mês',
            yaxis_title='Valor',
            barmode='group',  # barras lado a lado
            xaxis_tickangle=-45,
            plot_bgcolor='white'
        )

        st.plotly_chart(fig)

        # Gráfico com Total Real e Orçado
        st.subheader(f'Total Real vs Orçado - {company}')
        total_data = company_data[['Real', 'Orçado']].sum().reset_index()
        total_data.columns = ['Tipo', 'Valor']
        fig_total = go.Figure()
        fig_total.add_trace(go.Bar(
            x=total_data['Tipo'],
            y=total_data['Valor'],
            marker_color=['#FF3F03', 'black'],
            text=total_data['Valor'].map('R$ {:,.0f}'.format),
            textposition='outside'
        ))
        fig_total.update_layout(
            title=f'{company}: Total Real vs Orçado',
            xaxis_title='Tipo',
            yaxis_title='Valor',
            xaxis_tickangle=-45,
            plot_bgcolor='white'
        )

        st.plotly_chart(fig_total)

    # Gráfico consolidado
    df_cumulative = df_receita_filtered.copy()
    st.subheader('Gráfico Consolidado Real vs Orçado')
    consolidated_data = df_cumulative.groupby('Mes').sum(numeric_only=True).reset_index()
    fig_consolidated = go.Figure()
    fig_consolidated.add_trace(go.Bar(
        x=consolidated_data['Mes'],
        y=consolidated_data['Real'],
        name='Real',
        marker_color='#FF3F03',
        text=consolidated_data['Real'].map('R$ {:,.0f}'.format),
        textposition='outside'
    ))
    fig_consolidated.add_trace(go.Bar(
        x=consolidated_data['Mes'],
        y=consolidated_data['Orçado'],
        name='Orçado',
        marker_color='black',
        text=consolidated_data['Orçado'].map('R$ {:,.0f}'.format),
        textposition='outside'
    ))
    fig_consolidated.update_layout(
        title='Consolidado: Real vs Orçado',
        xaxis_title='Ano/Mês',
        yaxis_title='Valor',
        barmode='group',
        xaxis_tickangle=-45,
        plot_bgcolor='white'
    )

    st.plotly_chart(fig_consolidated)

    # Gráfico consolidado apenas com Totais Real e Orçado
    st.subheader('Gráfico Consolidado: Total Real vs Total Orçado')
    total_real = df_cumulative['Real'].sum()
    total_orcado = df_cumulative['Orçado'].sum()
    totals_data = pd.DataFrame({
        'Tipo': ['Real', 'Orçado'],
        'Valor': [total_real, total_orcado]
    })
    fig_total_consolidated = go.Figure()
    fig_total_consolidated.add_trace(go.Bar(
        x=totals_data['Tipo'],
        y=totals_data['Valor'],
        marker_color=['#FF3F03', 'black'],
        text=totals_data['Valor'].map('R$ {:,.0f}'.format),
        textposition='outside'
    ))
    fig_total_consolidated.update_layout(
        title='Consolidado: Total Real vs Total Orçado',
        xaxis_title='Tipo',
        yaxis_title='Valor',
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_total_consolidated)

    # Tabela Comparativa Ano contra Ano
    st.subheader('Comparativo Real vs Orçado')
    yearly_comparison = df_receita_filtered.groupby(['Ano', 'Mes']).sum(numeric_only=True).reset_index()
    yearly_comparison['Variação %'] = (
        (yearly_comparison['Real'] - yearly_comparison['Orçado']) / yearly_comparison['Orçado'] * 100
    ).fillna(0)
    yearly_comparison['Variação R$'] = (
        (yearly_comparison['Real'] - yearly_comparison['Orçado'])
    ).fillna(0)
    totals = yearly_comparison[['Real', 'Orçado']].sum().rename('Total')
    totals['Variação %'] = (
        (totals['Real'] - totals['Orçado']) / totals['Orçado'] * 100
    )
    totals['Variação R$'] = (
        (totals['Real'] - totals['Orçado'])
    )
    totals_df = pd.DataFrame(totals).T
    yearly_comparison = pd.concat([yearly_comparison, totals_df], ignore_index=True)
    st.dataframe(yearly_comparison[['Mes', 'Real', 'Orçado', 'Variação %', 'Variação R$']].style.format(
        {"Real": "R$ {:,.0f}", "Orçado": "R$ {:,.0f}", "Variação %": "{:.2f}%","Variação R$": "R$ {:,.0f}"}
    ).hide(axis='index'))

# Página de Faturamento por Cliente
elif page == "Faturamento por Cliente":
    # Aplicando filtros
    if selected_company != 'Todas':
        df_faturamento = df_faturamento[df_faturamento['Empresa'] == selected_company]

    if selected_clients:
        df_faturamento = df_faturamento[df_faturamento['Cliente'].isin(selected_clients)]

    if selected_class:
        df_faturamento = df_faturamento[df_faturamento['Classe Cliente'].isin(selected_class)]

    df_faturamento_filtered = df_faturamento[(df_faturamento['Data'] >= pd.to_datetime(min_date)) & (df_faturamento['Data'] <= pd.to_datetime(max_date))]

    # Tabela de Faturamento por Cliente Ano contra Ano
    st.subheader('Faturamento por Cliente')
    faturamento_comparison = df_faturamento_filtered.groupby(['Mes', 'Cliente', 'Empresa', 'Classe Cliente']).sum(numeric_only=True).reset_index()
    faturamento_comparison = faturamento_comparison[['Mes', 'Cliente', 'Empresa', 'Classe Cliente', 'Valor']]
    
    # Adicionar linha com totais
    totals = faturamento_comparison[['Valor']].sum().rename('Total')
    totals_df = pd.DataFrame(totals).T
    faturamento_comparison = pd.concat([faturamento_comparison, totals_df], ignore_index=True)
    
    st.dataframe(faturamento_comparison.style.format({"Valor": "R$ {:,.0f}"}).hide(axis='index'))

    # Gráfico de faturamento por Classe de Cliente
    st.subheader('Faturamento por Classe de Cliente')
    class_summary = df_faturamento_filtered.groupby('Classe Cliente').agg({'Valor': 'sum'}).reset_index()
    class_summary['Percentual'] = (class_summary['Valor'] / class_summary['Valor'].sum() * 100).round(2)

    fig_class_summary = go.Figure()
    fig_class_summary.add_trace(go.Bar(
        x=class_summary['Classe Cliente'],
        y=class_summary['Valor'],
        name='Valor',
        marker_color='#FF3F03',
        text=class_summary['Valor'].map('R$ {:,.0f}'.format),
        textposition='outside'
    ))
    fig_class_summary.add_trace(go.Bar(
        x=class_summary['Classe Cliente'],
        y=class_summary['Percentual'],
        name='Percentual',
        marker_color='black',
        text=class_summary['Percentual'].map('{:.2f}%'.format),
        textposition='outside'
    ))
    fig_class_summary.update_layout(
        title='Faturamento por Classe de Cliente',
        xaxis_title='Classe de Cliente',
        yaxis_title='Valor / Percentual',
        barmode='group',
        xaxis_tickangle=-45,
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_class_summary)

    # Tabela Top 10 Clientes por Valor
    st.subheader('Top 10 Clientes por Valor')
    top_clients = df_faturamento_filtered.groupby(['Cliente']).agg({'Valor': 'sum'}).reset_index()
    top_clients = top_clients.sort_values(by='Valor', ascending=False).head(10)
    top_clients['Ranking'] = range(1, len(top_clients) + 1)
    
    # Adicionar linha com totais
    top_clients_total = top_clients[['Valor']].sum().rename('Total')
    top_clients_total_df = pd.DataFrame(top_clients_total).T
    top_clients = pd.concat([top_clients, top_clients_total_df], ignore_index=True)

    st.dataframe(top_clients.style.format({"Valor": "R$ {:,.0f}"}).hide(axis='index'))
