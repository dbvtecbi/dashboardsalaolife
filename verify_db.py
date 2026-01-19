import sqlite3
import pandas as pd

# Verificar o banco de dados que criamos
db_file = r'c:\Users\techb_gc46061\Downloads\Dash_Salão_Capital_Life\DBV Capital_Positivador_MTD.db'

try:
    conn = sqlite3.connect(db_file)
    
    # Verificar se a tabela existe e tem dados
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f'Tabelas encontradas: {tables}')
    
    if tables:
        table_name = tables[0][0]
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        print(f'Registros na tabela {table_name}: {count}')
        
        # Verificar colunas importantes
        cursor.execute(f'PRAGMA table_info({table_name})')
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        print(f'Colunas: {col_names[:10]}...')  # Primeiras 10 colunas
        
        # Verificar se há dados não nulos
        if count > 0:
            cursor.execute(f'SELECT * FROM {table_name} LIMIT 3')
            sample = cursor.fetchall()
            print(f'Amostra de dados: {sample[0][:3] if sample else "Nenhum dado"}...')
    
    conn.close()
    
except Exception as e:
    print(f'Erro: {e}')
