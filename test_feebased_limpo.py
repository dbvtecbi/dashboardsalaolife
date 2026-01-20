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
    
    # Calcular crescimento diário necessário
    dias_total_ano = 365
    crescimento_diario = (OBJETIVO_FINAL_FEEBASED - VALOR_INICIAL_FEEBASED) / dias_total_ano
    
    # Calcular dias decorridos desde início de 2026 até a data de referência
    inicio_2026 = pd.Timestamp(2026, 1, 1)
    if data_ref < inicio_2026:
        dias_decorridos = 0
    else:
        dias_decorridos = 0
        current_date = inicio_2026
        while current_date <= data_ref:
            dias_decorridos += 1
            current_date += pd.Timedelta(days=1)
    
    # Calcular valor projetado
    threshold_ano = VALOR_INICIAL_FEEBASED + (crescimento_diario * dias_decorridos)
    threshold_ano = min(threshold_ano, OBJETIVO_FINAL_FEEBASED)
    
    return {
        'threshold': threshold_ano,
        'dias_decorridos': dias_decorridos,
        'crescimento_diario': crescimento_diario
    }

# Testar com data de 16/01/2026 (antiga data fixa)
data_16_jan = pd.Timestamp(2026, 1, 16)
resultado_16 = calcular_feebased_projetado(data_16_jan)

print("=== VERIFICAÇÃO FEEBASED ===")
print(f"Data: 16/01/2026")
print(f"Dias decorridos: {resultado_16['dias_decorridos']}")
print(f"Crescimento diário: R$ {resultado_16['crescimento_diario']:,.2f}")
print(f"Valor projetado: R$ {resultado_16['threshold']:,.2f}")
print()

# Fórmula manual para verificação
crescimento_total = 200_000_000 - 119_358_620
crescimento_diario_manual = crescimento_total / 365
valor_projetado_manual = 119_358_620 + (crescimento_diario_manual * 16)

print("=== VERIFICAÇÃO MANUAL ===")
print(f"Crescimento total necessário: R$ {crescimento_total:,.2f}")
print(f"Crescimento diário (manual): R$ {crescimento_diario_manual:,.2f}")
print(f"Valor projetado (manual): R$ {valor_projetado_manual:,.2f}")
print()

print("=== COMPARAÇÃO ===")
print(f"Valor projetado (código): R$ {resultado_16['threshold']:,.2f}")
print(f"Valor projetado (manual):  R$ {valor_projetado_manual:,.2f}")
print(f"Diferença: R$ {abs(resultado_16['threshold'] - valor_projetado_manual):,.2f}")
print(f"Os valores batem? {'SIM' if abs(resultado_16['threshold'] - valor_projetado_manual) < 0.01 else 'NÃO'}")
