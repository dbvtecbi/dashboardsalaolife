import sqlite3
import pandas as pd
from pathlib import Path

# Caminhos dos arquivos
caminho_db_origem = Path("DBV Capital_Produtos.db")
caminho_csv = Path("DBV Capital_Produtos.csv")
caminho_db_destino = Path("DBV Capital_Produtos_Novo.db")

print("=== CONVERSÃO DO BANCO DE DADOS ===")

# 1. Conectar ao banco original
print(f"Conectando ao banco: {caminho_db_origem}")
conn_origem = sqlite3.connect(str(caminho_db_origem))

# 2. Verificar tabelas disponíveis
cursor = conn_origem.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = [t[0] for t in cursor.fetchall()]
print(f"Tabelas encontradas: {tabelas}")

# 3. Processar cada tabela
for nome_tabela in tabelas:
    print(f"\n--- Processando tabela: {nome_tabela} ---")
    
    # Ler todos os dados da tabela
    query = f"SELECT * FROM \"{nome_tabela}\""
    df = pd.read_sql_query(query, conn_origem)
    
    print(f"Registros encontrados: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    
    # Salvar como CSV
    if len(tabelas) == 1:
        df.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
        print(f"✅ CSV salvo: {caminho_csv}")
    else:
        csv_tabela = Path(f"DBV Capital_Produtos_{nome_tabela}.csv")
        df.to_csv(csv_tabela, index=False, encoding='utf-8-sig')
        print(f"✅ CSV salvo: {csv_tabela}")
    
    # Criar novo banco de dados
    conn_destino = sqlite3.connect(str(caminho_db_destino))
    df.to_sql(nome_tabela, conn_destino, index=False, if_exists='replace')
    conn_destino.close()
    print(f"✅ Tabela '{nome_tabela}' criada no novo banco")

conn_origem.close()

print(f"\n✅ Banco de dados novo criado: {caminho_db_destino}")
print("=== PROCESSO CONCLUÍDO ===")
