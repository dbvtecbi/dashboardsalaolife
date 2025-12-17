import sqlite3

def list_table_columns():
    db_path = 'DBV Capital_Positivador.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas no banco de dados
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Tabelas no banco de dados:")
        for table in tables:
            table_name = table[0]
            print(f"\nTabela: {table_name}")
            
            # Obter informações das colunas
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print("\nColunas:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
            # Mostrar as primeiras linhas para referência
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
                first_row = cursor.fetchone()
                if first_row:
                    print("\nPrimeira linha de exemplo:")
                    col_names = [desc[0] for desc in cursor.description]
                    for name, value in zip(col_names, first_row):
                        print(f"{name}: {value}")
            except Exception as e:
                print(f"\nNão foi possível ler dados da tabela {table_name}: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")

if __name__ == "__main__":
    list_table_columns()
