#!/usr/bin/env python3
"""
Script para testar e validar os cálculos do FeeBased
"""

import pandas as pd
from datetime import datetime

def calcular_feebased_projetado(data_ref):
    """
    Reproduz exatamente a lógica do cálculo do FeeBased no dashboard
    """
    # Valores definidos conforme solicitação
    OBJETIVO_FINAL_FEEBASED = 200_000_000.0  # 200 milhões
    VALOR_INICIAL_FEEBASED = 119_358_620.0  # Valor inicial fixo
    
    print(f"=== CÁLCULO FEEBASED ===")
    print(f"Data de Referência: {data_ref}")
    print(f"Valor Inicial: R$ {VALOR_INICIAL_FEEBASED:,.2f}")
    print(f"Objetivo Final: R$ {OBJETIVO_FINAL_FEEBASED:,.2f}")
    print()
    
    # Calcular crescimento diário necessário (mesma lógica do Rumo a 1bi)
    dias_total_ano = 365
    crescimento_diario = (OBJETIVO_FINAL_FEEBASED - VALOR_INICIAL_FEEBASED) / dias_total_ano if dias_total_ano > 0 else 0
    
    print(f"Crescimento diário necessário: R$ {crescimento_diario:,.2f}")
    print(f"Crescimento total necessário: R$ {OBJETIVO_FINAL_FEEBASED - VALOR_INICIAL_FEEBASED:,.2f}")
    print()
    
    # Calcular dias decorridos desde início de 2026 até a data de referência
    inicio_2026 = pd.Timestamp(2026, 1, 1)
    if data_ref < inicio_2026:
        dias_decorridos = 0
    else:
        # Contar TODOS os dias do ano (365 dias), não apenas úteis
        dias_decorridos = 0
        current_date = inicio_2026
        while current_date <= data_ref:
            # Contar todos os dias (incluindo fins de semana)
            dias_decorridos += 1
            current_date += pd.Timedelta(days=1)
    
    print(f"Dias decorridos desde 01/01/2026: {dias_decorridos}")
    
    # Calcular valor projetado (mesma lógica dos outros cards)
    threshold_ano = VALOR_INICIAL_FEEBASED + (crescimento_diario * dias_decorridos)
    threshold_ano = min(threshold_ano, OBJETIVO_FINAL_FEEBASED)
    
    print(f"Valor projetado (threshold): R$ {threshold_ano:,.2f}")
    print(f"Percentual do objetivo: {(threshold_ano / OBJETIVO_FINAL_FEEBASED) * 100:.2f}%")
    print()
    
    # Calcular dias restantes
    fim_2026 = pd.Timestamp(2026, 12, 31)
    dias_restantes = max(0, (fim_2026 - data_ref).days)
    print(f"Dias restantes até 31/12/2026: {dias_restantes}")
    
    return {
        'threshold_ano': threshold_ano,
        'dias_decorridos': dias_decorridos,
        'dias_restantes': dias_restantes,
        'crescimento_diario': crescimento_diario
    }

def testar_varias_datas():
    """
    Testa o cálculo com várias datas de referência
    """
    # Testar com algumas datas específicas
    datas_teste = [
        pd.Timestamp(2026, 1, 16),  # Data que estava sendo usada antes
        pd.Timestamp(2026, 1, 31),  # Final de janeiro
        pd.Timestamp(2026, 6, 30),  # Meio do ano
        pd.Timestamp(2026, 12, 31), # Final do ano
        pd.Timestamp(2025, 12, 31), # Antes do início
    ]
    
    for data in datas_teste:
        print("=" * 60)
        resultado = calcular_feebased_projetado(data)
        print()

if __name__ == "__main__":
    testar_varias_datas()
