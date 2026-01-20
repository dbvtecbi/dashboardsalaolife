import sqlite3
import pandas as pd
from pathlib import Path

def debug_meta_2026():
    """Debug para verificar se meta_2026 está sendo obtida corretamente"""
    
    print("=== DEBUG META 2026 ===")
    
    # Testar a função obter_meta_objetivo
    from pages.Dashboard_Salão_Atualizado import obter_meta_objetivo
    
    try:
        meta_2026 = obter_meta_objetivo(2026, "auc_objetivo_ano", 694_000_000.0)
        print(f"meta_2026 obtida: R$ {meta_2026:,.2f}")
        
        # Verificar diretamente no banco
        caminho_db = Path("DBV Capital_Objetivos.db")
        conn = sqlite3.connect(str(caminho_db))
        df = pd.read_sql_query('SELECT * FROM objetivos', conn)
        conn.close()
        
        # Encontrar linha para 2026
        row_2026 = df.loc[df["col_0"] == "2026"]
        if not row_2026.empty and len(row_2026.columns) > 3:
            valor_banco = float(row_2026.iloc[0][3])  # col_3 = "AUC Objetivo"
            print(f"valor no banco (AUC Objetivo): R$ {valor_banco:,.2f}")
            
            if abs(meta_2026 - valor_banco) > 0.01:
                print(f"❌ Diferença detectada: R$ {abs(meta_2026 - valor_banco):,.2f}")
            else:
                print(f"✅ Valores consistentes")
        else:
            print("❌ Não foi possível encontrar o valor no banco")
            
    except Exception as e:
        print(f"❌ Erro no debug: {e}")

if __name__ == "__main__":
    debug_meta_2026()
