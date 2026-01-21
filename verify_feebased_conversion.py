import sqlite3
import pandas as pd

def verify_feebased_conversion():
    """Verifica se a conversão do FeeBased foi bem-sucedida"""
    
    # Verificar CSV
    try:
        df_csv = pd.read_csv('DBV Capital_FeeBased.csv')
        print(f"✅ CSV verificado:")
        print(f"   - Linhas: {len(df_csv)}")
        print(f"   - Colunas: {len(df_csv.columns)}")
        print(f"   - Colunas: {list(df_csv.columns)}")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
    
    # Verificar DB
    try:
        conn = sqlite3.connect('DBV Capital_FeeBased.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM feebased")
        row_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA table_info(feebased)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        cursor.execute("SELECT * FROM feebased LIMIT 3")
        sample_data = cursor.fetchall()
        
        print(f"\n✅ DB verificado:")
        print(f"   - Linhas: {row_count}")
        print(f"   - Colunas: {len(column_names)}")
        print(f"   - Colunas: {column_names}")
        print(f"   - Amostra de dados (primeiras 3 linhas):")
        for i, row in enumerate(sample_data):
            print(f"     Linha {i+1}: {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao ler DB: {e}")

if __name__ == "__main__":
    verify_feebased_conversion()
