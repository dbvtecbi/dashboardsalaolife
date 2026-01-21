import pandas as pd
import sqlite3
import os
from pathlib import Path

def convert_excel_to_csv_and_db():
    """
    Converte arquivo Excel para CSV e depois para SQLite DB
    Mantendo todas as colunas e linhas originais
    """
    
    # Caminhos dos arquivos
    excel_file = "DBV Capital_Positivador (MTD).xlsx"
    csv_file = "DBV Capital_Positivador (MTD).csv"
    db_file = "DBV Capital_Positivador (MTD).db"
    
    print(f"Convertendo {excel_file}...")
    
    try:
        # Passo 1: Ler arquivo Excel mantendo todas as abas/planilhas
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        print(f"Planilhas encontradas: {list(excel_data.keys())}")
        
        # Passo 2: Converter para CSV (se houver múltiplas planilhas, salvar todas)
        if len(excel_data) == 1:
            # Se tiver apenas uma planilha
            sheet_name = list(excel_data.keys())[0]
            df = excel_data[sheet_name]
            
            # Salvar CSV mantendo todas as colunas e linhas
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"CSV salvo: {csv_file}")
            print(f"Dimensões: {df.shape[0]} linhas, {df.shape[1]} colunas")
            print(f"Colunas: {list(df.columns)}")
            
            # Passo 3: Converter para SQLite
            conn = sqlite3.connect(db_file)
            
            # Salvar no banco de dados mantendo estrutura original
            df.to_sql('positivador_mtd', conn, if_exists='replace', index=False)
            
            # Verificar dados salvos
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM positivador_mtd")
            row_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA table_info(positivador_mtd)")
            columns_info = cursor.fetchall()
            
            print(f"DB criado: {db_file}")
            print(f"Linhas no DB: {row_count}")
            print(f"Colunas no DB: {[col[1] for col in columns_info]}")
            
            conn.close()
            
        else:
            # Se tiver múltiplas planilhas
            print("Múltiplas planilhas encontradas. Processando cada uma...")
            
            for sheet_name, df in excel_data.items():
                # Nome seguro para arquivos
                safe_sheet_name = sheet_name.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
                sheet_csv = f"DBV Capital_Positivador (MTD)_{safe_sheet_name}.csv"
                
                # Salvar CSV da planilha
                df.to_csv(sheet_csv, index=False, encoding='utf-8-sig')
                print(f"CSV salvo: {sheet_csv} ({df.shape[0]} linhas, {df.shape[1]} colunas)")
            
            # Para múltiplas planilhas, criar DB com todas
            conn = sqlite3.connect(db_file)
            
            for sheet_name, df in excel_data.items():
                safe_sheet_name = sheet_name.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
                table_name = f"positivador_mtd_{safe_sheet_name}"
                
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"Tabela '{table_name}' criada no DB com {df.shape[0]} linhas")
            
            conn.close()
            print(f"DB criado: {db_file}")
        
        print("\n✅ Conversão concluída com sucesso!")
        print(f"Arquivos gerados:")
        if os.path.exists(csv_file):
            print(f"  - CSV: {csv_file} ({os.path.getsize(csv_file):,} bytes)")
        print(f"  - DB: {db_file} ({os.path.getsize(db_file):,} bytes)")
        
    except Exception as e:
        print(f"❌ Erro durante conversão: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    convert_excel_to_csv_and_db()
