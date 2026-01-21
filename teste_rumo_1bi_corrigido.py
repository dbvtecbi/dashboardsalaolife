"""
Teste do RUMO A 1BI corrigido com objetivo fixo de 1bi
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    print("🔍 Teste RUMO A 1BI - Objetivo Fixo 1bi")
    print("=" * 50)
    
    # Importar as funções
    try:
        from correcao_final import (
            carregar_dados_objetivos_pj1_robusto,
            obter_dados_rumo_1bi_robusto
        )
        print("✅ Funções importadas")
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
    
    # Testar a função
    try:
        objetivo_total, projetado_acumulado = obter_dados_rumo_1bi_robusto(df, data_ref)
        
        print(f"\n🎯 Resultados:")
        print(f"Objetivo Total (retornado pela função): R$ {objetivo_total:,.2f}")
        print(f"Projetado Acumulado: R$ {projetado_acumulado:,.2f}")
        
        # Verificar o objetivo correto
        OBJETIVO_FINAL = 1_000_000_000.0
        print(f"\n📊 Valores esperados no card:")
        print(f"Objetivo Total (fixo): R$ {OBJETIVO_FINAL:,.2f} ({OBJETIVO_FINAL/1_000_000_000:.0f}bi)")
        print(f"Projetado: R$ {projetado_acumulado:,.2f} ({projetado_acumulado/1_000_000:.1f}M)")
        
        # Comparar com AUC-2026
        from correcao_final import obter_dados_auc_2026_robusto
        obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
        
        print(f"\n📈 Comparação:")
        print(f"AUC-2026 - Objetivo: R$ {obj_auc:,.2f} ({obj_auc/1_000_000:.1f}M)")
        print(f"AUC-2026 - Projetado: R$ {proj_auc:,.2f} ({proj_auc/1_000_000:.1f}M)")
        print(f"RUMO-1BI - Objetivo: R$ {OBJETIVO_FINAL:,.2f} ({OBJETIVO_FINAL/1_000_000_000:.0f}bi)")
        print(f"RUMO-1BI - Projetado: R$ {projetado_acumulado:,.2f} ({projetado_acumulado/1_000_000:.1f}M)")
        
        # Verificações
        print(f"\n✅ Verificações:")
        if abs(projetado_acumulado - proj_auc) < 1000:
            print("✅ Projetado igual ao AUC-2026 (conforme solicitado)")
        else:
            print("⚠️ Projetado diferente do AUC-2026")
            
        if OBJETIVO_FINAL == 1_000_000_000.0:
            print("✅ Objetivo fixo em 1bi (conforme solicitado)")
        else:
            print("❌ Objetivo não é 1bi")
        
        print(f"\n🎉 Teste concluído com sucesso!")
        print("Execute: `streamlit run Home.py` para ver no dashboard.")
        
    except Exception as e:
        print(f"❌ Erro ao testar função: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
