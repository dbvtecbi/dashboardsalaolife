import pandas as pd
from datetime import date

def testar_nova_logica():
    """Testar a nova lógica de período"""
    
    print("=== TESTE DA NOVA LÓGICA DE PERÍODO ===")
    
    # Simular data de atualização
    data_atualizacao = "Dezembro/2025"
    
    # Converter do formato "Mês/Ano" para datetime
    month_names_pt = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6,
        "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    
    # Parse do formato "Dezembro/2025"
    if "/" in data_atualizacao:
        mes_str, ano_str = data_atualizacao.split("/")
        mes_num = month_names_pt.get(mes_str, 12)
        ano_num = int(ano_str)
        data_referencia = pd.Timestamp(ano_num, mes_num, 1)
        print(f"Data de referência: {data_referencia.strftime('%d/%m/%Y')}")
    
    per = data_referencia.to_period("M")
    di = date(per.year, per.month, 1)
    df_ = date(per.year, per.month, pd.Timestamp(per.year, per.month, 1).days_in_month)
    
    print(f"Período: {di.strftime('%d/%m/%Y')} a {df_.strftime('%d/%m/%Y')}")
    
    # Dicionário com os nomes dos meses em português
    month_names_pt_abr = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }
    month_year = f"{month_names_pt_abr[per.month]}/{per.year}"
    print(f"Label do mês: {month_year}")
    
    return di, df_, month_year

if __name__ == "__main__":
    di, df_, month_year = testar_nova_logica()
    print(f"\nResultado: {di} a {df_} -> {month_year}")
