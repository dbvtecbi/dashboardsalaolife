import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple
import streamlit as st

@st.cache_data(show_spinner=False)
def carregar_dados_objetivos_pj1() -> Optional[pd.DataFrame]:
    """
    Carrega os dados da tabela Objetivos_PJ1 do banco de dados DBV Capital_Objetivos.db
    
    Returns:
        DataFrame com os dados ou None se houver erro
    """
    try:
        conn = sqlite3.connect('DBV Capital_Objetivos.db')
        
        # Verificar se a tabela existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Objetivos_PJ1'")
        if not cursor.fetchone():
            st.error("Tabela Objetivos_PJ1 não encontrada no banco de dados")
            conn.close()
            return None
        
        # Carregar dados
        query = "SELECT * FROM Objetivos_PJ1 ORDER BY Data"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Verificar se o DataFrame está vazio
        if df.empty:
            st.warning("DataFrame vazio após carregar dados da Objetivos_PJ1")
            return None
        
        # Debug: mostrar colunas encontradas
        print(f"Colunas encontradas: {list(df.columns)}")
        
        # Verificar se a coluna 'Data' existe
        if 'Data' not in df.columns:
            st.error(f"Coluna 'Data' não encontrada. Colunas disponíveis: {list(df.columns)}")
            return None
        
        # Converter coluna Data para datetime
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        
        # Remover linhas com data inválida
        df = df.dropna(subset=['Data'])
        
        # Verificar se ainda há dados após limpeza
        if df.empty:
            st.warning("DataFrame vazio após remover datas inválidas")
            return None
        
        # Ordenar por data
        df = df.sort_values('Data').reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados da Objetivos_PJ1: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
        return None

def obter_valor_por_data(df: pd.DataFrame, data_ref: datetime, coluna_valor: str) -> float:
    """
    Obtém o valor de uma coluna para uma data específica ou a data mais próxima anterior
    
    Args:
        df: DataFrame com os dados
        data_ref: Data de referência
        coluna_valor: Nome da coluna para obter o valor
    
    Returns:
        Valor encontrado ou 0.0
    """
    if df is None or df.empty:
        return 0.0
    
    # Converter data_ref para datetime se for string
    if isinstance(data_ref, str):
        data_ref = pd.to_datetime(data_ref, format='%d/%m/%Y', errors='coerce')
    
    # Filtrar datas menores ou iguais à data de referência
    df_filtrado = df[df['Data'] <= data_ref]
    
    if df_filtrado.empty:
        return 0.0
    
    # Obter o valor da data mais recente
    valor = df_filtrado.iloc[-1][coluna_valor]
    
    return float(valor) if pd.notna(valor) else 0.0

def obter_ultimo_dia_mes(df: pd.DataFrame, data_ref: datetime, coluna_valor: str) -> float:
    """
    Obtém o valor do último dia do mês correspondente à data de referência
    
    Args:
        df: DataFrame com os dados
        data_ref: Data de referência
        coluna_valor: Nome da coluna para obter o valor
    
    Returns:
        Valor do último dia do mês ou 0.0
    """
    if df is None or df.empty:
        print("DataFrame é None ou vazio")
        return 0.0
    
    # Verificar se a coluna 'Data' existe
    if 'Data' not in df.columns:
        print(f"Coluna 'Data' não encontrada. Colunas: {list(df.columns)}")
        return 0.0
    
    # Converter data_ref para datetime se for string
    if isinstance(data_ref, str):
        data_ref = pd.to_datetime(data_ref, format='%d/%m/%Y', errors='coerce')
    
    # Verificar se a coluna de valor existe
    if coluna_valor not in df.columns:
        print(f"Coluna '{coluna_valor}' não encontrada. Colunas: {list(df.columns)}")
        return 0.0
    
    # Filtrar dados do mês específico
    try:
        df_mes = df[(df['Data'].dt.year == data_ref.year) & (df['Data'].dt.month == data_ref.month)]
    except Exception as e:
        print(f"Erro ao filtrar por mês: {e}")
        return 0.0
    
    if df_mes.empty:
        print(f"Nenhum dado encontrado para o mês {data_ref.month}/{data_ref.year}")
        return 0.0
    
    # Obter o valor do último dia disponível no mês
    valor = df_mes.iloc[-1][coluna_valor]
    
    return float(valor) if pd.notna(valor) else 0.0

