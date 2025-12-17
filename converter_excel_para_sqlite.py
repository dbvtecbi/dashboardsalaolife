import pandas as pd
import sqlite3
from pathlib import Path

def excel_para_sqlite(caminho_excel, caminho_saida=None):
    """
    Converte um arquivo Excel para SQLite, mantendo todos os dados.
    
    Args:
        caminho_excel (str): Caminho para o arquivo Excel de entrada
        caminho_saida (str, opcional): Caminho para o arquivo SQLite de saída. 
                                     Se não informado, usa o mesmo nome do Excel com extensão .db
    """
    # Define o caminho de saída se não for informado
    if caminho_saida is None:
        caminho_saida = str(Path(caminho_excel).with_suffix('.db'))
    
    print(f"Lendo arquivo Excel: {caminho_excel}")
    
    # Lê todas as planilhas do Excel
    xls = pd.ExcelFile(caminho_excel)
    
    # Conecta ao banco de dados SQLite
    conn = sqlite3.connect(caminho_saida)
    
    # Para cada planilha no Excel, cria uma tabela no SQLite
    for sheet_name in xls.sheet_names:
        print(f"Processando planilha: {sheet_name}")
        
        # Lê a planilha
        df = pd.read_excel(xls, sheet_name=sheet_name)
        
        # Remove espaços e caracteres especiais dos nomes das colunas
        df.columns = [str(col).strip().replace(' ', '_').replace('.', '_') for col in df.columns]
        
        # Salva no SQLite
        df.to_sql(sheet_name, conn, index=False, if_exists='replace')
        
        print(f"  - Tabela '{sheet_name}' criada com {len(df)} registros")
    
    # Fecha a conexão
    conn.close()
    
    print(f"\nConversão concluída! Arquivo salvo em: {caminho_saida}")
    return caminho_saida

if __name__ == "__main__":
    # Caminho para o arquivo Excel
    caminho_excel = r"c:\Users\techb_gc46061\Downloads\dashboard\backup-2\DBV Capital_Positivador (MTD).xlsx"
    
    # Converte para SQLite
    caminho_db = excel_para_sqlite(caminho_excel)
    
    print(f"\nArquivo convertido com sucesso para: {caminho_db}")
