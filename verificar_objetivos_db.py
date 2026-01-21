import sqlite3
import pandas as pd

# Conectar ao banco de dados
conn = sqlite3.connect('DBV Capital_Objetivos.db')

# Verificar tabelas
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tabelas encontradas:")
for table in tables:
    print(f"- {table[0]}")

# Verificar estrutura da tabela objetivos
if any('objetivos' in str(table) for table in tables):
    print("\nEstrutura da tabela objetivos:")
    cursor.execute("PRAGMA table_info(objetivos);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    # Verificar primeiros dados
    print("\nPrimeiros 10 registros:")
    df = pd.read_sql_query("SELECT * FROM objetivos LIMIT 10", conn)
    print(df)
    
    # Verificar todas as colunas disponíveis
    print("\nColunas disponíveis:")
    for i, col in enumerate(df.columns):
        print(f"- col_{i}: {df[col].dtype}")
    
    # Verificar dados específicos por linha
    print("\nDados detalhados por linha:")
    for idx, row in df.head(3).iterrows():
        print(f"\nLinha {idx}:")
        for i, col in enumerate(df.columns):
            print(f"  col_{i}: {row[col]}")

conn.close()
