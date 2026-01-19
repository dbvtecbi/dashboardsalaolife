import sqlite3
import pandas as pd

def verificar_conversao(db_path):
    """
    Verifica os dados convertidos no banco de dados SQLite
    """
    print(f"Verificando banco de dados: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print(f"\nTabelas encontradas: {len(tabelas)}")
        
        total_linhas = 0
        total_colunas = 0
        
        for tabela in tabelas:
            nome_tabela = tabela[0]
            print(f"\n--- Tabela: {nome_tabela} ---")
            
            # Contar linhas
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            linhas = cursor.fetchone()[0]
            
            # Contar colunas
            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas_info = cursor.fetchall()
            num_colunas = len(colunas_info)
            
            print(f"Linhas: {linhas}")
            print(f"Colunas: {num_colunas}")
            
            # Mostrar primeiras 3 linhas
            cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 3")
            primeiras_linhas = cursor.fetchall()
            
            if primeiras_linhas:
                print("Primeiras 3 linhas:")
                for i, linha in enumerate(primeiras_linhas, 1):
                    print(f"  {i}: {linha}")
            
            total_linhas += linhas
            total_colunas += num_colunas
        
        print(f"\n--- RESUMO ---")
        print(f"Total de tabelas: {len(tabelas)}")
        print(f"Total de linhas: {total_linhas}")
        print(f"Total de colunas: {total_colunas}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar banco de dados: {str(e)}")

if __name__ == "__main__":
    verificar_conversao("DBV Capital_Objetivos.db")
