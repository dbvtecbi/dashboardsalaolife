"""
Teste rápido para verificar se o KeyError foi corrigido
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    print("🔍 Teste do KeyError corrigido")
    print("=" * 50)
    
    # Importar as funções do dashboard
    try:
        from Dashboard_Salão_Atualizado import (
            carregar_dados_objetivos_pj1,
            obter_meta_objetivo,
            obter_auc_initial,
            calcular_indicadores_objetivos
        )
        print("✅ Funções importadas")
    except Exception as e:
        print(f"❌ Erro ao importar: {e}")
        return
    
    # Data de referência
    data_ref = datetime(2026, 1, 19)
    print(f"📅 Data de referência: {data_ref}")
    
    # Testar carregar dados
    try:
        df = carregar_dados_objetivos_pj1()
        if df is not None and not df.empty:
            print(f"✅ Dados carregados: {len(df)} registros")
            print(f"Colunas: {list(df.columns)}")
        else:
            print("❌ Dados não carregados")
            return
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return
    
    # Testar obter_meta_objetivo
    try:
        meta_cap = obter_meta_objetivo(2026, "cap_objetivo_ano", 0.0)
        meta_auc = obter_meta_objetivo(2026, "auc_objetivo_ano", 0.0)
        print(f"✅ Meta Captação 2026: R$ {meta_cap:,.2f}")
        print(f"✅ Meta AUC 2026: R$ {meta_auc:,.2f}")
    except Exception as e:
        print(f"❌ Erro em obter_meta_objetivo: {e}")
        return
    
    # Testar obter_auc_initial
    try:
        auc_initial = obter_auc_initial(2026)
        print(f"✅ AUC Initial 2026: R$ {auc_initial:,.2f}")
    except Exception as e:
        print(f"❌ Erro em obter_auc_initial: {e}")
        return
    
    # Testar calcular_indicadores_objetivos (simulado)
    try:
        # Criar DataFrames simulados para o teste
        df_pos_f = pd.DataFrame({
            'Data_Posicao': [data_ref],
            'cap_liq': [29600000.0],
            'auc': [474900000.0]
        })
        
        df_pos_full = pd.DataFrame({
            'Data_Posicao': [data_ref],
            'cap_liq': [29600000.0],
            'auc': [474900000.0]
        })
        
        resultado = calcular_indicadores_objetivos(
            df_pos=df_pos_f,
            df_pos_ytd=df_pos_full
        )
        
        print(f"✅ calcular_indicadores_objetivos executado")
        print(f"   - capliq_ano: {resultado.get('capliq_ano', {})}")
        print(f"   - capliq_mes: {resultado.get('capliq_mes', {})}")
        print(f"   - auc: {resultado.get('auc', {})}")
        
    except Exception as e:
        print(f"❌ Erro em calcular_indicadores_objetivos: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 Todos os testes passaram! O KeyError foi corrigido.")
    print("Agora execute: `streamlit run Home.py` para testar o dashboard.")

if __name__ == "__main__":
    main()