def obter_objetivo_total_por_data(df: pd.DataFrame, data_ref: datetime, coluna_objetivo: str) -> float:
    """
    Obtém o objetivo total cruzando a coluna de objetivo com a data de referência
    
    Args:
        df: DataFrame com os dados
        data_ref: Data de referência (data de atualização do dashboard)
        coluna_objetivo: Nome da coluna de objetivo
    
    Returns:
        Valor do objetivo para a data de referência
    """
    if df is None or df.empty:
        return 0.0
    
    # Converter data_ref para datetime se for string
    if isinstance(data_ref, str):
        data_ref = pd.to_datetime(data_ref, format='%d/%m/%Y', errors='coerce')
    
    # Obter o ano da data de referência
    ano_ref = data_ref.year
    
    # Filtrar dados do ano específico
    df_ano = df[df['Data'].dt.year == ano_ref]
    
    if df_ano.empty:
        return 0.0
    
    # Obter o valor da coluna de objetivo (geralmente é constante para todo o ano)
    valor = df_ano.iloc[0][coluna_objetivo]
    
    return float(valor) if pd.notna(valor) else 0.0

# Funções específicas para cada card

def obter_dados_captacao_ano(df_objetivos_pj1: pd.DataFrame, data_ref: datetime) -> Tuple[float, float]:
    """
    Obtém os dados para o card CAPTAÇÃO LÍQUIDA ANO
    
    Returns:
        Tuple: (objetivo_total, projetado_acumulado)
    """
    objetivo_total = obter_objetivo_total_por_data(df_objetivos_pj1, data_ref, "Cap Objetivo (ano)")
    projetado_acumulado = obter_valor_por_data(df_objetivos_pj1, data_ref, "Cap Acumulado")
    
    return objetivo_total, projetado_acumulado

def obter_dados_auc_2026(df_objetivos_pj1: pd.DataFrame, data_ref: datetime) -> Tuple[float, float]:
    """
    Obtém os dados para o card AUC - 2026
    
    Returns:
        Tuple: (objetivo_total, projetado_acumulado)
    """
    objetivo_total = obter_objetivo_total_por_data(df_objetivos_pj1, data_ref, "AUC Objetivo (Ano)")
    projetado_acumulado = obter_valor_por_data(df_objetivos_pj1, data_ref, "AUC Acumulado")
    
    return objetivo_total, projetado_acumulado

def obter_dados_captacao_mes(df_objetivos_pj1: pd.DataFrame, data_ref: datetime) -> Tuple[float, float]:
    """
    Obtém os dados para o card CAPTAÇÃO LÍQUIDA MÊS
    
    Returns:
        Tuple: (objetivo_total_mes, projetado_mes)
    """
    # Verificações robustas
    if df_objetivos_pj1 is None:
        print("❌ df_objetivos_pj1 é None")
        return 0.0, 0.0
    
    if not isinstance(df_objetivos_pj1, pd.DataFrame):
        print(f"❌ df_objetivos_pj1 não é DataFrame: {type(df_objetivos_pj1)}")
        return 0.0, 0.0
    
    if df_objetivos_pj1.empty:
        print("❌ df_objetivos_pj1 está vazio")
        return 0.0, 0.0
    
    if 'Data' not in df_objetivos_pj1.columns:
        print(f"❌ Coluna 'Data' não encontrada. Colunas: {list(df_objetivos_pj1.columns)}")
        return 0.0, 0.0
    
    print(f"✅ DataFrame OK: {len(df_objetivos_pj1)} registros, colunas: {list(df_objetivos_pj1.columns)}")
    
    # Objetivo total do mês: pegar o valor do último dia do mês correspondente
    objetivo_total_mes = obter_ultimo_dia_mes(df_objetivos_pj1, data_ref, "Cap Acumulado")
    
    # Projetado do mês: valor acumulado até a data de referência
    projetado_mes = obter_valor_por_data(df_objetivos_pj1, data_ref, "Cap Acumulado")
    
    return objetivo_total_mes, projetado_mes

def obter_cap_diario_verificacao(df_objetivos_pj1: pd.DataFrame, data_ref: datetime) -> float:
    """
    Obtém o valor diário para verificação (prova real)
    
    Returns:
        Valor diário da captação
    """
    return obter_valor_por_data(df_objetivos_pj1, data_ref, "Cap Diário (ANO)")
