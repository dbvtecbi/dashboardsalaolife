import sqlite3
import pandas as pd

# Lista de bancos de dados para verificar
bancos = [
    'DBV Capital_Positivador.db',
    'DBV Capital_Positivador (MTD).db',
    'DBV Capital_FeeBased.db',
    'DBV Capital_Produtos.db'
]

for banco in bancos:
    print(f"\n{'='*60}")
    print(f"VERIFICANDO: {banco}")
    print('='*60)
    
    try:
        conn = sqlite3.connect(banco)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tabelas encontradas: {[t[0] for t in tables]}")
        
        # Para cada tabela, verificar estrutura e procurar colunas relevantes
        for table_name in [t[0] for t in tables]:
            print(f"\n--- Tabela: {table_name} ---")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Verificar se tem colunas relevantes
            colunas_relevantes = []
            for col in columns:
                col_name = col[1].lower()
                if any(keyword in col_name for keyword in ['data', 'cap', 'auc', 'acumulado', 'objetivo', 'diário', 'dia']):
                    colunas_relevantes.append(col[1])
            
            if colunas_relevantes:
                print(f"Colunas relevantes: {colunas_relevantes}")
                
                # Verificar alguns dados
                df_sample = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 2", conn)
                print("Amostra de dados:")
                print(df_sample[list(df_sample.columns[:5])].to_string())  # Primeiras 5 colunas
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao acessar {banco}: {e}")

print(f"\n{'='*60}")
print("VERIFICAÇÃO CONCLUÍDA")
print('='*60)
