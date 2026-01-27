import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple
import streamlit as st

def calcular_dias_uteis(ano: int) -> int:
    """Calcula dias úteis no ano (simplificado)"""
    try:
        dias_uteis = 252  # padrão aproximado
        if ano == 2026:
            dias_uteis = 252
        elif ano == 2027:
            dias_uteis = 252
        return dias_uteis
    except:
        return 252

def calcular_valor_projetado_auc_2026_local(auc_initial: float, meta_2026: float, data_ref: datetime) -> float:
    """
    Calcula o valor projetado para o card AUC - 2026 (versão local)
    """
    try:
        # Calcular dias úteis
        dias_uteis_2026 = calcular_dias_uteis(2026)
        dias_uteis_2027 = calcular_dias_uteis(2027)
        dias_uteis_total = dias_uteis_2026 + dias_uteis_2027
        
        # Calcular crescimento diário necessário
        OBJETIVO_FINAL_RUMO = 1_000_000_000.0
        crescimento_diario = (OBJETIVO_FINAL_RUMO - auc_initial) / dias_uteis_total if dias_uteis_total > 0 else 0
        
        # Calcular dias decorridos desde início do ano
        inicio_ano = datetime(data_ref.year, 1, 1)
        dias_decorridos = (data_ref - inicio_ano).days + 1
        
        # Calcular valor projetado
        valor_projetado = auc_initial + (crescimento_diario * dias_decorridos)
        
        return max(0.0, min(valor_projetado, OBJETIVO_FINAL_RUMO))
    except Exception:
        return 0.0

def calcular_valor_projetado_rumo_1bi_local(auc_initial: float, data_ref: datetime) -> float:
    """
    Calcula o valor projetado para o card Rumo a 1bi (versão local)
    """
    try:
        # Calcular dias úteis
        dias_uteis_2026 = calcular_dias_uteis(2026)
        dias_uteis_2027 = calcular_dias_uteis(2027)
        dias_total = dias_uteis_2026 + dias_uteis_2027
        
        # Calcular crescimento diário necessário
        OBJETIVO_FINAL_RUMO = 1_000_000_000.0
        crescimento_diario = (OBJETIVO_FINAL_RUMO - auc_initial) / dias_total if dias_total > 0 else 0
        
        # Calcular dias decorridos desde início de 2026
        inicio_2026 = datetime(2026, 1, 1)
        dias_decorridos = (data_ref - inicio_2026).days + 1
        
        # Calcular valor projetado
        valor_projetado = auc_initial + (crescimento_diario * dias_decorridos)
        
        return max(0.0, min(valor_projetado, OBJETIVO_FINAL_RUMO))
    except Exception:
        return 0.0

@st.cache_data(show_spinner=False)
def carregar_dados_objetivos_pj1_robusto() -> Optional[pd.DataFrame]:
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
            st.warning("DataFrame vazio após limpeza de datas inválidas")
            return None
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao carregar dados da Objetivos_PJ1: {str(e)}")
        return None

