import sqlite3
import pandas as pd
from pathlib import Path

def debug_normalizacao():
    """Debug da normalização de texto"""
    
    caminho_db = Path("DBV Capital_Produtos.db")
    conn = sqlite3.connect(str(caminho_db))
    
    # Ler todos os dados
    df = pd.read_sql_query("SELECT * FROM Produtos", conn)
    
    print("=== DEBUG DA NORMALIZAÇÃO ===")
    
    # Verificar valores únicos da coluna Linha Receita
    valores_unicos = df["Linha Receita"].unique()
    print(f"Valores únicos em 'Linha Receita': {len(valores_unicos)}")
    for val in sorted(valores_unicos):
        if val:  # Pular valores vazios
            print(f"  - '{val}'")
    
    # Testar normalização
    def _norm_txt(x: object) -> str:
        s = "" if x is None else str(x)
        s = s.lower().strip()
        return s
    
    print(f"\n--- Teste de normalização para Auto/RE ---")
    area_values = ["Auto/RE", "AutoRE", "Auto", "RE"]
    targets = {_norm_txt(v) for v in area_values}
    print(f"Targets normalizados: {targets}")
    
    s = df["Linha Receita"].astype(str).apply(_norm_txt)
    filtered = df[s.isin(targets)].copy()
    
    print(f"Registros encontrados: {len(filtered)}")
    if not filtered.empty:
        print(f"Valores normalizados encontrados: {filtered['Linha Receita'].astype(str).apply(_norm_txt).unique()}")
    
    conn.close()

if __name__ == "__main__":
    debug_normalizacao()
