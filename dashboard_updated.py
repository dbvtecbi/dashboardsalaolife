"""
Dashboard Atualizado - DBV Capital

Este script carrega e exibe os dados do Positivador e Objetivos de forma correta.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import database_utils as db

# Configuração da página
st.set_page_config(
    page_title="DBV Capital - Dashboard Atualizado",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título do dashboard
st.title("DBV Capital - Dashboard Atualizado")
st.markdown("---")

# Carregar dados
with st.spinner('Carregando dados...'):
    df_pos = db.load_positivador_data()
    df_obj = db.load_objetivos_data()

# Exibir dados brutos para depuração
with st.expander("🔍 Dados Brutos (Depuração)", expanded=False):
    st.write("### Dados do Positivador")
    st.dataframe(df_pos.head())
    
    st.write("### Dados de Objetivos")
    st.dataframe(df_obj)

# Função para calcular métricas
def calcular_metricas(df):
    """Calcula as métricas principais do dashboard."""
    metricas = {}
    
    if df.empty:
        return metricas
    
    try:
        # Captação Líquida do Mês
        if 'Captacao_Liquida_em_M' in df.columns:
            metricas['captacao_liquida_mes'] = df['Captacao_Liquida_em_M'].sum()
        
        # Net Em M
        if 'Net_Em_M' in df.columns:
            metricas['net_em_m'] = df['Net_Em_M'].sum()
        
        # Contagem de clientes
        if 'Cliente' in df.columns:
            metricas['total_clientes'] = df['Cliente'].nunique()
        
        # Contagem de assessores
        if 'Assessor' in df.columns:
            metricas['total_assessores'] = df['Assessor'].nunique()
        
        # Captação por segmento
        if 'Segmento' in df.columns and 'Captacao_Liquida_em_M' in df.columns:
            captacao_por_segmento = df.groupby('Segmento')['Captacao_Liquida_em_M'].sum().reset_index()
            metricas['captacao_por_segmento'] = captacao_por_segmento
        
        # Net por segmento
        if 'Segmento' in df.columns and 'Net_Em_M' in df.columns:
            net_por_segmento = df.groupby('Segmento')['Net_Em_M'].sum().reset_index()
            metricas['net_por_segmento'] = net_por_segmento
            
    except Exception as e:
        st.error(f"Erro ao calcular métricas: {e}")
    
    return metricas

# Calcular métricas
metricas = calcular_metricas(df_pos)

# Exibir métricas principais
st.header("Visão Geral")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Captação Líquida do Mês (R$)", 
              f"{metricas.get('captacao_liquida_mes', 0):,.2f} M" if 'captacao_liquida_mes' in metricas else "N/A")

with col2:
    st.metric("Patrimônio Líquido (R$)", 
              f"{metricas.get('net_em_m', 0):,.2f} M" if 'net_em_m' in metricas else "N/A")

with col3:
    st.metric("Total de Clientes", 
              f"{metricas.get('total_clientes', 0):,}" if 'total_clientes' in metricas else "N/A")

with col4:
    st.metric("Total de Assessores", 
              f"{metricas.get('total_assessores', 0):,}" if 'total_assessores' in metricas else "N/A")

# Gráficos de segmentação
if 'captacao_por_segmento' in metricas and not metricas['captacao_por_segmento'].empty:
    st.subheader("Captação por Segmento")
    fig = px.pie(
        metricas['captacao_por_segmento'], 
        values='Captacao_Liquida_em_M', 
        names='Segmento',
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

if 'net_por_segmento' in metricas and not metricas['net_por_segmento'].empty:
    st.subheader("Patrimônio Líquido por Segmento")
    fig = px.bar(
        metricas['net_por_segmento'], 
        x='Segmento', 
        y='Net_Em_M',
        labels={'Net_Em_M': 'Patrimônio Líquido (R$)', 'Segmento': 'Segmento'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Rodapé
st.markdown("---")
st.caption("Atualizado em: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
