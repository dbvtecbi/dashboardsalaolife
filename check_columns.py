import sqlite3
import pandas as pd
from column_mapping import get_column_mapping, get_table_name

def check_columns():
    db_path = "DBV Capital_Positivador (MTD).db"
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        
        # Obter o nome real da tabela
        table_name = get_table_name('capital_positivador')
        
        # Verificar se a tabela existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        if not cursor.fetchone():
            print(f"Erro: A tabela '{table_name}' não foi encontrada no banco de dados.")
            return
        
        # Obter informações das colunas da tabela
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        columns = cursor.fetchall()
        
        print(f"\nColunas na tabela '{table_name}':")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Verificar se as colunas necessárias existem
        required_columns = [
            'Data_Posicao', 'Captacao_Liquida_em_M', 'Net_Em_M', 
            'Assessor', 'Cliente', 'Tipo_Pessoa'
        ]
        
        print("\nVerificando colunas necessárias:")
        available_columns = [col[1] for col in columns]
        missing_columns = []
        
        for col in required_columns:
            mapped_col = get_column_mapping(col)
            if mapped_col in available_columns:
                print(f"✅ {col} -> {mapped_col} (encontrada)")
            else:
                print(f"❌ {col} -> {mapped_col} (não encontrada)")
                missing_columns.append(col)
        
        # Carregar dados de exemplo
        print("\nCarregando dados de exemplo...")
        query = f'SELECT * FROM "{table_name}" LIMIT 5'
        df = pd.read_sql_query(query, conn)
        
        # Renomear colunas para os nomes esperados
        reverse_mapping = {v: k for k, v in get_column_mapping('all').items() if k != 'capital_positivador'}
        df_renamed = df.rename(columns=reverse_mapping)
        
        print("\nDados de exemplo (após renomeação de colunas):")
        print(df_renamed.head())
        
        # Verificar valores nulos
        print("\nValores nulos por coluna:")
        print(df_renamed.isnull().sum())
        
        # Verificar valores únicos em colunas importantes
        if 'Data_Posicao' in df_renamed.columns:
            print("\nDatas únicas na coluna Data_Posicao:")
            print(df_renamed['Data_Posicao'].unique())
        
        if 'Captacao_Liquida_em_M' in df_renamed.columns:
            print("\nEstatísticas para Captacao_Liquida_em_M:")
            print(df_renamed['Captacao_Liquida_em_M'].describe())
        
        if 'Net_Em_M' in df_renamed.columns:
            print("\nEstatísticas para Net_Em_M:")
            print(df_renamed['Net_Em_M'].describe())
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar colunas: {e}")
        import traceback
        traceback.print_exc()

def check_objetivos():
    """Verifica os dados da tabela de objetivos."""
    db_path = "DBV Capital_Objetivos.db"
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Verificar tabelas disponíveis
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        print("\nTabelas disponíveis no banco de objetivos:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Verificar colunas
            cursor.execute(f'PRAGMA table_info("{table[0]}")')
            columns = cursor.fetchall()
            print(f"  Colunas: {', '.join([col[1] for col in columns])}")
            
            # Mostrar dados de exemplo
            try:
                df = pd.read_sql_query(f'SELECT * FROM "{table[0]}"', conn)
                print(f"  Dados de exemplo:")
                print(df.head().to_string())
                print()
            except Exception as e:
                print(f"  Erro ao carregar dados: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar objetivos: {e}")

if __name__ == "__main__":
    print("=== Verificando dados do Positivador ===")
    check_columns()
    
    print("\n=== Verificando dados de Objetivos ===")
    check_objetivos()
