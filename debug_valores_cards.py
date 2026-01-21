"""
Debug para verificar por que os valores dos cards estão incorretos
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Simular contexto básico
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

# Importar funções
sys.path.append(str(Path(__file__).parent))
from correcao_final import (
    carregar_dados_objetivos_pj1_robusto,
    obter_dados_captacao_mes_robusto,
    obter_dados_captacao_ano_robusto,
    obter_dados_auc_2026_robusto
)

def debugar_cards():
    print("🔍 DEBUG DOS VALORES DOS CARDS")
    print("=" * 60)
    
    # Carregar dados
    df = carregar_dados_objetivos_pj1_robusto()
    if df is None:
        print("❌ Falha ao carregar dados")
        return
    
    print(f"✅ Dados carregados: {len(df)} registros")
    print(f"   Colunas: {list(df.columns)}")
    print(f"   Período: {df['Data'].min().strftime('%d/%m/%Y')} a {df['Data'].max().strftime('%d/%m/%Y')}")
    
    # Data de referência (simulando a do dashboard)
    data_ref = datetime(2026, 1, 19)
    print(f"\n📅 Data de referência: {data_ref.strftime('%d/%m/%Y')}")
    
    print("\n" + "="*40)
    print("📊 CAPTAÇÃO LÍQUIDA MÊS")
    print("="*40)
    
    # Verificar passo a passo
    print("\n1. Chamando obter_dados_captacao_mes_robusto...")
    obj_total_mes, proj_mes = obter_dados_captacao_mes_robusto(df, data_ref)
    print(f"   Retorno: objetivo={obj_total_mes}, projetado={proj_mes}")
    
    # Verificação manual
    print("\n2. Verificação manual...")
    
    # Filtrar mês
    df_mes = df[(df['Data'].dt.year == data_ref.year) & (df['Data'].dt.month == data_ref.month)]
    print(f"   Registros no mês: {len(df_mes)}")
    
    if not df_mes.empty:
        ultimo_valor = float(df_mes['Cap Acumulado'].iloc[-1])
        print(f"   Último valor do mês (Cap Acumulado): R$ {ultimo_valor:,.2f}")
        
        # Filtrar até data
        df_ate_data = df[df['Data'] <= data_ref]
        if not df_ate_data.empty:
            valor_ate_data = float(df_ate_data['Cap Acumulado'].iloc[-1])
            print(f"   Valor até {data_ref.strftime('%d/%m/%Y')} (Cap Acumulado): R$ {valor_ate_data:,.2f}")
        else:
            print("   ❌ Nenhum registro até a data de referência")
    else:
        print("   ❌ Nenhum registro no mês")
    
    print("\n" + "="*40)
    print("📊 CAPTAÇÃO LÍQUIDA ANO")
    print("="*40)
    
    obj_total_ano, proj_ano = obter_dados_captacao_ano_robusto(df, data_ref)
    print(f"   Retorno: objetivo={obj_total_ano}, projetado={proj_ano}")
    
    # Verificação manual
    df_ano = df[df['Data'].dt.year == data_ref.year]
    if not df_ano.empty:
        obj_ano_manual = float(df_ano['Cap Objetivo (ano)'].iloc[0])
        print(f"   Objetivo manual (Cap Objetivo ano): R$ {obj_ano_manual:,.2f}")
    
    print("\n" + "="*40)
    print("📊 AUC - 2026")
    print("="*40)
    
    obj_total_auc, proj_auc = obter_dados_auc_2026_robusto(df, data_ref)
    print(f"   Retorno: objetivo={obj_total_auc}, projetado={proj_auc}")
    
    # Verificação manual
    if not df_ano.empty:
        obj_auc_manual = float(df_ano['AUC Objetivo (Ano)'].iloc[0])
        print(f"   Objetivo manual (AUC Objetivo Ano): R$ {obj_auc_manual:,.2f}")
    
    print("\n" + "="*60)
    print("🔍 ANÁLISE DOS PROBLEMAS")
    print("="*60)
    
    # Verificar se os valores são muito pequenos
    if obj_total_mes < 1000:
        print(f"⚠️  PROBLEMA: obj_total_mes muito pequeno: R$ {obj_total_mes:,.2f}")
    else:
        print(f"✅ obj_total_mes OK: R$ {obj_total_mes:,.2f}")
    
    if proj_mes < 1000:
        print(f"⚠️  PROBLEMA: proj_mes muito pequeno: R$ {proj_mes:,.2f}")
    else:
        print(f"✅ proj_mes OK: R$ {proj_mes:,.2f}")
    
    # Verificar se os dados estão em escala correta
    print(f"\n📈 Escala dos dados:")
    print(f"   Cap Acumulado - min: R$ {df['Cap Acumulado'].min():,.2f}, max: R$ {df['Cap Acumulado'].max():,.2f}")
    print(f"   Cap Objetivo (ano) - valor típico: R$ {df['Cap Objetivo (ano)'].iloc[0]:,.2f}")
    print(f"   AUC Acumulado - min: R$ {df['AUC Acumulado'].min():,.2f}, max: R$ {df['AUC Acumulado'].max():,.2f}")
    print(f"   AUC Objetivo (Ano) - valor típico: R$ {df['AUC Objetivo (Ano)'].iloc[0]:,.2f}")

if __name__ == "__main__":
    debugar_cards()
