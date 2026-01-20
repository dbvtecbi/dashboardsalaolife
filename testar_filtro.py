import sqlite3
import pandas as pd
from pathlib import Path
from datetime import date

def testar_filtro_areas():
    """Testar se os filtros de áreas estão funcionando corretamente"""
    
    caminho_db = Path("DBV Capital_Produtos.db")
    conn = sqlite3.connect(str(caminho_db))
    
    # Ler todos os dados
    df = pd.read_sql_query("SELECT * FROM Produtos", conn)
    
    # Converter colunas
    df["data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["valor_negocio"] = pd.to_numeric(df["Valor Negócio (R$)"], errors="coerce").fillna(0.0)
    df = df.dropna(subset=["data"]).reset_index(drop=True)
    
    print("=== TESTE DE FILTRO DE ÁREAS ===")
    print(f"Total de registros: {len(df)}")
    
    # Mapeamento de áreas (igual ao do dashboard)
    AREA_MAP = {
        "Vida": ["Vida", "Seguros", "Seguro", "Vida/Seguros", "Vida e Seguros"],
        "Auto/RE": ["Auto/RE", "AutoRE", "Auto", "RE"],
        "Saúde": ["Saúde", "Saude"],
        "Câmbio": ["Câmbio", "Cambio"],
        "Consórcio": ["Consórcio", "Consorcio"],
        "Crédito": ["Crédito", "Credito"],
    }
    
    # Testar cada área
    for area_name, area_values in AREA_MAP.items():
        print(f"\n--- Área: {area_name} ---")
        
        # Filtrar área
        targets = {str(v).lower().strip() for v in area_values}
        s = df["Linha Receita"].astype(str).str.lower().str.strip()
        filtered = df[s.isin(targets)].copy()
        
        print(f"Registros encontrados: {len(filtered)}")
        
        if not filtered.empty:
            # Verificar período (usando data mais recente)
            data_referencia = filtered["data"].max()
            per = data_referencia.to_period("M")
            di = date(per.year, per.month, 1)
            df_ = date(per.year, per.month, pd.Timestamp(per.year, per.month, 1).days_in_month)
            
            print(f"Período: {di.strftime('%d/%m/%Y')} a {df_.strftime('%d/%m/%Y')}")
            
            # Filtrar mês
            mask = (filtered["data"].dt.date >= di) & (filtered["data"].dt.date <= df_)
            df_mes = filtered.loc[mask]
            
            print(f"Registros no período: {len(df_mes)}")
            print(f"Valor total: R$ {df_mes['valor_negocio'].sum():,.2f}")
            
            # Mostrar algumas datas
            if not df_mes.empty:
                print(f"Datas: {sorted(df_mes['data'].dt.strftime('%d/%m/%Y').unique())}")
        else:
            print("Nenhum registro encontrado")
    
    conn.close()

if __name__ == "__main__":
    testar_filtro_areas()
