import sqlite3
import pandas as pd

def verificar_estrutura_objetivos():
    """Verifica a estrutura da tabela Objetivos_PJ1"""
    
    print("🔍 Verificando estrutura da tabela Objetivos_PJ1...")
    
    try:
        conn = sqlite3.connect('DBV Capital_Objetivos.db')
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Objetivos_PJ1'")
        tabela = cursor.fetchone()
        
        if not tabela:
            print("❌ Tabela Objetivos_PJ1 não encontrada")
            return None
        
        print("✅ Tabela Objetivos_PJ1 encontrada")
        
        # Verificar colunas
        cursor.execute("PRAGMA table_info(Objetivos_PJ1)")
        colunas = cursor.fetchall()
        
        print("\n📋 Estrutura da tabela:")
        for col in colunas:
            print(f"   - {col[1]} ({col[2]})")
        
        # Verificar dados amostra
        query = "SELECT * FROM Objetivos_PJ1 LIMIT 5"
        df_amostra = pd.read_sql_query(query, conn)
        
        print(f"\n📊 Amostra de dados ({len(df_amostra)} linhas):")
        print(df_amostra.to_string())
        
        # Verificar período dos dados
        cursor.execute("SELECT MIN(Data), MAX(Data), COUNT(*) FROM Objetivos_PJ1")
        periodo = cursor.fetchone()
        
        print(f"\n📅 Período dos dados:")
        print(f"   - Data inicial: {periodo[0]}")
        print(f"   - Data final: {periodo[1]}")
        print(f"   - Total registros: {periodo[2]}")
        
        conn.close()
        return df_amostra
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

if __name__ == "__main__":
    verificar_estrutura_objetivos()
