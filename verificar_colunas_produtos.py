import sqlite3
import pandas as pd

def verificar_colunas_produtos():
    """Verifica todas as colunas e valores únicos do DBV Capital_Produtos.db"""
    
    print("🔍 Verificando colunas e valores do DBV Capital_Produtos.db...")
    
    try:
        conn = sqlite3.connect('DBV Capital_Produtos.db')
        
        # Verificar todas as colunas
        query = "PRAGMA table_info(Produtos)"
        df_colunas = pd.read_sql_query(query, conn)
        
        print("📋 Colunas disponíveis:")
        for _, row in df_colunas.iterrows():
            print(f"   - {row['name']} ({row['type']})")
        
        # Verificar valores únicos de cada coluna relevante
        colunas_relevantes = ['Produto', 'Fonte Receita', 'Linha Receita', 'Categoria']
        
        for coluna in colunas_relevantes:
            print(f"\n📊 Valores únicos de '{coluna}':")
            query = f"SELECT DISTINCT [{coluna}] FROM Produtos WHERE [{coluna}] IS NOT NULL AND [{coluna}] != '' LIMIT 20"
            df_valores = pd.read_sql_query(query, conn)
            
            for _, row in df_valores.iterrows():
                if row[coluna]:
                    print(f"   - {row[coluna]}")
        
        # Verificar se há coluna que possa ser a "área"
        query = "SELECT * FROM Produtos LIMIT 3"
        df_amostra = pd.read_sql_query(query, conn)
        
        print(f"\n📊 Amostra completa de dados:")
        print(df_amostra.to_string())
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    verificar_colunas_produtos()
