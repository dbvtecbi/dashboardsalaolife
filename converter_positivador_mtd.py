import pandas as pd
import sqlite3
import os
from pathlib import Path

def converter_positivador_mtd():
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
        # Verificar se o arquivo Excel existe
        if not os.path.exists(excel_file):
            print(f"❌ Arquivo Excel não encontrado: {excel_file}")
            return None
        
        # Passo 1: Ler arquivo Excel mantendo todas as abas/planilhas
        print("📖 Lendo arquivo Excel...")
        excel_data = pd.read_excel(excel_file, sheet_name=None)
        
        print(f"📊 Planilhas encontradas: {list(excel_data.keys())}")
        
        # Passo 2: Converter para CSV (se houver múltiplas planilhas, salvar todas)
        if len(excel_data) == 1:
            # Se tiver apenas uma planilha
            sheet_name = list(excel_data.keys())[0]
            df = excel_data[sheet_name]
            
            print(f"📋 Processando planilha: {sheet_name}")
            print(f"   - Dimensões: {df.shape[0]} linhas, {df.shape[1]} colunas")
            print(f"   - Colunas: {list(df.columns)}")
            
            # Salvar CSV mantendo todas as colunas e linhas
            print("💾 Salvando CSV...")
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"✅ CSV salvo: {csv_file}")
            
            # Passo 3: Converter para SQLite
            print("💾 Convertendo para SQLite...")
            conn = sqlite3.connect(db_file)
            
            # Salvar no banco de dados mantendo estrutura original
            df.to_sql('positivador_mtd', conn, if_exists='replace', index=False)
            
            # Verificar dados salvos
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM positivador_mtd")
            row_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA table_info(positivador_mtd)")
            columns_info = cursor.fetchall()
            
            print(f"✅ DB criado: {db_file}")
            print(f"   - Linhas no DB: {row_count}")
            print(f"   - Colunas no DB: {[col[1] for col in columns_info]}")
            
            # Verificar integridade dos dados
            if row_count == len(df) and len(columns_info) == len(df.columns):
                print("✅ Todos os dados foram preservados no banco!")
            else:
                print("⚠️  Possível perda de dados durante conversão para DB")
            
            conn.close()
            
        else:
            # Se tiver múltiplas planilhas
            print("📋 Múltiplas planilhas encontradas. Processando cada uma...")
            
            # Para múltiplas planilhas, criar DB com todas
            conn = sqlite3.connect(db_file)
            
            for sheet_name, df in excel_data.items():
                print(f"📋 Processando planilha: {sheet_name}")
                print(f"   - Dimensões: {df.shape[0]} linhas, {df.shape[1]} colunas")
                
                # Nome seguro para arquivos e tabelas
                safe_sheet_name = sheet_name.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
                sheet_csv = f"DBV Capital_Positivador (MTD)_{safe_sheet_name}.csv"
                table_name = f"positivador_mtd_{safe_sheet_name}"
                
                # Salvar CSV da planilha
                df.to_csv(sheet_csv, index=False, encoding='utf-8-sig')
                print(f"✅ CSV salvo: {sheet_csv}")
                
                # Salvar no banco de dados
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"✅ Tabela '{table_name}' criada no DB")
            
            conn.close()
            print(f"✅ DB criado: {db_file}")
        
        print("\n✅ Conversão concluída com sucesso!")
        print(f"📁 Arquivos gerados:")
        
        # Verificar arquivos criados
        if os.path.exists(csv_file):
            tamanho_csv = os.path.getsize(csv_file)
            print(f"   - CSV: {csv_file} ({tamanho_csv:,} bytes)")
        
        if os.path.exists(db_file):
            tamanho_db = os.path.getsize(db_file)
            print(f"   - DB: {db_file} ({tamanho_db:,} bytes)")
        
        # Verificação final
        print("\n🔍 Verificação final:")
        if os.path.exists(csv_file):
            df_csv = pd.read_csv(csv_file)
            print(f"   - CSV: {len(df_csv)} linhas, {len(df_csv.columns)} colunas")
        
        if os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   - DB: {len(tables)} tabela(s)")
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                rows = cursor.fetchone()[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                cols = len(cursor.fetchall())
                print(f"     • {table_name}: {rows} linhas, {cols} colunas")
            
            conn.close()
        
        return csv_file, db_file
        
    except Exception as e:
        print(f"❌ Erro durante conversão: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    converter_positivador_mtd()
