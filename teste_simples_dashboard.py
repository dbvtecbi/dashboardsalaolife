"""
Teste simples para verificar se o dashboard pode ser carregado
"""
import sys
from pathlib import Path

def testar_carregamento():
    print("🧪 Teste simples do dashboard...")
    print("=" * 40)
    
    try:
        # Adicionar path
        sys.path.append(str(Path('.').absolute()))
        
        # Testar import das funções robustas
        print("1. Testando funções robustas...")
        from correcao_final import (
            carregar_dados_objetivos_pj1_robusto,
            obter_dados_captacao_mes_robusto,
            obter_dados_captacao_ano_robusto,
            obter_dados_auc_2026_robusto
        )
        print("✅ Funções robustas importadas!")
        
        # Testar carregamento de dados
        print("\n2. Testando carregamento de dados...")
        df = carregar_dados_objetivos_pj1_robusto()
        if df is not None:
            print(f"✅ Dados carregados: {len(df)} registros")
        else:
            print("❌ Falha ao carregar dados")
            return False
        
        # Testar funções principais
        print("\n3. Testando funções principais...")
        from datetime import datetime
        data_ref = datetime(2026, 1, 19)
        
        obj_mes, proj_mes = obter_dados_captacao_mes_robusto(df, data_ref)
        print(f"✅ CAPTAÇÃO MÊS: {obj_mes:,.2f} | {proj_mes:,.2f}")
        
        obj_ano, proj_ano = obter_dados_captacao_ano_robusto(df, data_ref)
        print(f"✅ CAPTAÇÃO ANO: {obj_ano:,.2f} | {proj_ano:,.2f}")
        
        obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
        print(f"✅ AUC 2026: {obj_auc:,.2f} | {proj_auc:,.2f}")
        
        print("\n✅ Todos os testes concluídos com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_carregamento()
    if sucesso:
        print("\n🎉 Dashboard está funcional!")
    else:
        print("\n❌ Há problemas no dashboard!")
