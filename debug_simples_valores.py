"""
Debug simples para verificar os valores dos cards
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Mock do streamlit
class MockSt:
    def set_page_config(self, *args, **kwargs): pass
    def markdown(self, content, unsafe_allow_html=False): pass
    def cache_data(self, show_spinner=True):
        def decorator(func): return func
        return decorator
    class cache_data:
        def __init__(self, show_spinner=True): self.show_spinner = show_spinner
        def __call__(self, func): return func

sys.modules['streamlit'] = MockSt()

# Função de formatação simplificada
def formatar_valor_curto(valor):
    try:
        v = float(valor or 0)
    except (ValueError, TypeError):
        return "R$ 0"
    
    if v >= 1_000_000_000:
        return f"R$ {v / 1_000_000_000:,.1f}bi"
    if v >= 1_000_000:
        return f"R$ {v / 1_000_000:,.1f}M"
    if v >= 1_000:
        return f"R$ {v / 1_000:,.1f}K"
    return f"R$ {v:,.0f}"

def testar_valores():
    print("🔍 DEBUG SIMPLES DOS VALORES")
    print("=" * 50)
    
    # Importar funções robustas
    sys.path.append(str(Path('.').absolute()))
    from correcao_final import (
        carregar_dados_objetivos_pj1_robusto,
        obter_dados_captacao_mes_robusto,
        obter_dados_captacao_ano_robusto,
        obter_dados_auc_2026_robusto
    )
    
    # Data de referência
    data_ref = datetime(2026, 1, 19)
    print(f"📅 Data de referência: {data_ref}")
    
    # Carregar dados
    df = carregar_dados_objetivos_pj1_robusto()
    if df is None:
        print("❌ Falha ao carregar dados")
        return
    
    print(f"✅ Dados carregados: {len(df)} registros")
    
    print("\n📊 CAPTAÇÃO LÍQUIDA MÊS")
    print("-" * 30)
    obj_mes, proj_mes = obter_dados_captacao_mes_robusto(df, data_ref)
    print(f"Objetivo Total: {formatar_valor_curto(obj_mes)}")
    print(f"Projetado: {formatar_valor_curto(proj_mes)}")
    print(f"Valores brutos: obj={obj_mes}, proj={proj_mes}")
    
    print("\n📊 CAPTAÇÃO LÍQUIDA ANO")
    print("-" * 30)
    obj_ano, proj_ano = obter_dados_captacao_ano_robusto(df, data_ref)
    print(f"Objetivo Total: {formatar_valor_curto(obj_ano)}")
    print(f"Projetado: {formatar_valor_curto(proj_ano)}")
    print(f"Valores brutos: obj={obj_ano}, proj={proj_ano}")
    
    print("\n📊 AUC - 2026")
    print("-" * 30)
    obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
    print(f"Objetivo Total: {formatar_valor_curto(obj_auc)}")
    print(f"Projetado: {formatar_valor_curto(proj_auc)}")
    print(f"Valores brutos: obj={obj_auc}, proj={proj_auc}")
    
    print("\n🔍 ANÁLISE")
    print("-" * 30)
    
    # Verificar se os valores são zeros ou uns
    problemas = []
    if obj_mes == 0: problemas.append("obj_mes é 0")
    if proj_mes == 0: problemas.append("proj_mes é 0")
    if proj_mes == 1: problemas.append("proj_mes é 1")
    if obj_ano == 0: problemas.append("obj_ano é 0")
    if proj_ano == 0: problemas.append("proj_ano é 0")
    if proj_ano == 1: problemas.append("proj_ano é 1")
    
    if problemas:
        print("⚠️  PROBLEMAS ENCONTRADOS:")
        for p in problemas:
            print(f"   - {p}")
    else:
        print("✅ Nenhum problema detectado nos valores")
    
    # Verificar formatação
    print(f"\n🎨 TESTE DE FORMATAÇÃO:")
    test_values = [0, 1, 1000, 15000000, 183600000, 694000000]
    for val in test_values:
        print(f"   {val} -> {formatar_valor_curto(val)}")

if __name__ == "__main__":
    testar_valores()
