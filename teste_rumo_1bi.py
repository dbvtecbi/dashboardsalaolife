"""
Teste da nova lógica do card RUMO A 1BI
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    print("🔍 Teste da Nova Lógica RUMO A 1BI")
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
    
    # Testar a nova função
    try:
        objetivo_total, projetado_acumulado = obter_dados_rumo_1bi_robusto(df, data_ref)
        
        print(f"\n🎯 Resultados da Nova Lógica:")
        print(f"Objetivo Total (2027): R$ {objetivo_total:,.2f}")
        print(f"Projetado Acumulado: R$ {projetado_acumulado:,.2f}")
        
        # Verificação
        if objetivo_total > 0 and projetado_acumulado > 0:
            print("✅ Valores corretos!")
            
            # Comparar com AUC-2026
            from correcao_final import obter_dados_auc_2026_robusto
            obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
            
            print(f"\n📊 Comparação com AUC-2026:")
            print(f"AUC-2026 - Objetivo: R$ {obj_auc:,.2f}, Projetado: R$ {proj_auc:,.2f}")
            print(f"RUMO-1BI - Objetivo: R$ {objetivo_total:,.2f}, Projetado: R$ {projetado_acumulado:,.2f}")
            
            # Verificar se o projetado é o mesmo (deveria ser)
            if abs(projetado_acumulado - proj_auc) < 0.01:
                print("✅ Projetado igual ao AUC-2026 (conforme solicitado)")
            else:
                print("⚠️ Projetado diferente do AUC-2026")
                
            # Verificar se o objetivo é maior (deveria ser para 2027)
            if objetivo_total > obj_auc:
                print("✅ Objetivo maior que AUC-2026 (conforme esperado para 2027)")
            else:
                print("⚠️ Objetivo não é maior que AUC-2026")
                
        else:
            print("❌ Valores zerados!")
            
    except Exception as e:
        print(f"❌ Erro ao testar função: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n🎉 Teste concluído!")
    print("Execute: `streamlit run Home.py` para ver no dashboard.")

if __name__ == "__main__":
    main()
