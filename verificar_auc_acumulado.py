"""
Verificar o valor exato do AUC Acumulado para 19/01/2026
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Adicionar paths
sys.path.append(str(Path(__file__).parent))

def main():
    print("🔍 Verificando AUC Acumulado - 19/01/2026")
    print("=" * 50)
    
    # Importar função robusta
    try:
        from correcao_final import carregar_dados_objetivos_pj1_robusto
        print("✅ Função importada")
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        return
    
    # Data de referência
    data_ref = datetime(2026, 1, 19)
    print(f"📅 Data de referência: {data_ref}")
    
    # Carregar dados
    try:
        df = carregar_dados_objetivos_pj1_robusto()
        if df is not None and not df.empty:
            print(f"✅ Dados carregados: {len(df)} registros")
        else:
            print("❌ Dados não carregados")
            return
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    # Verificar dados da data específica
    data_str = data_ref.strftime('%Y-%m-%d')
    print(f"\n🔍 Procurando dados para {data_str}:")
    
    # Garantir que Data seja datetime
    if not pd.api.types.is_datetime64_any_dtype(df['Data']):
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    
    # Filtrar pela data exata
    df_data = df[df['Data'].dt.strftime('%Y-%m-%d') == data_str]
    
    if not df_data.empty:
        print(f"✅ Encontrado {len(df_data)} registro(s) para {data_str}")
        
        # Mostrar dados completos
        print("\n📊 Dados completos:")
        for idx, row in df_data.iterrows():
            print(f"Data: {row['Data']}")
            print(f"AUC Objetivo (Ano): {row['AUC Objetivo (Ano)']}")
            print(f"AUC Acumulado: {row['AUC Acumulado']}")
            print(f"Cap Objetivo (ano): {row['Cap Objetivo (ano)']}")
            print(f"Cap Acumulado: {row['Cap Acumulado']}")
            print("-" * 30)
        
        # Valor exato do AUC Acumulado
        valor_exato = float(df_data['AUC Acumulado'].iloc[0])
        print(f"\n💰 Valor exato do AUC Acumulado: {valor_exato}")
        print(f"💰 Arredondado (1 casa): {valor_exato/1_000_000:.1f}M")
        print(f"💰 Arredondado (2 casas): {valor_exato/1_000_000:.2f}M")
        
        # Verificar qual valor está sendo retornado pela função
        from correcao_final import obter_dados_auc_2026_robusto, obter_dados_rumo_1bi_robusto
        
        obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
        obj_rumo, proj_rumo = obter_dados_rumo_1bi_robusto(df, data_ref)
        
        print(f"\n🔍 Valores retornados pelas funções:")
        print(f"AUC-2026 - Projetado: R$ {proj_auc:,.2f} ({proj_auc/1_000_000:.1f}M)")
        print(f"RUMO-1BI - Projetado: R$ {proj_rumo:,.2f} ({proj_rumo/1_000_000:.1f}M)")
        
        # Verificar diferença
        diferenca = abs(valor_exato - proj_auc)
        print(f"\n📏 Diferença: R$ {diferenca:,.2f}")
        
        if diferenca < 1000:  # Menos de 1.000 de diferença
            print("✅ Valores praticamente iguais (diferença < R$ 1.000)")
        else:
            print("⚠️ Diferença significativa detectada!")
            
    else:
        print(f"❌ Nenhum registro encontrado para {data_str}")
        
        # Mostrar datas próximas
        print("\n📅 Datas disponíveis próximas:")
        df_sorted = df.sort_values('Data')
        data_ref_ts = pd.Timestamp(data_ref)
        
        # Encontrar registros mais próximos
        df_sorted['diferenca'] = abs(df_sorted['Data'] - data_ref_ts)
        proximos = df_sorted.nsmallest(5, 'diferenca')
        
        for idx, row in proximos.iterrows():
            print(f"Data: {row['Data'].strftime('%Y-%m-%d')} | AUC Acumulado: {row['AUC Acumulado']}")

if __name__ == "__main__":
    main()