@st.cache_data(show_spinner=False)
def obter_dados_captacao_mes_robusto(df_objetivos: pd.DataFrame, data_ref: datetime) -> Tuple[float, float]:
    """
    Obtém dados de captação do mês específico usando a tabela Objetivos_PJ1
    
    Args:
        df_objetivos: DataFrame com dados objetivos (não usado, mantido para compatibilidade)
        data_ref: Data de referência (data de atualização do dashboard)
        
    Returns:
        Tuple com (objetivo_total_mes, projetado_mes)
    """
    try:
        # Conectar ao banco de dados Objetivos
        conn = sqlite3.connect('DBV Capital_Objetivos.db')
        
        # Converter data_ref para string no formato dd/mm/YYYY
        data_ref_str = data_ref.strftime('%d/%m/%Y')
        
        # Buscar o valor de Cap Acumulado para a data específica
        query = """
        SELECT "Cap Acumulado" as cap_acumulado 
        FROM Objetivos_PJ1 
        WHERE Data = ?
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (data_ref_str,))
        resultado = cursor.fetchone()
        
        conn.close()
        
        if resultado and resultado[0] is not None:
            projetado_mes = float(resultado[0])
            # Para o objetivo do mês, podemos usar o valor do dia ou uma meta mensal
            objetivo_total_mes = projetado_mes  # Usar o mesmo valor como objetivo
        else:
            # Se não encontrar data exata, buscar o valor mais próximo
            conn = sqlite3.connect('DBV Capital_Objetivos.db')
            query = """
            SELECT "Cap Acumulado" as cap_acumulado 
            FROM Objetivos_PJ1 
            WHERE Data <= ? 
            ORDER BY Data DESC 
            LIMIT 1
            """
            cursor = conn.cursor()
            cursor.execute(query, (data_ref_str,))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0] is not None:
                projetado_mes = float(resultado[0])
                objetivo_total_mes = projetado_mes
            else:
                projetado_mes = 0.0
                objetivo_total_mes = 0.0
        
        return objetivo_total_mes, projetado_mes
        
    except Exception as e:
        st.error(f"Erro ao obter dados de captação do mês: {str(e)}")
        return 0.0, 0.0

@st.cache_data(show_spinner=False)
def obter_dados_captacao_ano_robusto(df_objetivos: pd.DataFrame, data_ref: datetime) -> Tuple[float, float]:
    """
    Obtém dados de captação do ano específico usando a tabela Objetivos_PJ1
    
    Args:
        df_objetivos: DataFrame com dados objetivos (não usado, mantido para compatibilidade)
        data_ref: Data de referência (data de atualização do dashboard)
        
    Returns:
        Tuple com (objetivo_total, projetado_acumulado)
    """
    try:
        # Conectar ao banco de dados Objetivos
        conn = sqlite3.connect('DBV Capital_Objetivos.db')
        
        # Converter data_ref para string no formato dd/mm/YYYY
        data_ref_str = data_ref.strftime('%d/%m/%Y')
        
        # Buscar o valor de Cap Acumulado para a data específica (acumulado anual)
        query = """
        SELECT "Cap Acumulado" as cap_acumulado,
               "Cap Objetivo (ano)" as cap_objetivo_ano
        FROM Objetivos_PJ1 
        WHERE Data = ?
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (data_ref_str,))
        resultado = cursor.fetchone()
        
        conn.close()
        
        if resultado and resultado[0] is not None:
            projetado_acumulado = float(resultado[0])
            objetivo_total = float(resultado[1]) if resultado[1] is not None else projetado_acumulado
        else:
            # Se não encontrar data exata, buscar o valor mais próximo
            conn = sqlite3.connect('DBV Capital_Objetivos.db')
            query = """
            SELECT "Cap Acumulado" as cap_acumulado,
                   "Cap Objetivo (ano)" as cap_objetivo_ano
            FROM Objetivos_PJ1 
            WHERE Data <= ? 
            ORDER BY Data DESC 
            LIMIT 1
            """
            cursor = conn.cursor()
            cursor.execute(query, (data_ref_str,))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0] is not None:
                projetado_acumulado = float(resultado[0])
                objetivo_total = float(resultado[1]) if resultado[1] is not None else projetado_acumulado
            else:
                projetado_acumulado = 0.0
                objetivo_total = 0.0
        
        return objetivo_total, projetado_acumulado
        
    except Exception as e:
        st.error(f"Erro ao obter dados de captação do ano: {str(e)}")
        return 0.0, 0.0

@st.cache_data(show_spinner=False)
def obter_dados_captacao_acumulado_robusto(data_ref: datetime) -> Optional[pd.DataFrame]:
    """
    Obtém dados de captação acumulados até a data de referência
    
    Args:
        data_ref: Data de referência
        
    Returns:
        DataFrame com dados de captação acumulados ou None
    """
    try:
        # Carregar dados objetivos
        df_objetivos = carregar_dados_objetivos_pj1_robusto()
        if df_objetivos is None:
            return None
        
        # Filtrar até a data de referência
        df_acumulado = df_objetivos[df_objetivos['Data'] <= data_ref]
        
        return df_acumulado
        
    except Exception as e:
        st.error(f"Erro ao obter dados de captação acumulados: {str(e)}")
        return None

def calcular_captacao_periodo(df: pd.DataFrame, coluna_valor: str = 'Valor') -> float:
    """
    Calcula a captação total em um período
    
    Args:
        df: DataFrame com dados
        coluna_valor: Nome da coluna de valores
        
    Returns:
        Valor total de captação
    """
    try:
        if df is None or df.empty:
            return 0.0
        
        if coluna_valor not in df.columns:
            st.warning(f"Coluna '{coluna_valor}' não encontrada. Colunas: {list(df.columns)}")
            return 0.0
        
        # Converter para numérico
        df[coluna_valor] = pd.to_numeric(df[coluna_valor], errors='coerce').fillna(0)
        
        return float(df[coluna_valor].sum())
        
    except Exception as e:
        st.error(f"Erro ao calcular captação: {str(e)}")
        return 0.0

def formatar_valor_monetario(valor: float) -> str:
    """
    Formata valor monetário para exibição
    
    Args:
        valor: Valor numérico
        
    Returns:
        String formatada
    """
    try:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return "R$ 0,00"

