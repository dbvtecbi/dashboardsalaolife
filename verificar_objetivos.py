import sqlite3
import pandas as pd
from pathlib import Path

def verificar_objetivos():
    """Verificar o conteúdo do banco de objetivos para encontrar a discrepância"""
    
    caminho_db = Path("DBV Capital_Objetivos.db")
    
    print("=== VERIFICAÇÃO DO BANCO DE OBJETIVOS ===")
    
    if not caminho_db.exists():
        print(f"❌ Banco de objetivos não encontrado: {caminho_db}")
        return
    
    print(f"✅ Banco encontrado: {caminho_db}")
    print(f"Tamanho: {caminho_db.stat().st_size} bytes")
    
    conn = sqlite3.connect(str(caminho_db))
    
    try:
        # Verificar tabelas
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        print(f"\n📋 Tabelas: {[t[0] for t in tabelas]}")
        
        # Ler dados da tabela objetivos
        if tabelas:
            df = pd.read_sql_query('SELECT * FROM objetivos', conn)
            print(f"\n📊 Dados da tabela objetivos:")
            print(f"Registros: {len(df)}")
            print(f"Colunas: {list(df.columns)}")
            
            if not df.empty:
                print(f"\n📈 Dados completos:")
                for i, row in df.iterrows():
                    print(f"Registro {i+1}:")
                    for col in df.columns:
                        print(f"  {col}: {row[col]}")
                    print()
                
                # Verificar especificamente os valores de AUC
                if 'AUC Inicial' in df.columns:
                    print(f"\n🎯 Valores de AUC Inicial:")
                    for idx, val in df['AUC Inicial'].items():
                        if pd.notna(val):
                            print(f"  Registro {idx}: R$ {float(val):,.2f}")
                
                # Verificar objetivos por ano
                if 'Objetivo' in df.columns:
                    print(f"\n📅 Objetivos por ano:")
                    objetivos_ano = df.groupby('Objetivo')['AUC Inicial'].apply(lambda x: x.max() if pd.notna(x).any() else 0)
                    for ano, auc_val in objetivos_ano.items():
                        print(f"  {ano}: R$ {float(auc_val):,.2f}")
    
    except Exception as e:
        print(f"❌ Erro ao ler banco: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verificar_objetivos()
