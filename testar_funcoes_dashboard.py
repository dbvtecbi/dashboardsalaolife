import sys
import pandas as pd
from pathlib import Path

# Adicionar o diretório das páginas ao path
sys.path.append(str(Path(__file__).parent / "pages"))

try:
    from Dashboard_Salão_Atualizado import (
        calcular_dias_uteis,
        calcular_valor_projetado_auc_2026,
        calcular_valor_projetado_rumo_1bi,
        calcular_valor_projetado_feebased
    )
    
    print("=== TESTE DAS FUNÇÕES CORRIGIDAS ===\n")
    
    # Data de teste
    data_teste = pd.Timestamp(2026, 1, 16)  # 16/01/2026
    
    print(f"Data de teste: {data_teste.strftime('%d/%m/%Y')}")
    print()
    
    # Testar dias úteis
    dias_uteis_2026 = calcular_dias_uteis(2026)
    dias_uteis_2027 = calcular_dias_uteis(2027)
    
    print(f"Dias úteis 2026: {dias_uteis_2026}")
    print(f"Dias úteis 2027: {dias_uteis_2027}")
    print(f"Total: {dias_uteis_2026 + dias_uteis_2027}")
    print()
    
    # Testar AUC 2026
    auc_initial = 340_603_335.84
    meta_2026 = 560_217_582.04
    
    projetado_auc = calcular_valor_projetado_auc_2026(auc_initial, meta_2026, data_teste)
    print(f"=== AUC 2026 ===")
    print(f"Valor projetado: R$ {projetado_auc:,.2f}")
    print(f"% da meta: {(projetado_auc / meta_2026) * 100:.2f}%")
    print()
    
    # Testar Rumo 1BI
    projetado_1bi = calcular_valor_projetado_rumo_1bi(auc_initial, data_teste)
    print(f"=== RUMO 1BI ===")
    print(f"Valor projetado: R$ {projetado_1bi:,.2f}")
    print(f"% do objetivo: {(projetado_1bi / 1_000_000_000) * 100:.2f}%")
    print()
    
    # Testar FeeBased
    projetado_feebased = calcular_valor_projetado_feebased(data_teste)
    print(f"=== FEEBASED ===")
    print(f"Valor projetado: R$ {projetado_feebased:,.2f}")
    print(f"% do objetivo: {(projetado_feebased / 200_000_000) * 100:.2f}%")
    print()
    
    print("✅ Todas as funções executaram com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar funções: {e}")
except Exception as e:
    print(f"❌ Erro ao executar testes: {e}")
    import traceback
    traceback.print_exc()
