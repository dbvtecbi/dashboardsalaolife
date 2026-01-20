import pandas as pd
import sqlite3
from pathlib import Path

def converter_positivador_mtd_para_db():
    """Converter DBV Capital_Positivador (MTD).xlsx para CSV e DB mantendo todas as linhas e colunas"""
    
    # Caminhos dos arquivos
    caminho_excel = Path("DBV Capital_Positivador (MTD).xlsx")
    caminho_csv = Path("DBV Capital_Positivador_MTD.csv")
    caminho_db = Path("DBV Capital_Positivador_MTD.db")
    
    print("=== CONVERSÃO DE POSITIVADOR MTD PARA CSV E DB ===")
    
    # 1. Verificar se o arquivo Excel existe
    if not caminho_excel.exists():
        print(f"❌ Arquivo Excel não encontrado: {caminho_excel}")
        return
    
    print(f"✅ Arquivo Excel encontrado: {caminho_excel}")
    print(f"Tamanho: {caminho_excel.stat().st_size} bytes")
    
    try:
        # 2. Ler todas as planilhas do Excel
        excel_file = pd.ExcelFile(str(caminho_excel))
        planilhas = excel_file.sheet_names
        print(f"\n📋 Planilhas encontradas: {planilhas}")
        
        # Processar cada planilha
        for nome_planilha in planilhas:
            print(f"\n--- Processando planilha: {nome_planilha} ---")
            
            # Ler a planilha mantendo todas as linhas e colunas
            df = pd.read_excel(str(caminho_excel), sheet_name=nome_planilha, header=0)
            
            print(f"📊 Registros encontrados: {len(df)}")
            print(f"📋 Colunas: {list(df.columns)}")
            
            # Salvar como CSV
            if len(planilhas) == 1:
                # Se só tiver uma planilha, salva diretamente
                df.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
                print(f"✅ CSV salvo: {caminho_csv}")
            else:
                # Se tiver múltiplas planilhas, salva com prefixo
                csv_planilha = Path(f"DBV Capital_Positivador_MTD_{nome_planilha}.csv")
                df.to_csv(csv_planilha, index=False, encoding='utf-8-sig')
                print(f"✅ CSV salvo: {csv_planilha}")
            
            # Salvar no banco de dados
            conn = sqlite3.connect(str(caminho_db))
            
            # Limpar nome da tabela para SQLite
            nome_tabela = nome_planilha.replace(" ", "_").replace("-", "_").replace("/", "_").replace("(", "").replace(")", "")
            nome_tabela = "".join(c for c in nome_tabela if c.isalnum() or c == "_")
            
            # Converter todas as colunas para string para evitar problemas
            print("🔄 Convertendo colunas para texto...")
            for col in df.columns:
                df[col] = df[col].astype(str)
                # Tratar valores NaN
                df[col] = df[col].replace('nan', '')
            
            # Criar tabela manualmente com todas as colunas como TEXT
            col_defs = []
            for col in df.columns:
                col_limpa = col.replace('"', '""')  # Escapar aspas
                col_defs.append(f'"{col_limpa}" TEXT')
            
            create_sql = f'''
            CREATE TABLE IF NOT EXISTS {nome_tabela} (
                {", ".join(col_defs)}
            )
            '''
            
            cursor = conn.cursor()
            cursor.execute(create_sql)
            
            # Inserir dados linha por linha para garantir integridade
            print("📝 Inserindo dados no banco...")
            for index, row in df.iterrows():
                # Preparar valores
                valores = tuple(str(val) if pd.notna(val) else '' for val in row)
                
                # Construir INSERT
                placeholders = ", ".join(["?" for _ in range(len(row))])
                insert_sql = f'INSERT INTO {nome_tabela} VALUES ({placeholders})'
                
                cursor.execute(insert_sql, valores)
            
            conn.commit()
            conn.close()
            
            print(f"✅ Tabela '{nome_tabela}' criada no banco de dados")
            
            # Verificar se foi criada corretamente
            conn_verificacao = sqlite3.connect(str(caminho_db))
            df_verificacao = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {nome_tabela}", conn_verificacao)
            count = df_verificacao.iloc[0]['count']
            print(f"   ✅ Registros verificados: {count}")
            conn_verificacao.close()
        
        # 3. Verificação final do banco
        print(f"\n=== VERIFICAÇÃO FINAL DO BANCO ===")
        conn_final = sqlite3.connect(str(caminho_db))
        cursor = conn_final.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas_criadas = [t[0] for t in cursor.fetchall()]
        print(f"📁 Tabelas criadas no banco: {tabelas_criadas}")
        
        total_registros = 0
        for tabela in tabelas_criadas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            total_registros += count
            print(f"  - {tabela}: {count:,} registros")
        
        conn_final.close()
        
        print(f"\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"📊 Total de registros processados: {total_registros:,}")
        print(f"📁 Arquivos criados:")
        print(f"   - CSV: {caminho_csv}")
        print(f"   - Banco de dados: {caminho_db}")
        
    except Exception as e:
        print(f"❌ Erro durante a conversão: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    converter_positivador_mtd_para_db()
