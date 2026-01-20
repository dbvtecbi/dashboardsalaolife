import pandas as pd
from pathlib import Path

def verificar_dados_excel():
    """Verificar os dados do Excel para identificar problemas"""
    
    caminho_excel = Path("DBV Capital_Produtos.xlsx")
    
    print("=== VERIFICAÇÃO DOS DADOS DO EXCEL ===")
    
    # Ler a planilha
    df = pd.read_excel(str(caminho_excel), sheet_name="Produtos")
    
    print(f"Total de registros: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    
    # Verificar cada coluna
    for col in df.columns:
        print(f"\n--- Coluna: {col} ---")
        print(f"Tipo: {df[col].dtype}")
        
        if df[col].dtype in ['int64', 'float64']:
            print(f"Valor mínimo: {df[col].min()}")
            print(f"Valor máximo: {df[col].max()}")
            
            # Verificar valores muito grandes
            max_val = df[col].max()
            if pd.notna(max_val):
                try:
                    int_val = int(max_val)
                    print(f"Valor máximo como int: {int_val}")
                    print(f"Limite SQLite INTEGER: {2**63 - 1}")
                    if abs(int_val) > 2**63 - 1:
                        print(f"⚠️ VALOR MUITO GRANDE DETECTADO!")
                except (OverflowError, ValueError):
                    print(f"⚠️ ERRO NA CONVERSÃO PARA INT!")
        
        # Mostrar alguns exemplos
        print(f"Primeiros 5 valores: {df[col].head().tolist()}")
        print(f"Valores únicos (primeiros 10): {df[col].dropna().unique()[:10].tolist()}")

if __name__ == "__main__":
    verificar_dados_excel()
