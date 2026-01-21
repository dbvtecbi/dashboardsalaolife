"""
Teste simples com a data real do dashboard
"""
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    print("🔍 Teste com data real do dashboard")
    print("=" * 50)
    
    # Data real do dashboard
    data_ref = datetime(2026, 1, 19)
    print(f"Data de referência: {data_ref}")
    
    # Importar funções robustas
    try:
        from correcao_final import (
            carregar_dados_objetivos_pj1_robusto,
            obter_dados_captacao_mes_robusto,
            obter_dados_captacao_ano_robusto,
            obter_dados_auc_2026_robusto
        )
        print("✅ Funções importadas")
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        return
    
    # Carregar dados
    df = carregar_dados_objetivos_pj1_robusto()
    if df is None or df.empty:
        print("❌ Dados não carregados")
        return
    
    print(f"✅ Dados carregados: {len(df)} registros")
    
    # Verificar se a data existe
    data_str = data_ref.strftime('%Y-%m-%d')
    if data_str in df['Data'].dt.strftime('%Y-%m-%d').values:
        print(f"✅ Data {data_str} existe nos dados")
    else:
        print(f"❌ Data {data_str} NÃO existe nos dados")
        return
    
    # Testar funções
    print("\n🧪 Testando funções:")
    
    try:
        obj_mes, proj_mes = obter_dados_captacao_mes_robusto(df, data_ref)
        print(f"CAPTAÇÃO MÊS: Objetivo R$ {obj_mes:,.2f}, Projetado R$ {proj_mes:,.2f}")
        
        obj_ano, proj_ano = obter_dados_captacao_ano_robusto(df, data_ref)
        print(f"CAPTAÇÃO ANO: Objetivo R$ {obj_ano:,.2f}, Projetado R$ {proj_ano:,.2f}")
        
        obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
        print(f"AUC 2026: Objetivo R$ {obj_auc:,.2f}, Projetado R$ {proj_auc:,.2f}")
        
        # Verificar se algum valor é zero
        if obj_mes == 0 or proj_mes == 0:
            print("❌ PROBLEMA: CAPTAÇÃO MÊS com valores zerados!")
        if obj_ano == 0 or proj_ano == 0:
            print("❌ PROBLEMA: CAPTAÇÃO ANO com valores zerados!")
        if obj_auc == 0 or proj_auc == 0:
            print("❌ PROBLEMA: AUC 2026 com valores zerados!")
        
        if all(v > 0 for v in [obj_mes, proj_mes, obj_ano, proj_ano, obj_auc, proj_auc]):
            print("✅ Todos os valores estão corretos!")
        else:
            print("❌ Há valores zerados!")
            
    except Exception as e:
        print(f"❌ Erro ao testar funções: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
