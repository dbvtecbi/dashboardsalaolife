import sqlite3
import pandas as pd

def check_columns():
    db_path = "DBV Capital_Positivador (MTD).db"
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        
        # Obter nomes das tabelas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Tabelas no banco de dados:")
        for table in tables:
            table_name = table[0]
            print(f"\nTabela: {table_name}")
            
            # Obter informações das colunas
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("\nColunas:")
            for col in columns:
                col_id, col_name, col_type, notnull, default_val, pk = col
                print(f"- {col_name} ({col_type}){' [PK]' if pk else ''}")
            
            # Mostrar primeiras linhas como exemplo
            try:
                df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 1", conn)
                print("\nExemplo de dados (primeira linha):")
                for col in df.columns:
                    print(f"- {col}: {df[col].iloc[0] if not df.empty else 'N/A'}")
            except Exception as e:
                print(f"\nErro ao ler dados da tabela: {e}")
            
            print("\n" + "="*80 + "\n")
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_columns()
