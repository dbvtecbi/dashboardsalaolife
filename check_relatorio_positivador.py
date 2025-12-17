import sqlite3
import pandas as pd

def check_columns():
    db_path = "DBV Capital_Positivador (MTD).db"
    
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        
        # Obter informações das colunas da tabela
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info("Relatório Positivador")')
        columns = cursor.fetchall()
        
        print("Colunas na tabela 'Relatório Positivador':")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # Verificar se as colunas necessárias existem
        df = pd.read_sql_query('SELECT * FROM "Relatório Positivador" LIMIT 5', conn)
        print("\nPrimeiras 5 linhas:")
        print(df)
        
        # Verificar se existem dados para o ano atual
        if 'Data_Posição' in df.columns:
            print("\nDatas disponíveis:")
            print(f"Data mínima: {df['Data_Posição'].min()}")
            print(f"Data máxima: {df['Data_Posição'].max()}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")

if __name__ == "__main__":
    check_columns()
