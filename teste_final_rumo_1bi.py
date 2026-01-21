"""
Teste final do RUMO A 1BI com objetivo do banco de dados
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar paths
sys.path.append(str(Path(__file__).parent))

def main():
    print("🔍 Teste Final RUMO A 1BI")
    print("=" * 50)
    
    # Importar funções
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
        
        print(f"\n🎯 Resultados RUMO A 1BI:")
        print(f"Objetivo Total: R$ {objetivo_total:,.2f} ({objetivo_total/1_000_000:.1f}M)")
        print(f"Projetado: R$ {projetado_acumulado:,.2f} ({projetado_acumulado/1_000_000:.1f}M)")
        
        # Verificar se está pegando do banco
        if objetivo_total > 694_000_000:  # Maior que o objetivo de 2026
            print("✅ Objetivo maior que 2026 (usando projeção para 2027)")
        else:
            print("⚠️ Objetivo não parece ser de 2027")
        
        # Comparar com AUC-2026
        from correcao_final import obter_dados_auc_2026_robusto
        obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
        
        print(f"\n📊 Comparação:")
        print(f"AUC-2026 - Objetivo: R$ {obj_auc:,.2f} ({obj_auc/1_000_000:.1f}M)")
        print(f"AUC-2026 - Projetado: R$ {proj_auc:,.2f} ({proj_auc/1_000_000:.1f}M)")
        print(f"RUMO-1BI - Objetivo: R$ {objetivo_total:,.2f} ({objetivo_total/1_000_000:.1f}M)")
        print(f"RUMO-1BI - Projetado: R$ {projetado_acumulado:,.2f} ({projetado_acumulado/1_000_000:.1f}M)")
        
        # Verificações
        print(f"\n✅ Verificações:")
        if abs(projetado_acumulado - proj_auc) < 1000:
            print("✅ Projetado igual ao AUC-2026 (conforme solicitado)")
        else:
            print("⚠️ Projetado diferente do AUC-2026")
        
        if objetivo_total > obj_auc:
            print("✅ Objetivo RUMO-1BI maior que AUC-2026 (conforme esperado)")
        else:
            print("⚠️ Objetivo RUMO-1BI não é maior que AUC-2026")
        
        print(f"\n🎉 Teste final concluído!")
        print("Execute: `streamlit run Home.py` para ver no dashboard.")
        
    except Exception as e:
        print(f"❌ Erro ao testar função: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
