import pandas as pd

def verificar_assessores_pl():
    """Verifica a estrutura do arquivo Assessores_PL.xlsx"""
    
    print("🔍 Verificando estrutura do arquivo Assessores_PL.xlsx...")
    
    try:
        df = pd.read_excel("Assessores_PL.xlsx")
        
        print(f"📊 Dimensões: {df.shape}")
        print(f"📋 Colunas: {list(df.columns)}")
        print(f"\n📄 Primeiras linhas:")
        print(df.head())
        
        print(f"\n📄 Tipos de dados:")
        print(df.dtypes)
        
        return df
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

if __name__ == "__main__":
    verificar_assessores_pl()
