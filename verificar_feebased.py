import pandas as pd

def verificar_feebased():
    """Verifica os códigos dos assessores no arquivo FeeBased"""
    
    print("🔍 Verificando códigos no arquivo FeeBased...")
    
    try:
        # Ler arquivo FeeBased
        df_feebased = pd.read_excel("DBV Capital_FeeBased.xlsx")
        
        # Filtrar apenas ativos
        df_ativos = df_feebased[df_feebased['Status'] == 'Ativo'].copy()
        
        # Converter P/L para numérico
        df_ativos['pl_numeric'] = pd.to_numeric(df_ativos['P/L'], errors='coerce').fillna(0)
        
        # Agrupar por assessor
        pl_por_assessor = df_ativos.groupby('Código Assessor')['pl_numeric'].agg(['sum', 'count']).reset_index()
        pl_por_assessor.columns = ['Código Assessor', 'Total PL', 'QTD Clientes']
        
        print(f"📊 Assessores com FeeBased ativo:")
        print(pl_por_assessor.sort_values('Total PL', ascending=False).to_string(index=False))
        
        print(f"\n📋 Códigos únicos de assessores no FeeBased:")
        codigos_feebased = sorted(df_ativos['Código Assessor'].unique())
        print(codigos_feebased)
        
        # Ler arquivo enriquecido
        df_enriquecido = pd.read_excel("Assessores_PL_Enriquecido.xlsx")
        codigos_enriquecido = sorted(df_enriquecido['CÓDIGO ASSESSOR'].astype(str).unique())
        
        print(f"\n📋 Códigos únicos no arquivo enriquecido:")
        print(codigos_enriquecido)
        
        # Verificar interseção
        set_feebased = set(df_ativos['Código Assessor'].astype(str))
        set_enriquecido = set(codigos_enriquecido)
        
        intersecao = set_feebased.intersection(set_enriquecido)
        print(f"\n🔗 Códigos em comum: {len(intersecao)}")
        print(sorted(intersecao))
        
        print(f"\n❌ Códigos no FeeBased mas não no enriquecido: {len(set_feebased - set_enriquecido)}")
        print(sorted(set_feebased - set_enriquecido))
        
        return pl_por_assessor
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None

if __name__ == "__main__":
    verificar_feebased()
