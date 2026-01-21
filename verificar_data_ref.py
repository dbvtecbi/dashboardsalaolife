"""
Verificar qual data_ref está sendo usada no dashboard
"""
import sys
from pathlib import Path
import pandas as pd

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / 'pages'))

def main():
    print("🔍 Verificando data_ref do dashboard")
    print("=" * 50)
    
    try:
        # Importar a função que define data_ref
        from Dashboard_Salão_Atualizado import obter_ultima_data_posicao
        
        # Obter a data real
        data_atualizacao_bd = obter_ultima_data_posicao()
        data_ref = pd.Timestamp(data_atualizacao_bd).normalize()
        
        print(f"Data de atualização do BD: {data_atualizacao_bd}")
        print(f"data_ref usada no dashboard: {data_ref}")
        print(f"Ano: {data_ref.year}")
        print(f"Mês: {data_ref.month}")
        print(f"Dia: {data_ref.day}")
        
        # Verificar se esta data existe nos dados da Objetivos_PJ1
        from correcao_final import carregar_dados_objetivos_pj1_robusto
        
        df_objetivos_pj1 = carregar_dados_objetivos_pj1()
        if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
            print(f"\n📊 Dados da Objetivos_PJ1:")
            print(f"Total de registros: {len(df_objetivos_pj1)}")
            print(f"Período: {df_objetivos_pj1['Data'].min()} a {df_objetivos_pj1['Data'].max()}")
            
            # Verificar se a data_ref existe nos dados
            data_ref_formatada = data_ref.strftime('%Y-%m-%d')
            if data_ref_formatada in df_objetivos_pj1['Data'].dt.strftime('%Y-%m-%d').values:
                print(f"✅ Data {data_ref_formatada} existe nos dados")
                
                # Mostrar os dados desta data
                dados_data = df_objetivos_pj1[df_objetivos_pj1['Data'].dt.strftime('%Y-%m-%d') == data_ref_formatada]
                print(f"Dados para {data_ref_formatada}:")
                print(dados_data[['Data', 'Cap Objetivo (ano)', 'Cap Acumulado', 'AUC Objetivo (Ano)', 'AUC Acumulado']].to_string())
            else:
                print(f"❌ Data {data_ref_formatada} NÃO existe nos dados!")
                print("Datas disponíveis:")
                datas_disponiveis = df_objetivos_pj1['Data'].dt.strftime('%Y-%m-%d').unique()[:10]
                for data in datas_disponiveis:
                    print(f"  - {data}")
        
        # Testar com a data real
        print(f"\n🧪 Testando com a data real do dashboard:")
        from correcao_final import (
            obter_dados_captacao_mes_robusto,
            obter_dados_captacao_ano_robusto,
            obter_dados_auc_2026_robusto
        )
        
        if df_objetivos_pj1 is not None and not df_objetivos_pj1.empty:
            obj_mes, proj_mes = obter_dados_captacao_mes_robusto(df_objetivos_pj1, data_ref)
            obj_ano, proj_ano = obter_dados_captacao_ano_robusto(df_objetivos_pj1, data_ref)
            obj_auc, proj_auc = obter_dados_auc_2026_robusto(df_objetivos_pj1, data_ref)
            
            print(f"CAPTAÇÃO MÊS: Objetivo R$ {obj_mes:,.2f}, Projetado R$ {proj_mes:,.2f}")
            print(f"CAPTAÇÃO ANO: Objetivo R$ {obj_ano:,.2f}, Projetado R$ {proj_ano:,.2f}")
            print(f"AUC 2026: Objetivo R$ {obj_auc:,.2f}, Projetado R$ {proj_auc:,.2f}")
            
            if obj_mes == 0 or proj_mes == 0:
                print("❌ PROBLEMA: Valores zerados com a data real!")
            else:
                print("✅ Valores corretos com a data real!")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
