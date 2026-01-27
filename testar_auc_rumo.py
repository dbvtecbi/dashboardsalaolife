from correcao_final import obter_dados_auc_2026_robusto, obter_dados_rumo_1bi_robusto
from datetime import datetime

def testar_auc_rumo():
    """Testa as funções corrigidas de AUC-2026 e Rumo a 1bi"""
    
    print("🧪 Testando AUC-2026 e Rumo a 1bi com nova lógica...")
    
    # Datas de teste
    datas_teste = [
        datetime(2026, 1, 5),   # 05/01/2026
        datetime(2026, 1, 15),  # 15/01/2026  
        datetime(2026, 1, 25),  # 25/01/2026
        datetime(2026, 1, 31),  # 31/01/2026
    ]
    
    for data in datas_teste:
        print(f"\n📅 Data: {data.strftime('%d/%m/%Y')}")
        
        # Testar AUC-2026
        obj_auc, proj_auc = obter_dados_auc_2026_robusto(None, data)
        print(f"   📊 AUC-2026 - Objetivo: R$ {obj_auc:,.2f}")
        print(f"   📊 AUC-2026 - Projetado: R$ {proj_auc:,.2f}")
        
        # Testar Rumo a 1bi
        obj_rumo, proj_rumo = obter_dados_rumo_1bi_robusto(None, data)
        print(f"   📊 Rumo 1bi - Objetivo: R$ {obj_rumo:,.2f}")
        print(f"   📊 Rumo 1bi - Projetado: R$ {proj_rumo:,.2f}")
        
        # Verificar se os projetados são iguais (usam mesma coluna)
        if proj_auc == proj_rumo:
            print(f"   ✅ Projetados iguais (usam mesma coluna AUC Acumulado)")
        else:
            print(f"   ❌ Projetados diferentes!")

if __name__ == "__main__":
    testar_auc_rumo()
