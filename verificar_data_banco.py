#!/usr/bin/env python3
"""
Script para verificar qual data real está sendo obtida do banco de dados
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))

# Importar a função específica
import importlib.util
spec = importlib.util.spec_from_file_location("dashboard", os.path.join(os.path.dirname(__file__), 'pages', 'Dashboard_Salão_Atualizado.py'))
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)

obter_ultima_data_posicao = dashboard.obter_ultima_data_posicao

try:
    data_real = obter_ultima_data_posicao()
    print(f"Data real obtida do banco: {data_real}")
    print(f"Data formatada: {data_real.strftime('%d/%m/%Y')}")
    
    # Importar pandas para testar o cálculo com a data real
    import pandas as pd
    
    # Valores do FeeBased
    OBJETIVO_FINAL_FEEBASED = 200_000_000.0
    VALOR_INICIAL_FEEBASED = 119_358_620.0
    
    # Converter para Timestamp
    data_ref = pd.Timestamp(data_real).normalize()
    
    # Calcular dias decorridos
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
    crescimento_diario = (OBJETIVO_FINAL_FEEBASED - VALOR_INICIAL_FEEBASED) / 365
    threshold_ano = VALOR_INICIAL_FEEBASED + (crescimento_diario * dias_decorridos)
    threshold_ano = min(threshold_ano, OBJETIVO_FINAL_FEEBASED)
    
    print(f"\n=== CÁLCULO COM DATA REAL ===")
    print(f"Dias decorridos: {dias_decorridos}")
    print(f"Valor projetado: R$ {threshold_ano:,.2f}")
    
except Exception as e:
    print(f"Erro ao obter data do banco: {e}")
    print("Usando data atual como fallback...")
    from datetime import datetime
    data_real = datetime.now()
    print(f"Data atual: {data_real}")
