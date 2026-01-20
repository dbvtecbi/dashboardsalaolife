import pandas as pd
from pathlib import Path

def verificar_calculo_projetados():
    """Verificar como os valores projetados são calculados"""
    
    print("=== VERIFICAÇÃO DE CÁLCULO DE VALORES PROJETADOS ===")
    
    # Ler o CSV
    caminho_csv = Path("DBV Capital_Positivador_MTD.csv")
    df = pd.read_csv(caminho_csv)
    
    # Converter colunas de data
    df['Data Atualização'] = pd.to_datetime(df['Data Atualização'], errors='coerce')
    
    # Filtrar dados mais recentes
    data_max = df['Data Atualização'].max()
    df_recentes = df[df['Data Atualização'] == data_max]
    
    print(f"📅 Data mais recente: {data_max.strftime('%d/%m/%Y')}")
    print(f"📊 Registros mais recentes: {len(df_recentes)}")
    
    # Converter colunas numéricas
    colunas_net = [
        'Net em M 1', 'Net Em M', 'Net Renda Fixa', 'Net Fundos Imobiliários',
        'Net Renda Variável', 'Net Fundos', 'Net Financeiro', 'Net Previdência', 'Net Outros'
    ]
    
    for col in colunas_net:
        if col in df_recentes.columns:
            df_recentes[col] = pd.to_numeric(df_recentes[col], errors='coerce').fillna(0)
    
    print(f"\n💰 Cálculo dos valores projetados mais recentes:")
    
    # Calcular totais (simulando como o dashboard faria)
    total_net_m1 = df_recentes['Net em M 1'].sum() if 'Net em M 1' in df_recentes.columns else 0
    total_net_m = df_recentes['Net Em M'].sum() if 'Net Em M' in df_recentes.columns else 0
    total_renda_fixa = df_recentes['Net Renda Fixa'].sum() if 'Net Renda Fixa' in df_recentes.columns else 0
    total_fundos_imob = df_recentes['Net Fundos Imobiliários'].sum() if 'Net Fundos Imobiliários' in df_recentes.columns else 0
    total_renda_var = df_recentes['Net Renda Variável'].sum() if 'Net Renda Variável' in df_recentes.columns else 0
    total_fundos = df_recentes['Net Fundos'].sum() if 'Net Fundos' in df_recentes.columns else 0
    total_financeiro = df_recentes['Net Financeiro'].sum() if 'Net Financeiro' in df_recentes.columns else 0
    total_previdencia = df_recentes['Net Previdência'].sum() if 'Net Previdência' in df_recentes.columns else 0
    total_outros = df_recentes['Net Outros'].sum() if 'Net Outros' in df_recentes.columns else 0
    
    print(f"Net em M 1: R$ {total_net_m1:,.2f}")
    print(f"Net Em M: R$ {total_net_m:,.2f}")
    print(f"Net Renda Fixa: R$ {total_renda_fixa:,.2f}")
    print(f"Net Fundos Imobiliários: R$ {total_fundos_imob:,.2f}")
    print(f"Net Renda Variável: R$ {total_renda_var:,.2f}")
    print(f"Net Fundos: R$ {total_fundos:,.2f}")
    print(f"Net Financeiro: R$ {total_financeiro:,.2f}")
    print(f"Net Previdência: R$ {total_previdencia:,.2f}")
    print(f"Net Outros: R$ {total_outros:,.2f}")
    
    # Calcular possíveis totais para "Rumo a 1bi" e "AUC-2026"
    print(f"\n🎯 Possíveis cálculos para metas:")
    
    # Possível cálculo 1: Soma de todos os Net
    total_geral_1 = total_net_m1 + total_renda_fixa + total_fundos_imob + total_renda_var + total_fundos + total_financeiro + total_previdencia + total_outros
    print(f"Soma todos os Net (exceto Net Em M): R$ {total_geral_1:,.2f}")
    
    # Possível cálculo 2: Net Em M + outros componentes
    total_geral_2 = total_net_m + total_renda_fixa + total_fundos_imob + total_renda_var + total_fundos + total_financeiro + total_previdencia + total_outros
    print(f"Net Em M + outros: R$ {total_geral_2:,.2f}")
    
    # Possível cálculo 3: Apenas Net Em M
    print(f"Apenas Net Em M: R$ {total_net_m:,.2f}")
    
    # Verificar valores individuais máximos
    print(f"\n📈 Valores máximos individuais:")
    for col in colunas_net:
        if col in df_recentes.columns:
            max_val = df_recentes[col].max()
            print(f"{col}: R$ {max_val:,.2f}")
    
    # Verificar se há algum padrão nos dados
    print(f"\n🔍 Análise de padrões:")
    print(f"Assessores únicos: {df_recentes['Assessor'].nunique()}")
    print(f"Status únicos: {df_recentes['Status'].unique()}")
    print(f"Segmentos únicos: {df_recentes['Segmento'].unique()}")

if __name__ == "__main__":
    verificar_calculo_projetados()
