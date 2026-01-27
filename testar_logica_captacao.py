from correcao_final import obter_dados_captacao_mes_robusto, obter_dados_captacao_ano_robusto
from datetime import datetime

def testar_logica_captacao():
    """Testa a nova lógica de captação com diferentes datas"""
    
    print("🧪 Testando nova lógica de captação...")
    
    # Datas de teste
    datas_teste = [
        datetime(2026, 1, 5),   # 05/01/2026
        datetime(2026, 1, 15),  # 15/01/2026  
        datetime(2026, 1, 25),  # 25/01/2026
        datetime(2026, 1, 31),  # 31/01/2026
    ]
    
    for data in datas_teste:
        print(f"\n📅 Data: {data.strftime('%d/%m/%Y')}")
        
        # Testar captação mensal
        obj_mes, proj_mes = obter_dados_captacao_mes_robusto(None, data)
        print(f"   📊 Mês - Objetivo: R$ {obj_mes:,.2f}")
        print(f"   📊 Mês - Projetado: R$ {proj_mes:,.2f}")
        
        # Testar captação anual
        obj_ano, proj_ano = obter_dados_captacao_ano_robusto(None, data)
        print(f"   📊 Ano - Objetivo: R$ {obj_ano:,.2f}")
        print(f"   📊 Ano - Projetado: R$ {proj_ano:,.2f}")

if __name__ == "__main__":
    testar_logica_captacao()
