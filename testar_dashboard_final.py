import sqlite3
import pandas as pd
from pathlib import Path
from datetime import date

def testar_dashboard_final():
    """Testar como ficará o dashboard com a nova lógica"""
    
    caminho_db = Path("DBV Capital_Produtos.db")
    conn = sqlite3.connect(str(caminho_db))
    
    # Ler todos os dados
    df = pd.read_sql_query("SELECT * FROM Produtos", conn)
    
    # Converter colunas
    df["data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["valor_negocio"] = pd.to_numeric(df["Valor Negócio (R$)"], errors="coerce").fillna(0.0)
    df = df.dropna(subset=["data"]).reset_index(drop=True)
    
    print("=== SIMULAÇÃO DO DASHBOARD - DEZEMBRO/2025 ===")
    
    # Mapeamento de áreas
    AREA_MAP = {
        "Vida": ["Vida", "Seguros", "Seguro", "Vida/Seguros", "Vida e Seguros"],
        "Auto/RE": ["Auto/RE", "AutoRE", "Auto", "RE"],
        "Saúde": ["Saúde", "Saude"],
        "Câmbio": ["Câmbio", "Cambio"],
        "Consórcio": ["Consórcio", "Consorcio"],
        "Crédito": ["Crédito", "Credito"],
    }
    
    # Definir período: Dezembro/2025
    di = date(2025, 12, 1)
    df_ = date(2025, 12, 31)
    
    print(f"Período: {di.strftime('%d/%m/%Y')} a {df_.strftime('%d/%m/%Y')}")
    print()
    
    # Testar cada área
    for area_name, area_values in AREA_MAP.items():
        print(f"--- {area_name} ---")
        
        # Filtrar área
        def _norm_txt(x: object) -> str:
            s = "" if x is None else str(x)
            return s.strip().lower()
        
        targets = {_norm_txt(v) for v in area_values}
        s = df["Linha Receita"].astype(str).apply(_norm_txt)
        filtered = df[s.isin(targets)].copy()
        
        if filtered.empty:
            print("❌ Sem dados para esta área")
            print()
            continue
        
        # Filtrar período de dezembro
        mask = (filtered["data"].dt.date >= di) & (filtered["data"].dt.date <= df_)
        df_mes = filtered.loc[mask]
        
        if df_mes.empty:
            print("❌ Sem dados em dezembro/2025 (card vazio)")
            print()
            continue
        
        valor_total = float(df_mes["valor_negocio"].sum())
        qtd_total = int(df_mes.shape[0])
        
        print(f"✅ Valor: R$ {valor_total:,.2f}")
        print(f"✅ Qtd: {qtd_total}")
        print(f"📅 Datas: {sorted(df_mes['data'].dt.strftime('%d/%m/%Y').unique())}")
        print()
    
    conn.close()

if __name__ == "__main__":
    testar_dashboard_final()
