import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

def verificar_dados_dezembro():
    """Verificar dados de Auto/RE e Saúde em dezembro de 2025"""
    
    caminho_db = Path("DBV Capital_Produtos.db")
    conn = sqlite3.connect(str(caminho_db))
    
    print("=== VERIFICAÇÃO DE DADOS DE DEZEMBRO/2025 ===")
    
    # Ler todos os dados
    df = pd.read_sql_query("SELECT * FROM Produtos", conn)
    
    # Converter colunas
    df["data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["valor_negocio"] = pd.to_numeric(df["Valor Negócio (R$)"], errors="coerce").fillna(0.0)
    
    # Filtrar dezembro de 2025
    dezembro_mask = (df["data"].dt.year == 2025) & (df["data"].dt.month == 12)
    df_dezembro = df[dezembro_mask]
    
    print(f"Total de registros em dezembro/2025: {len(df_dezembro)}")
    
    # Verificar por linha de receita
    linhas_receita = df_dezembro["Linha Receita"].value_counts()
    print(f"\n📊 Registros por linha de receita em dezembro/2025:")
    for linha, count in linhas_receita.items():
        print(f"  - {linha}: {count} registros")
    
    # Verificar Auto/RE
    df_auto = df_dezembro[df_dezembro["Linha Receita"].str.contains("Auto", case=False, na=False)]
    print(f"\n🚗 Auto/RE em dezembro/2025:")
    print(f"  Registros: {len(df_auto)}")
    if not df_auto.empty:
        print(f"  Valor total: R$ {df_auto['valor_negocio'].sum():,.2f}")
        print(f"  Data mais recente: {df_auto['data'].max().strftime('%d/%m/%Y')}")
        print(f"  Primeiros registros:")
        for i, row in df_auto.head(3).iterrows():
            print(f"    {row['data'].strftime('%d/%m/%Y')} - R$ {row['valor_negocio']:,.2f} - {row['Produto']}")
    
    # Verificar Saúde
    df_saude = df_dezembro[df_dezembro["Linha Receita"].str.contains("Saúde", case=False, na=False)]
    print(f"\n🏥 Saúde em dezembro/2025:")
    print(f"  Registros: {len(df_saude)}")
    if not df_saude.empty:
        print(f"  Valor total: R$ {df_saude['valor_negocio'].sum():,.2f}")
        print(f"  Data mais recente: {df_saude['data'].max().strftime('%d/%m/%Y')}")
        print(f"  Primeiros registros:")
        for i, row in df_saude.head(3).iterrows():
            print(f"    {row['data'].strftime('%d/%m/%Y')} - R$ {row['valor_negocio']:,.2f} - {row['Produto']}")
    
    # Verificar todas as datas disponíveis para estas áreas
    print(f"\n📅 Datas disponíveis para Auto/RE:")
    df_auto_todas = df[df["Linha Receita"].str.contains("Auto", case=False, na=False)]
    if not df_auto_todas.empty:
        datas_auto = df_auto_todas["data"].dt.strftime('%Y-%m').unique()
        print(f"  Meses: {sorted(datas_auto)}")
        print(f"  Data mais recente: {df_auto_todas['data'].max().strftime('%d/%m/%Y')}")
    
    print(f"\n📅 Datas disponíveis para Saúde:")
    df_saude_todas = df[df["Linha Receita"].str.contains("Saúde", case=False, na=False)]
    if not df_saude_todas.empty:
        datas_saude = df_saude_todas["data"].dt.strftime('%Y-%m').unique()
        print(f"  Meses: {sorted(datas_saude)}")
        print(f"  Data mais recente: {df_saude_todas['data'].max().strftime('%d/%m/%Y')}")
    
    conn.close()

if __name__ == "__main__":
    verificar_dados_dezembro()
