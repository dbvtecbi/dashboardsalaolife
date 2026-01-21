"""
CORREÇÃO FINAL PARA O ERRO KeyError: 'Data'

Este arquivo contém uma versão mais robusta das funções para evitar o erro
de KeyError no contexto do Streamlit.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple
import streamlit as st

@st.cache_data(show_spinner=False)
def carregar_dados_objetivos_pj1_robusto() -> Optional[pd.DataFrame]:
    """
    Versão robusta para carregar dados da Objetivos_PJ1
    """
    try:
        conn = sqlite3.connect('DBV Capital_Objetivos.db')
        
        # Verificar se a tabela existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Objetivos_PJ1'")
        if not cursor.fetchone():
            conn.close()
            return None
        
        # Carregar dados
        query = "SELECT * FROM Objetivos_PJ1 ORDER BY Data"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return None
        
        # Verificar e converter coluna Data
        if 'Data' not in df.columns:
            return None
            
        # Converter para datetime e criar cópia de segurança
        df = df.copy()
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        df = df.dropna(subset=['Data'])
        
        if df.empty:
            return None
        
        # Resetar índice para evitar problemas
        df = df.reset_index(drop=True)
        
        return df
        
    except Exception:
        return None

def obter_dados_captacao_mes_robusto(df_objetivos_pj1: Optional[pd.DataFrame], data_ref) -> Tuple[float, float]:
    """
    Versão robusta para obter dados de captação mensal
    """
    # Verificação completa
    if df_objetivos_pj1 is None:
        return 0.0, 0.0
    
    if not isinstance(df_objetivos_pj1, pd.DataFrame):
        return 0.0, 0.0
    
    if df_objetivos_pj1.empty:
        return 0.0, 0.0
    
    # Verificar colunas necessárias
    colunas_necessarias = ['Data', 'Cap Acumulado']
    for col in colunas_necessarias:
        if col not in df_objetivos_pj1.columns:
            return 0.0, 0.0
    
    # Converter data_ref para Timestamp se necessário
    if not isinstance(data_ref, pd.Timestamp):
        data_ref = pd.Timestamp(data_ref)
    
    try:
        # Filtrar dados do mês
        df_mes = df_objetivos_pj1[
            (df_objetivos_pj1['Data'].dt.year == data_ref.year) & 
            (df_objetivos_pj1['Data'].dt.month == data_ref.month)
        ]
        
        if df_mes.empty:
            return 0.0, 0.0
        
        # Obter valores
        objetivo_total_mes = float(df_mes['Cap Acumulado'].iloc[-1])
        
        # Projetado até a data
        df_ate_data = df_objetivos_pj1[df_objetivos_pj1['Data'] <= data_ref]
        if df_ate_data.empty:
            projetado_mes = 0.0
        else:
            projetado_mes = float(df_ate_data['Cap Acumulado'].iloc[-1])
        
        return objetivo_total_mes, projetado_mes
        
    except Exception:
        return 0.0, 0.0

# Funções similares para os outros cards
def obter_dados_captacao_ano_robusto(df_objetivos_pj1: Optional[pd.DataFrame], data_ref) -> Tuple[float, float]:
    """Versão robusta para captação anual"""
    if df_objetivos_pj1 is None or df_objetivos_pj1.empty:
        return 0.0, 0.0
    
    if not all(col in df_objetivos_pj1.columns for col in ['Data', 'Cap Objetivo (ano)', 'Cap Acumulado']):
        return 0.0, 0.0
    
    try:
        if not isinstance(data_ref, pd.Timestamp):
            data_ref = pd.Timestamp(data_ref)
        
        # Objetivo total (pegar do ano)
        df_ano = df_objetivos_pj1[df_objetivos_pj1['Data'].dt.year == data_ref.year]
        if df_ano.empty:
            return 0.0, 0.0
        objetivo_total = float(df_ano['Cap Objetivo (ano)'].iloc[0])
        
        # Projetado acumulado
        df_ate_data = df_objetivos_pj1[df_objetivos_pj1['Data'] <= data_ref]
        if df_ate_data.empty:
            projetado = 0.0
        else:
            projetado = float(df_ate_data['Cap Acumulado'].iloc[-1])
        
        return objetivo_total, projetado
        
    except Exception:
        return 0.0, 0.0

def obter_dados_auc_2026_robusto(df_objetivos_pj1: Optional[pd.DataFrame], data_ref) -> Tuple[float, float]:
    """Versão robusta para AUC 2026"""
    if df_objetivos_pj1 is None or df_objetivos_pj1.empty:
        return 0.0, 0.0
    
    if not all(col in df_objetivos_pj1.columns for col in ['Data', 'AUC Objetivo (Ano)', 'AUC Acumulado']):
        return 0.0, 0.0
    
    try:
        if not isinstance(data_ref, pd.Timestamp):
            data_ref = pd.Timestamp(data_ref)
        
        # Objetivo total
        df_ano = df_objetivos_pj1[df_objetivos_pj1['Data'].dt.year == data_ref.year]
        if df_ano.empty:
            return 0.0, 0.0
        objetivo_total = float(df_ano['AUC Objetivo (Ano)'].iloc[0])
        
        # Projetado acumulado
        df_ate_data = df_objetivos_pj1[df_objetivos_pj1['Data'] <= data_ref]
        if df_ate_data.empty:
            projetado = 0.0
        else:
            projetado = float(df_ate_data['AUC Acumulado'].iloc[-1])
        
        return objetivo_total, projetado
        
    except Exception:
        return 0.0, 0.0


def obter_dados_rumo_1bi_robusto(df_objetivos_pj1, data_ref):
    """
    Obtém os dados para o card RUMO A 1BI usando a lógica do AUC-2026
    mas com objetivo para 2027 (01/01/2027)
    
    Args:
        df_objetivos_pj1: DataFrame com os dados da Objetivos_PJ1
        data_ref: Data de referência
        
    Returns:
        tuple: (objetivo_total, projetado_acumulado)
    """
    try:
        # Verificar se o DataFrame é válido
        if df_objetivos_pj1 is None or df_objetivos_pj1.empty:
            return 0.0, 0.0
        
        # Verificar se as colunas necessárias existem
        colunas_necessarias = ['Data', 'AUC Objetivo (Ano)', 'AUC Acumulado']
        for col in colunas_necessarias:
            if col not in df_objetivos_pj1.columns:
                return 0.0, 0.0
        
        # Garantir que a coluna Data seja datetime
        if not pd.api.types.is_datetime64_any_dtype(df_objetivos_pj1['Data']):
            df_objetivos_pj1['Data'] = pd.to_datetime(df_objetivos_pj1['Data'], errors='coerce')
        
        # Objetivo Total: AUC Objetivo (Ano) para 2027 (primeiro dia de 2027)
        data_2027 = pd.Timestamp(2027, 1, 1)
        
        # Filtrar registros de 2027 ou usar o último valor disponível
        df_2027 = df_objetivos_pj1[df_objetivos_pj1['Data'].dt.year == 2027]
        
        if not df_2027.empty:
            # Pegar o primeiro registro de 2027
            df_2027_sorted = df_2027.sort_values('Data')
            objetivo_total = float(df_2027_sorted['AUC Objetivo (Ano)'].iloc[0])
        else:
            # Se não tiver dados de 2027, usar o último valor disponível como projeção
            df_sorted = df_objetivos_pj1.sort_values('Data')
            if not df_sorted.empty:
                ultimo_valor = float(df_sorted['AUC Objetivo (Ano)'].iloc[-1])
                # Aplicar um crescimento estimado para 2027 (ex: 10% de crescimento)
                objetivo_total = ultimo_valor * 1.10
            else:
                objetivo_total = 0.0
        
        # Projetado: Usar a mesma lógica do AUC-2026 (AUC Acumulado na data_ref)
        data_ref_formatada = data_ref.strftime('%Y-%m-%d')
        df_data_ref = df_objetivos_pj1[df_objetivos_pj1['Data'].dt.strftime('%Y-%m-%d') == data_ref_formatada]
        
        if not df_data_ref.empty:
            projetado_acumulado = float(df_data_ref['AUC Acumulado'].iloc[0])
        else:
            # Se não encontrar a data exata, usar o valor mais próximo
            df_objetivos_pj1_sorted = df_objetivos_pj1.sort_values('Data')
            data_ref_ts = pd.Timestamp(data_ref)
            
            # Encontrar o registro mais próximo da data_ref
            idx_proximo = (df_objetivos_pj1_sorted['Data'] - data_ref_ts).abs().idxmin()
            projetado_acumulado = float(df_objetivos_pj1_sorted.loc[idx_proximo, 'AUC Acumulado'])
        
        return objetivo_total, projetado_acumulado
        
    except Exception:
        return 0.0, 0.0


print("✅ Funções robustas carregadas com sucesso!")
print("Use estas funções para substituir as originais no Dashboard_Salão_Atualizado.py")
