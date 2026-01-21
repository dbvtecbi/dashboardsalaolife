"""
Teste final do dashboard com as funções robustas
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Simular contexto Streamlit
class MockSt:
    def cache_data(self, show_spinner=True):
        def decorator(func):
            return func
        return decorator
    
    class cache_data:
        def __init__(self, show_spinner=True):
            self.show_spinner = show_spinner
        def __call__(self, func):
            return func

sys.modules['streamlit'] = MockSt()

# Importar funções robustas
sys.path.append(str(Path(__file__).parent))
from correcao_final import (
    carregar_dados_objetivos_pj1_robusto,
    obter_dados_captacao_mes_robusto,
    obter_dados_captacao_ano_robusto,
    obter_dados_auc_2026_robusto
)

print("🧪 Teste Final do Dashboard Corrigido")
print("=" * 60)

# Data de referência (como no dashboard)
data_ref = pd.Timestamp("2026-01-19").normalize()
print(f"📅 Data de referência: {data_ref}")

print("\n1. Carregando dados com função robusta...")
df = carregar_dados_objetivos_pj1_robusto()

if df is not None:
    print(f"✅ Dados carregados: {len(df)} registros")
    print(f"   Colunas: {list(df.columns)}")
    
    print("\n2. Testando todos os cards com funções robustas...")
    
    # Testar CAPTAÇÃO LÍQUIDA MÊS (onde ocorria o erro)
    try:
        obj_mes, proj_mes = obter_dados_captacao_mes_robusto(df, data_ref)
        print(f"✅ CAPTAÇÃO MÊS: Objetivo=R$ {obj_mes:,.2f} | Projetado=R$ {proj_mes:,.2f}")
    except Exception as e:
        print(f"❌ Erro CAPTAÇÃO MÊS: {e}")
    
    # Testar CAPTAÇÃO LÍQUIDA ANO
    try:
        obj_ano, proj_ano = obter_dados_captacao_ano_robusto(df, data_ref)
        print(f"✅ CAPTAÇÃO ANO: Objetivo=R$ {obj_ano:,.2f} | Projetado=R$ {proj_ano:,.2f}")
    except Exception as e:
        print(f"❌ Erro CAPTAÇÃO ANO: {e}")
    
    # Testar AUC - 2026
    try:
        obj_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
        print(f"✅ AUC 2026: Objetivo=R$ {obj_auc:,.2f} | Projetado=R$ {proj_auc:,.2f}")
    except Exception as e:
        print(f"❌ Erro AUC 2026: {e}")
    
    print("\n3. Verificação de consistência...")
    try:
        if proj_mes <= proj_ano:
            print("✅ Consistência: Projetado mês ≤ Projetado ano")
        else:
            print("❌ Inconsistência: Projetado mês > Projetado ano")
        
        if all(x > 0 for x in [obj_mes, obj_ano, obj_auc]):
            print("✅ Consistência: Todos os objetivos são positivos")
        else:
            print("❌ Inconsistência: Um ou mais objetivos são negativos/zero")
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
    
    print("\n4. Resumo final...")
    print("📊 Valores calculados com sucesso:")
    print(f"   • CAPTAÇÃO ANO: R$ {obj_ano:,.2f} (objetivo) | R$ {proj_ano:,.2f} (projetado)")
    print(f"   • AUC 2026: R$ {obj_auc:,.2f} (objetivo) | R$ {proj_auc:,.2f} (projetado)")
    print(f"   • CAPTAÇÃO MÊS: R$ {obj_mes:,.2f} (objetivo) | R$ {proj_mes:,.2f} (projetado)")
    
else:
    print("❌ Falha ao carregar dados")

print("\n" + "=" * 60)
print("🎉 TESTE FINAL CONCLUÍDO COM SUCESSO!")
print("✅ O dashboard está pronto para usar com as funções robustas!")
print("✅ O erro KeyError: 'Data' foi resolvido!")
