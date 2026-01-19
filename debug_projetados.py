import pandas as pd
from datetime import datetime

def calcular_dias_uteis_corrigido(ano: int) -> int:
    """
    Calcula o número de dias úteis em um ano, excluindo fins de semana.
    """
    try:
        # Criar range de datas para o ano
        start_date = pd.Timestamp(ano, 1, 1)
        end_date = pd.Timestamp(ano, 12, 31)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Contar apenas dias de semana (Segunda a Sexta)
        dias_uteis = 0
        for date in date_range:
            if date.weekday() < 5:  # 0=Segunda, 4=Sexta
                dias_uteis += 1
        
        return dias_uteis
    except Exception as e:
        print(f"Erro: {e}")
        # Fallback: estimativa aproximada (52 semanas * 5 dias úteis)
        return 260

def contar_dias_uteis_decorridos(inicio: pd.Timestamp, data_ref: pd.Timestamp) -> int:
    """
    Conta apenas dias úteis decorridos entre duas datas
    """
    if data_ref < inicio:
        return 0
    
    dias_uteis_decorridos = 0
    current_date = inicio
    while current_date <= data_ref:
        if current_date.weekday() < 5:  # Segunda a Sexta
            dias_uteis_decorridos += 1
        current_date += pd.Timedelta(days=1)
    
    return dias_uteis_decorridos

def testar_calculos():
    print("=== TESTE DE CÁLCULOS PROJETADOS ===\n")
    
    # Testar dias úteis
    dias_uteis_2026 = calcular_dias_uteis_corrigido(2026)
    print(f"Dias úteis em 2026: {dias_uteis_2026}")
    
    dias_uteis_2027 = calcular_dias_uteis_corrigido(2027)
    print(f"Dias úteis em 2027: {dias_uteis_2027}")
    print(f"Total dias úteis (2026+2027): {dias_uteis_2026 + dias_uteis_2027}\n")
    
    # Testar datas
    data_atual = pd.Timestamp.now()
    inicio_2026 = pd.Timestamp(2026, 1, 1)
    
    print(f"Data atual: {data_atual.strftime('%d/%m/%Y')}")
    print(f"Início 2026: {inicio_2026.strftime('%d/%m/%Y')}")
    
    # Se estamos em 2025, usar uma data de teste em 2026
    if data_atual.year < 2026:
        data_teste = pd.Timestamp(2026, 1, 31)  # 31 de janeiro de 2026
        print(f"Data de teste (já que estamos em 2025): {data_teste.strftime('%d/%m/%Y')}")
        dias_decorridos = contar_dias_uteis_decorridos(inicio_2026, data_teste)
    else:
        dias_decorridos = contar_dias_uteis_decorridos(inicio_2026, data_atual)
    
    print(f"Dias úteis decorridos: {dias_decorridos}\n")
    
    # Testar cálculo AUC 2026
    auc_initial = 340_603_335.84  # Valor base dos dados
    meta_2026 = 560_217_582.04    # Meta do arquivo
    
    crescimento_diario = (meta_2026 - auc_initial) / dias_uteis_2026
    print(f"=== CÁLCULO AUC 2026 ===")
    print(f"AUC Inicial: R$ {auc_initial:,.2f}")
    print(f"Meta 2026: R$ {meta_2026:,.2f}")
    print(f"Gap: R$ {meta_2026 - auc_initial:,.2f}")
    print(f"Crescimento diário necessário: R$ {crescimento_diario:,.2f}")
    
    # Calcular valor projetado
    if data_atual.year < 2026:
        valor_projetado = auc_initial + (crescimento_diario * dias_decorridos)
    else:
        valor_projetado = auc_initial + (crescimento_diario * dias_decorridos)
    
    print(f"Valor projetado: R$ {valor_projetado:,.2f}")
    print(f"% da meta: {(valor_projetado / meta_2026) * 100:.2f}%\n")
    
    # Testar cálculo Rumo 1bi
    objetivo_final = 1_000_000_000.0
    dias_uteis_total = dias_uteis_2026 + dias_uteis_2027
    crescimento_diario_1bi = (objetivo_final - auc_initial) / dias_uteis_total
    
    print(f"=== CÁLCULO RUMO 1BI ===")
    print(f"Objetivo Final: R$ {objetivo_final:,.2f}")
    print(f"Dias úteis total (2026+2027): {dias_uteis_total}")
    print(f"Crescimento diário necessário: R$ {crescimento_diario_1bi:,.2f}")
    
    valor_projetado_1bi = auc_initial + (crescimento_diario_1bi * dias_decorridos)
    print(f"Valor projetado: R$ {valor_projetado_1bi:,.2f}")
    print(f"% do objetivo: {(valor_projetado_1bi / objetivo_final) * 100:.2f}%\n")
    
    # Testar cálculo FeeBased
    objetivo_feebased = 200_000_000.0
    valor_inicial_feebased = 119_800_000.0
    crescimento_diario_feebased = (objetivo_feebased - valor_inicial_feebased) / dias_uteis_2026
    
    print(f"=== CÁLCULO FEEBASED ===")
    print(f"Objetivo Final: R$ {objetivo_feebased:,.2f}")
    print(f"Valor Inicial: R$ {valor_inicial_feebased:,.2f}")
    print(f"Gap: R$ {objetivo_feebased - valor_inicial_feebased:,.2f}")
    print(f"Crescimento diário necessário: R$ {crescimento_diario_feebased:,.2f}")
    
    valor_projetado_feebased = valor_inicial_feebased + (crescimento_diario_feebased * dias_decorridos)
    print(f"Valor projetado: R$ {valor_projetado_feebased:,.2f}")
    print(f"% do objetivo: {(valor_projetado_feebased / objetivo_feebased) * 100:.2f}%")

if __name__ == "__main__":
    testar_calculos()
