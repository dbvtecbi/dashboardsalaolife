"""
Utilitários para acesso ao banco de dados do dashboard.
"""
import sqlite3
from pathlib import Path
import pandas as pd

# Mapeamento de nomes de colunas
def get_column_mapping():
    """Retorna um dicionário com o mapeamento de nomes de colunas."""
    return {
        # Tabelas
        'capital_positivador': 'Relatório Positivador',
        'objetivos_pj1': 'objetivos',
        
        # Colunas
        'Data_Posicao': 'Data_Posição',
        'Captacao_Liquida_em_M': 'Captação_Líquida_em_M',
        'Net_em_M': 'Net_Em_M',
        'Data_Atualizacao': 'Data_Atualização',
        'Tipo_Pessoa': 'Tipo_Pessoa',
        'Assessor': 'Assessor',
        'Cliente': 'Cliente'
    }

def get_db_path(db_name):
    """Retorna o caminho completo para o arquivo do banco de dados."""
    # Tenta encontrar o arquivo em vários locais possíveis
    possible_paths = [
        Path(__file__).parent / db_name,
        Path(__file__).parent.parent / db_name,
        Path(db_name)
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError(f"Não foi possível encontrar o arquivo do banco de dados: {db_name}")

def get_connection(db_name):
    """Retorna uma conexão com o banco de dados."""
    db_path = get_db_path(db_name)
    return sqlite3.connect(db_path)

def load_positivador_data():
    """Carrega os dados do Positivador."""
    mapping = get_column_mapping()
    table_name = mapping.get('capital_positivador', 'Relatório Positivador')
    
    # Mapeamento reverso para renomear as colunas
    reverse_mapping = {v: k for k, v in mapping.items() if k not in ['capital_positivador', 'objetivos_pj1']}
    
    try:
        conn = get_connection("DBV Capital_Positivador (MTD).db")
        df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
        
        # Renomear colunas para os nomes esperados pelo código
        df = df.rename(columns=reverse_mapping)
        
        # Converter datas
        if 'Data_Posicao' in df.columns:
            df['Data_Posicao'] = pd.to_datetime(df['Data_Posicao'], dayfirst=True, errors='coerce')
        
        return df
    
    except Exception as e:
        print(f"Erro ao carregar dados do Positivador: {e}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

def load_objetivos_data():
    """Carrega os dados de objetivos."""
    mapping = get_column_mapping()
    table_name = mapping.get('objetivos_pj1', 'objetivos')
    
    try:
        conn = get_connection("DBV Capital_Objetivos.db")
        return pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    
    except Exception as e:
        print(f"Erro ao carregar dados de objetivos: {e}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

def get_objetivo_anual(ano, coluna):
    """Obtém o valor do objetivo para um determinado ano e coluna."""
    try:
        df = load_objetivos_data()
        if df.empty:
            return 0.0
            
        # Encontrar o objetivo para o ano especificado
        objetivo = df[df['Objetivo'] == ano][coluna].values
        
        if len(objetivo) > 0:
            return float(objetivo[0])
        else:
            # Se não encontrar para o ano, retorna o valor mais próximo
            df = df[df['Objetivo'] >= ano].sort_values('Objetivo')
            if not df.empty:
                return float(df.iloc[0][coluna])
            
            # Se ainda não encontrar, retorna o último valor disponível
            df = df.sort_values('Objetivo', ascending=False)
            if not df.empty:
                return float(df.iloc[0][coluna])
            
            return 0.0
            
    except Exception as e:
        print(f"Erro ao obter objetivo {coluna} para o ano {ano}: {e}")
        return 0.0
