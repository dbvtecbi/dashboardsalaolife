import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Simular o contexto do Streamlit
class MockStreamlit:
    def error(self, msg):
        print(f"ERROR: {msg}")
    def warning(self, msg):
        print(f"WARNING: {msg}")
    def cache_data(self, show_spinner=True):
        def decorator(func):
            return func
        return decorator
    
    class cache_data:
        def __init__(self, show_spinner=True):
            self.show_spinner = show_spinner
        
        def __call__(self, func):
            return func

# Substituir st pelo mock
sys.modules['streamlit'] = MockStreamlit()

# Agora importar as funções
sys.path.append(str(Path(__file__).parent))

from funcoes_objetivos_pj1 import (
    carregar_dados_objetivos_pj1,
    obter_dados_captacao_mes,
    obter_dados_captacao_ano,
    obter_dados_auc_2026
)

print("🧪 Teste no Contexto do Dashboard")
print("=" * 50)

# Simular data_ref como no dashboard (vinda do banco de dados)
data_ref = pd.Timestamp("2026-01-19").normalize()
print(f"📅 data_ref: {data_ref} (tipo: {type(data_ref)})")

print("\n1. Carregando dados...")
df_objetivos_pj1 = carregar_dados_objetivos_pj1()

if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
    print(f"✅ Dados carregados: {len(df_objetivos_pj1)} registros")
    print(f"   Colunas: {list(df_objetivos_pj1.columns)}")
    
    print("\n2. Testando CAPTAÇÃO LÍQUIDA MÊS (onde ocorre o erro)...")
    try:
        objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
        print(f"✅ CAPTAÇÃO MÊS: Objetivo={objetivo_total_mes:,.2f}, Projetado={projetado_mes:,.2f}")
    except Exception as e:
        print(f"❌ Erro em CAPTAÇÃO MÊS: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testando outros cards...")
    try:
        objetivo_total, projetado_acumulado = obter_dados_captacao_ano(df_objetivos_pj1, data_ref)
        print(f"✅ CAPTAÇÃO ANO: Objetivo={objetivo_total:,.2f}, Projetado={projetado_acumulado:,.2f}")
    except Exception as e:
        print(f"❌ Erro em CAPTAÇÃO ANO: {e}")
    
    try:
        objetivo_total_auc, projetado_acumulado_auc = obter_dados_auc_2026(df_objetivos_pj1, data_ref)
        print(f"✅ AUC 2026: Objetivo={objetivo_total_auc:,.2f}, Projetado={projetado_acumulado_auc:,.2f}")
    except Exception as e:
        print(f"❌ Erro em AUC 2026: {e}")
        
else:
    print("❌ Falha ao carregar dados")

print("\n" + "=" * 50)
print("🏁 Teste Final Concluído")
