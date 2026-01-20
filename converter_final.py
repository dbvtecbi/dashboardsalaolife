import pandas as pd
import sqlite3
from pathlib import Path

def converter_excel_para_db():
    """Converter Excel para CSV e DB forçando tudo para texto primeiro"""
    
    # Caminhos dos arquivos
    caminho_excel = Path("DBV Capital_Produtos.xlsx")
    caminho_csv = Path("DBV Capital_Produtos.csv")
    caminho_db = Path("DBV Capital_Produtos.db")
    
    print("=== CONVERSÃO DE EXCEL PARA CSV E DB ===")
    
    # 1. Verificar se o arquivo Excel existe
    if not caminho_excel.exists():
        print(f"❌ Arquivo Excel não encontrado: {caminho_excel}")
        return
    
    print(f"✅ Arquivo Excel encontrado: {caminho_excel}")
    
    try:
        # 2. Ler a planilha
        print("📋 Lendo planilha 'Produtos'...")
        df = pd.read_excel(str(caminho_excel), sheet_name="Produtos", header=0)
        
        print(f"📊 Registros encontrados: {len(df)}")
        print(f"📋 Colunas: {list(df.columns)}")
        
        # 3. Converter todas as colunas para string para evitar problemas
        print("🔄 Convertendo colunas para texto...")
        for col in df.columns:
            df[col] = df[col].astype(str)
            # Tratar valores NaN
            df[col] = df[col].replace('nan', '')
        
        print("✅ Conversão para texto concluída")
        
        # 4. Salvar como CSV
        print("💾 Salvando CSV...")
        df.to_csv(caminho_csv, index=False, encoding='utf-8-sig')
        print(f"✅ CSV salvo: {caminho_csv}")
        
        # 5. Salvar no banco de dados
        print("🗄️ Criando banco de dados...")
        conn = sqlite3.connect(str(caminho_db))
        
        # Criar tabela manualmente com todas as colunas como TEXT
        nome_tabela = "Produtos"
        
        # Construir SQL CREATE TABLE
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
        
        # Inserir dados linha por linha
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
        
        # 6. Verificação final
        print("\n=== VERIFICAÇÃO FINAL ===")
        conn_verificacao = sqlite3.connect(str(caminho_db))
        df_verificacao = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {nome_tabela}", conn_verificacao)
        count = df_verificacao.iloc[0]['count']
        print(f"✅ Registros verificados: {count}")
        
        # Verificar algumas linhas
        df_amostra = pd.read_sql_query(f"SELECT * FROM {nome_tabela} LIMIT 3", conn_verificacao)
        print(f"📋 Amostra de dados:")
        for index, row in df_amostra.iterrows():
            print(f"   {index+1}: {dict(row)}")
        
        conn_verificacao.close()
        
        print(f"\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print(f"📊 Total de registros: {count:,}")
        print(f"📁 Arquivos criados:")
        print(f"   - CSV: {caminho_csv}")
        print(f"   - Banco de dados: {caminho_db}")
        
    except Exception as e:
        print(f"❌ Erro durante a conversão: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    converter_excel_para_db()
