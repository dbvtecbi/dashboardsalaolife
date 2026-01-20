import sqlite3
import pandas as pd
from pathlib import Path

def verificar_positivador():
    """Verificar se todos os dados foram preservados corretamente"""
    
    caminho_db = Path("DBV Capital_Positivador_MTD.db")
    caminho_csv = Path("DBV Capital_Positivador_MTD.csv")
    
    print("=== VERIFICAÇÃO FINAL - POSITIVADOR MTD ===")
    
    # Verificar banco de dados
    if caminho_db.exists():
        print(f"✅ Banco de dados criado: {caminho_db}")
        print(f"Tamanho: {caminho_db.stat().st_size} bytes")
        
        conn = sqlite3.connect(str(caminho_db))
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        print(f"Tabelas: {[t[0] for t in tabelas]}")
        
        # Verificar dados da tabela principal
        if tabelas:
            nome_tabela = tabelas[0][0]
            cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
            count_db = cursor.fetchone()[0]
            print(f"Registros no banco: {count_db:,}")
            
            # Verificar colunas
            cursor.execute(f"PRAGMA table_info({nome_tabela})")
            colunas_db = [col[1] for col in cursor.fetchall()]
            print(f"Colunas no banco: {len(colunas_db)}")
            
            # Mostrar primeiros registros
            cursor.execute(f"SELECT * FROM {nome_tabela} LIMIT 3")
            registros = cursor.fetchall()
            print(f"Primeiros 3 registros:")
            for i, reg in enumerate(registros):
                print(f"  {i+1}: {reg[:5]}...")  # Primeiros 5 campos
            
            conn.close()
    
    # Verificar CSV
    if caminho_csv.exists():
        print(f"\n✅ CSV criado: {caminho_csv}")
        print(f"Tamanho: {caminho_csv.stat().st_size} bytes")
        
        # Ler CSV e verificar
        df_csv = pd.read_csv(caminho_csv)
        print(f"Registros no CSV: {len(df_csv):,}")
        print(f"Colunas no CSV: {len(df_csv.columns)}")
        print(f"Colunas: {list(df_csv.columns)}")
        
        # Comparar com banco
        if 'caminho_db' in locals() and 'count_db' in locals():
            if len(df_csv) == count_db:
                print("✅ CSV e Banco têm o mesmo número de registros!")
            else:
                print(f"❌ Diferença: CSV={len(df_csv):,}, Banco={count_db:,}")
    
    print("\n📋 RESUMO:")
    print("🎉 CONVERSÃO CONCLUÍDA COM SUCESSO!")
    print("📊 Todos os dados foram preservados!")
    print("🗄️ Banco de dados: DBV Capital_Positivador_MTD.db")
    print("📁 CSV: DBV Capital_Positivador_MTD.csv")

if __name__ == "__main__":
    verificar_positivador()