@st.cache_data(show_spinner=False)
def obter_dados_auc_2026_robusto(df_objetivos: pd.DataFrame, data_ref: datetime = None) -> Tuple[float, float]:
    """
    Obtém dados do AUC 2026 usando a tabela Objetivos_PJ1
    
    Args:
        df_objetivos: DataFrame com dados objetivos (não usado, mantido para compatibilidade)
        data_ref: Data de referência (data de atualização do dashboard)
        
    Returns:
        Tuple com (objetivo_total, projetado_acumulado)
    """
    try:
        # Conectar ao banco de dados Objetivos
        conn = sqlite3.connect('DBV Capital_Objetivos.db')
        
        # Converter data_ref para string no formato dd/mm/YYYY
        data_ref_str = data_ref.strftime('%d/%m/%Y')
        
        # Buscar o valor de AUC Acumulado para a data específica
        query = """
        SELECT "AUC Acumulado" as auc_acumulado,
               "AUC Objetivo (Ano)" as auc_objetivo_ano
        FROM Objetivos_PJ1 
        WHERE Data = ?
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (data_ref_str,))
        resultado = cursor.fetchone()
        
        conn.close()
        
        if resultado and resultado[0] is not None:
            projetado_acumulado = float(resultado[0])
            objetivo_total = float(resultado[1]) if resultado[1] is not None else projetado_acumulado
        else:
            # Se não encontrar data exata, buscar o valor mais próximo
            conn = sqlite3.connect('DBV Capital_Objetivos.db')
            query = """
            SELECT "AUC Acumulado" as auc_acumulado,
                   "AUC Objetivo (Ano)" as auc_objetivo_ano
            FROM Objetivos_PJ1 
            WHERE Data <= ? 
            ORDER BY Data DESC 
            LIMIT 1
            """
            cursor = conn.cursor()
            cursor.execute(query, (data_ref_str,))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0] is not None:
                projetado_acumulado = float(resultado[0])
                objetivo_total = float(resultado[1]) if resultado[1] is not None else projetado_acumulado
            else:
                projetado_acumulado = 0.0
                objetivo_total = 0.0
        
        return objetivo_total, projetado_acumulado
        
    except Exception as e:
        st.error(f"Erro ao obter dados AUC 2026: {str(e)}")
        return 0.0, 0.0

@st.cache_data(show_spinner=False)
def obter_dados_rumo_1bi_robusto(df_objetivos: pd.DataFrame, data_ref: datetime = None) -> Tuple[float, float]:
    """
    Obtém dados do Rumo a 1bi usando a tabela Objetivos_PJ1
    
    Args:
        df_objetivos: DataFrame com dados objetivos (não usado, mantido para compatibilidade)
        data_ref: Data de referência (data de atualização do dashboard)
        
    Returns:
        Tuple com (objetivo_total, projetado_acumulado)
    """
    try:
        # Conectar ao banco de dados Objetivos
        conn = sqlite3.connect('DBV Capital_Objetivos.db')
        
        # Converter data_ref para string no formato dd/mm/YYYY
        data_ref_str = data_ref.strftime('%d/%m/%Y')
        
        # Buscar o valor de AUC Acumulado para a data específica (mesma coluna do AUC-2026)
        query = """
        SELECT "AUC Acumulado" as auc_acumulado,
               "AUC Objetivo (Ano)" as auc_objetivo_ano
        FROM Objetivos_PJ1 
        WHERE Data = ?
        """
        
        cursor = conn.cursor()
        cursor.execute(query, (data_ref_str,))
        resultado = cursor.fetchone()
        
        conn.close()
        
        if resultado and resultado[0] is not None:
            projetado_acumulado = float(resultado[0])
            # Para Rumo a 1bi, o objetivo é 1 bilhão
            objetivo_total = 1_000_000_000.0
        else:
            # Se não encontrar data exata, buscar o valor mais próximo
            conn = sqlite3.connect('DBV Capital_Objetivos.db')
            query = """
            SELECT "AUC Acumulado" as auc_acumulado,
                   "AUC Objetivo (Ano)" as auc_objetivo_ano
            FROM Objetivos_PJ1 
            WHERE Data <= ? 
            ORDER BY Data DESC 
            LIMIT 1
            """
            cursor = conn.cursor()
            cursor.execute(query, (data_ref_str,))
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado and resultado[0] is not None:
                projetado_acumulado = float(resultado[0])
                objetivo_total = 1_000_000_000.0
            else:
                projetado_acumulado = 0.0
                objetivo_total = 0.0
        
        return objetivo_total, projetado_acumulado
        
    except Exception as e:
        st.error(f"Erro ao obter dados Rumo a 1bi: {str(e)}")
        return 0.0, 0.0
