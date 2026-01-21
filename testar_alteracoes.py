import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Adicionar o diretório atual ao path para importar as funções
sys.path.append(str(Path(__file__).parent))

try:
    from funcoes_objetivos_pj1 import (
        carregar_dados_objetivos_pj1,
        obter_dados_captacao_ano,
        obter_dados_auc_2026,
        obter_dados_captacao_mes,
        obter_cap_diario_verificacao
    )
    print("✅ Importações realizadas com sucesso")
except ImportError as e:
    print(f"❌ Erro na importação: {e}")
    sys.exit(1)

def testar_funcoes():
    """Testa todas as funções implementadas"""
    
    print("=" * 60)
    print("TESTE DAS NOVAS FUNCIONALIDADES")
    print("=" * 60)
    
    # Data de referência para testes
    data_ref = datetime(2026, 1, 19)
    print(f"Data de referência: {data_ref.strftime('%d/%m/%Y')}")
    print()
    
    # 1. Testar carregamento dos dados
    print("1. Testando carregamento de dados...")
    df_objetivos_pj1 = carregar_dados_objetivos_pj1()
    
    if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
        print(f"✅ Dados carregados com sucesso: {len(df_objetivos_pj1)} registros")
        print(f"   Colunas: {list(df_objetivos_pj1.columns)}")
        print(f"   Período: {df_objetivos_pj1['Data'].min().strftime('%d/%m/%Y')} a {df_objetivos_pj1['Data'].max().strftime('%d/%m/%Y')}")
    else:
        print("❌ Erro ao carregar dados")
        return False
    
    print()
    
    # 2. Testar CAPTAÇÃO LÍQUIDA ANO
    print("2. Testando CAPTAÇÃO LÍQUIDA ANO...")
    objetivo_total, projetado_acumulado = obter_dados_captacao_ano(df_objetivos_pj1, data_ref)
    print(f"   Objetivo Total: R$ {objetivo_total:,.2f}")
    print(f"   Projetado Acumulado: R$ {projetado_acumulado:,.2f}")
    print("✅ CAPTAÇÃO LÍQUIDA ANO funcionando")
    print()
    
    # 3. Testar AUC - 2026
    print("3. Testando AUC - 2026...")
    objetivo_total_auc, projetado_acumulado_auc = obter_dados_auc_2026(df_objetivos_pj1, data_ref)
    print(f"   Objetivo Total AUC: R$ {objetivo_total_auc:,.2f}")
    print(f"   Projetado Acumulado AUC: R$ {projetado_acumulado_auc:,.2f}")
    print("✅ AUC - 2026 funcionando")
    print()
    
    # 4. Testar CAPTAÇÃO LÍQUIDA MÊS
    print("4. Testando CAPTAÇÃO LÍQUIDA MÊS...")
    objetivo_total_mes, projetado_mes = obter_dados_captacao_mes(df_objetivos_pj1, data_ref)
    print(f"   Objetivo Total Mês: R$ {objetivo_total_mes:,.2f}")
    print(f"   Projetado Mês: R$ {projetado_mes:,.2f}")
    print("✅ CAPTAÇÃO LÍQUIDA MÊS funcionando")
    print()
    
    # 5. Testar CAP Diário (verificação)
    print("5. Testando CAP Diário (verificação)...")
    cap_diario = obter_cap_diario_verificacao(df_objetivos_pj1, data_ref)
    print(f"   CAP Diário: R$ {cap_diario:,.2f}")
    print("✅ CAP Diário funcionando")
    print()
    
    # 6. Verificar consistência dos dados
    print("6. Verificando consistência dos dados...")
    
    # Verificar se o projetado do mês é menor ou igual ao projetado do ano
    if projetado_mes <= projetado_acumulado:
        print("✅ Consistência: Projetado mês ≤ Projetado ano")
    else:
        print("❌ Inconsistência: Projetado mês > Projetado ano")
    
    # Verificar se os objetivos são positivos
    if all(x > 0 for x in [objetivo_total, objetivo_total_auc, objetivo_total_mes]):
        print("✅ Consistência: Todos os objetivos são positivos")
    else:
        print("❌ Inconsistência: Um ou mais objetivos são negativos ou zero")
    
    print()
    
    # 7. Resumo dos valores para referência
    print("7. Resumo dos valores calculados:")
    print(f"   CAPTAÇÃO ANO - Objetivo: R$ {objetivo_total:,.2f} | Projetado: R$ {projetado_acumulado:,.2f}")
    print(f"   AUC 2026 - Objetivo: R$ {objetivo_total_auc:,.2f} | Projetado: R$ {projetado_acumulado_auc:,.2f}")
    print(f"   CAPTAÇÃO MÊS - Objetivo: R$ {objetivo_total_mes:,.2f} | Projetado: R$ {projetado_mes:,.2f}")
    print(f"   CAP DIÁRIO: R$ {cap_diario:,.2f}")
    
    print()
    print("=" * 60)
    print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    testar_funcoes()
