"""
Debug para verificar o contexto exato do dashboard
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Mock completo do streamlit
class MockSt:
    def set_page_config(self, *args, **kwargs): pass
    def markdown(self, content, unsafe_allow_html=False): 
        print(f"[MARKDOWN] {content[:100]}...")
    def cache_data(self, show_spinner=True):
        def decorator(func): return func
        return decorator
    class cache_data:
        def __init__(self, show_spinner=True): 
            self.show_spinner = show_spinner
        def __call__(self, func): 
            return func
    def spinner(self, text):
        class SpinnerContext:
            def __enter__(self): print(f"[SPINNER] {text}")
            def __exit__(self, *args): print("[SPINNER] Fim")
        return SpinnerContext()

sys.modules['streamlit'] = MockSt()

# Importar as funções do dashboard
sys.path.append(str(Path('.').absolute() / 'pages'))

def testar_contexto_cards():
    print("🎭 TESTE DO CONTEXTO EXATO DO DASHBOARD")
    print("=" * 60)
    
    # Simular variáveis que existem no dashboard
    data_ref = pd.Timestamp("2026-01-19").normalize()
    print(f"📅 data_ref: {data_ref}")
    
    # Simular mets (métricas)
    mets = {
        "capliq_mes": {"valor": 29600000.0},  # R$ 29,6M (valor realizado correto)
        "capliq_ano": {"valor": 29600000.0},
        "auc": {"valor": 474900000.0}  # R$ 474,9M (valor realizado correto)
    }
    print(f"📊 mets: {mets}")
    
    # Importar funções robustas
    from correcao_final import (
        carregar_dados_objetivos_pj1_robusto as carregar_dados_objetivos_pj1,
        obter_dados_captacao_mes_robusto as obter_dados_captacao_mes,
        obter_dados_captacao_ano_robusto as obter_dados_captacao_ano,
        obter_dados_auc_2026_robusto as obter_dados_auc_2026
    )
    
    # Importar função de formatação
    exec(open('pages/Dashboard_Salão_Atualizado.py').read().split('def formatar_valor_curto')[0])
    
    print("\n" + "="*50)
    print("📋 TESTE DO CARD CAPTAÇÃO LÍQUIDA MÊS")
    print("="*50)
    
    # Carregar dados
    df_objetivos_pj1 = carregar_dados_objetivos_pj1()
    
    if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
        print("✅ Usando nova lógica (Objetivos_PJ1)")
        
        # EXATAMENTE como no dashboard
        objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
        obj_total_mes = objetivo_total_mes
        threshold_mes = projetado_mes
        
        print(f"🔢 Valores brutos:")
        print(f"   objetivo_total_mes: {objetivo_total_mes} (tipo: {type(objetivo_total_mes)})")
        print(f"   projetado_mes: {projetado_mes} (tipo: {type(projetado_mes)})")
        print(f"   obj_total_mes: {obj_total_mes} (tipo: {type(obj_total_mes)})")
        print(f"   threshold_mes: {threshold_mes} (tipo: {type(threshold_mes)})")
        
        print(f"\n🎨 Valores formatados:")
        print(f"   obj_total_mes formatado: {formatar_valor_curto(obj_total_mes)}")
        print(f"   threshold_mes formatado: {formatar_valor_curto(threshold_mes)}")
        
        # Valor realizado
        v_mes = float(mets.get("capliq_mes", {}).get("valor", 0.0) or 0.0)
        print(f"   v_mes (realizado): R$ {v_mes:,.2f}")
        
        # Verificar se há algum problema
        if obj_total_mes == 0:
            print("⚠️  PROBLEMA: obj_total_mes é 0!")
        if threshold_mes == 0:
            print("⚠️  PROBLEMA: threshold_mes é 0!")
        if threshold_mes == 1:
            print("⚠️  PROBLEMA: threshold_mes é 1!")
            
    else:
        print("❌ Usando fallback (lógica antiga)")
    
    print("\n" + "="*50)
    print("📋 TESTE DO CARD CAPTAÇÃO LÍQUIDA ANO")
    print("="*50)
    
    if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
        objetivo_total, projetado_acumulado = obter_dados_captacao_ano(df_objetivos_pj1, data_ref)
        meta_eoy_col = objetivo_total
        threshold_ano_col = projetado_acumulado
        
        print(f"🔢 Valores brutos:")
        print(f"   objetivo_total: {objetivo_total} (tipo: {type(objetivo_total)})")
        print(f"   projetado_acumulado: {projetado_acumulado} (tipo: {type(projetado_acumulado)})")
        print(f"   meta_eoy_col: {meta_eoy_col} (tipo: {type(meta_eoy_col)})")
        print(f"   threshold_ano_col: {threshold_ano_col} (tipo: {type(threshold_ano_col)})")
        
        print(f"\n🎨 Valores formatados:")
        print(f"   meta_eoy_col formatado: {formatar_valor_curto(meta_eoy_col)}")
        print(f"   threshold_ano_col formatado: {formatar_valor_curto(threshold_ano_col)}")
        
        # Valor realizado
        v_ano_col = float(mets.get("capliq_ano", {}).get("valor", 0.0) or 0.0)
        print(f"   v_ano_col (realizado): R$ {v_ano_col:,.2f}")

if __name__ == "__main__":
    testar_contexto_cards()
