import sqlite3
from pathlib import Path

# Verificar o banco criado
caminho_db = Path('DBV Capital_Produtos.db')
conn = sqlite3.connect(str(caminho_db))
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()
print(f'Tabelas: {tabelas}')

if tabelas:
    cursor.execute("SELECT COUNT(*) FROM Produtos")
    count = cursor.fetchone()[0]
    print(f'Registros na tabela Produtos: {count}')
    
    # Verificar dados de Câmbio
    cursor.execute("SELECT COUNT(*) FROM Produtos WHERE \"Linha Receita\" LIKE '%Câmbio%'")
    cambio_count = cursor.fetchone()[0]
    print(f'Registros de Câmbio: {cambio_count}')
    
    # Verificar linhas de receita
    cursor.execute("SELECT DISTINCT \"Linha Receita\" FROM Produtos")
    linhas = cursor.fetchall()
    print(f'Linhas de receita: {[l[0] for l in linhas]}')

conn.close()
