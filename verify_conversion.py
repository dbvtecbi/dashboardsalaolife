import sqlite3
import pandas as pd

def verify_conversion():
    """Verifica se a conversão foi bem-sucedida"""
    
    # Verificar CSV
    try:
        df_csv = pd.read_csv('DBV Capital_Positivador (MTD).csv')
        print(f"✅ CSV verificado:")
        print(f"   - Linhas: {len(df_csv)}")
        print(f"   - Colunas: {len(df_csv.columns)}")
        print(f"   - Primeiras colunas: {list(df_csv.columns)[:5]}")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
    
    # Verificar DB
    try:
        conn = sqlite3.connect('DBV Capital_Positivador (MTD).db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM positivador_mtd")
        row_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA table_info(positivador_mtd)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        cursor.execute("SELECT * FROM positivador_mtd LIMIT 3")
        sample_data = cursor.fetchall()
        
        print(f"\n✅ DB verificado:")
        print(f"   - Linhas: {row_count}")
        print(f"   - Colunas: {len(column_names)}")
        print(f"   - Primeiras colunas: {column_names[:5]}")
        print(f"   - Amostra de dados (primeiras 3 linhas, 5 colunas):")
        for i, row in enumerate(sample_data):
            print(f"     Linha {i+1}: {row[:5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao ler DB: {e}")

if __name__ == "__main__":
    verify_conversion()
