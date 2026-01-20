import pandas as pd
from pathlib import Path

def investigar_projetados():
    """Investigar discrepância nos valores projetados"""
    
    caminho_csv = Path("DBV Capital_Positivador_MTD.csv")
    
    print("=== INVESTIGAÇÃO DE VALORES PROJETADOS ===")
    
    if not caminho_csv.exists():
        print(f"❌ Arquivo CSV não encontrado: {caminho_csv}")
        return
    
    # Ler o CSV
    df = pd.read_csv(caminho_csv)
    
    print(f"📊 Total de registros: {len(df)}")
    print(f"📋 Colunas: {list(df.columns)}")
    
    # Verificar colunas relacionadas a valores projetados
    colunas_projetados = [col for col in df.columns if 'projetad' in col.lower() or 'rumo' in col.lower() or 'auc' in col.lower()]
    print(f"\n🎯 Colunas de valores projetados: {colunas_projetados}")
    
    # Verificar valores únicos nas colunas de interesse
    colunas_interesse = ['Net em M 1', 'Net Em M', 'Net Renda Fixa', 'Net Fundos Imobiliários', 
                        'Net Renda Variável', 'Net Fundos', 'Net Financeiro', 'Net Previdência', 'Net Outros']
    
    print(f"\n📈 Análise das colunas de valores:")
    for col in colunas_interesse:
        if col in df.columns:
            # Remover valores nulos e converter para numérico
            valores = pd.to_numeric(df[col], errors='coerce').dropna()
            
            if not valores.empty:
                print(f"\n--- {col} ---")
                print(f"Registros não nulos: {len(valores)}")
                print(f"Valor mínimo: R$ {valores.min():,.2f}")
                print(f"Valor máximo: R$ {valores.max():,.2f}")
                print(f"Valor médio: R$ {valores.mean():,.2f}")
                print(f"Soma total: R$ {valores.sum():,.2f}")
                print(f"Valores únicos: {sorted(valores.unique())[:10]}")  # Primeiros 10 valores únicos
    
    # Verificar se há colunas específicas para "Rumo a 1bi" e "AUC-2026"
    print(f"\n🔍 Buscando colunas específicas:")
    for col in df.columns:
        if 'rumo' in col.lower() or 'auc' in col.lower():
            print(f"Coluna encontrada: {col}")
            valores_unicos = df[col].dropna().unique()
            print(f"Valores únicos: {valores_unicos}")
            print(f"Contagem: {df[col].value_counts().to_dict()}")
    
    # Verificar dados mais recentes
    if 'Data Atualização' in df.columns:
        print(f"\n📅 Dados mais recentes:")
        df['Data Atualização'] = pd.to_datetime(df['Data Atualização'], errors='coerce')
        data_max = df['Data Atualização'].max()
        print(f"Data mais recente: {data_max}")
        
        dados_recentes = df[df['Data Atualização'] == data_max]
        print(f"Registros na data mais recente: {len(dados_recentes)}")
        
        if not dados_recentes.empty:
            print("\nValores projetados mais recentes:")
            for col in colunas_interesse:
                if col in dados_recentes.columns:
                    valor = dados_recentes[col].iloc[0] if not pd.isna(dados_recentes[col].iloc[0]) else 'N/A'
                    print(f"  {col}: {valor}")

if __name__ == "__main__":
    investigar_projetados()
