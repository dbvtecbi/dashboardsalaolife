import sqlite3
import pandas as pd

def verificar_estrutura_produtos():
    """Verifica a estrutura do banco de dados DBV Capital_Produtos.db"""
    
    print("🔍 Verificando estrutura do DBV Capital_Produtos.db...")
    
    try:
        conn = sqlite3.connect('DBV Capital_Produtos.db')
        cursor = conn.cursor()
        
        # Verificar tabelas disponíveis
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        print(f"\n📋 Tabelas encontradas:")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
        
        # Verificar estrutura da tabela principal
        tabela_principal = None
        for tabela in tabelas:
            if 'produtos' in tabela[0].lower():
                tabela_principal = tabela[0]
                break
        
        if not tabela_principal:
            print("❌ Não encontrei tabela de produtos")
            return None
        
        print(f"\n📊 Estrutura da tabela '{tabela_principal}':")
        cursor.execute(f"PRAGMA table_info({tabela_principal})")
        colunas = cursor.fetchall()
        
        for col in colunas:
            print(f"   - {col[1]} ({col[2]})")
        
        # Verificar dados amostra
        query = f"SELECT * FROM {tabela_principal} LIMIT 5"
        df_amostra = pd.read_sql_query(query, conn)
        
        print(f"\n📊 Amostra de dados ({len(df_amostra)} linhas):")
        print(df_amostra.to_string())
        
        # Verificar áreas únicas
        cursor.execute(f"SELECT DISTINCT area FROM {tabela_principal} LIMIT 20")
        areas = cursor.fetchall()
        
        print(f"\n🏢 Áreas encontradas:")
        for area in areas:
            if area[0]:
                print(f"   - {area[0]}")
        
        # Verificar assessores únicos
        cursor.execute(f"SELECT DISTINCT codigo_assessor FROM {tabela_principal} LIMIT 20")
        assessores = cursor.fetchall()
        
        print(f"\n👥 Assessores encontrados:")
        for ass in assessores:
            if ass[0]:
                print(f"   - {ass[0]}")
        
        conn.close()
        return df_amostra, colunas
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None, None

if __name__ == "__main__":
    verificar_estrutura_produtos()
