import pandas as pd
import sqlite3
from pathlib import Path

def converter_para_csv(excel_path, csv_path):
    # Lê o arquivo Excel
    df = pd.read_excel(excel_path, engine='openpyxl')
    # Salva como CSV
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Arquivo CSV salvo em: {csv_path}")
    return df

def converter_para_sqlite(df, db_path, table_name='nps_data'):
    # Conecta ao banco de dados SQLite
    conn = sqlite3.connect(db_path)
    # Salva o DataFrame no SQLite
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Dados salvos no banco de dados: {db_path}")
    conn.close()

def main():
    # Define os caminhos dos arquivos
    base_dir = Path(__file__).parent
    excel_path = base_dir / "DBV Capital_NPS.xlsm"
    csv_path = base_dir / "DBV_Capital_NPS.csv"
    db_path = base_dir / "DBV_Capital_NPS.db"
    
    try:
        # Converte para CSV
        df = converter_para_csv(excel_path, csv_path)
        
        # Converte para SQLite
        converter_para_sqlite(df, db_path)
        
        print("\nConversão concluída com sucesso!")
        print(f"- Arquivo CSV: {csv_path}")
        print(f"- Banco de dados SQLite: {db_path}")
        
    except Exception as e:
        print(f"\nOcorreu um erro durante a conversão: {str(e)}")

if __name__ == "__main__":
    main()
