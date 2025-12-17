import pandas as pd
import sqlite3
import unicodedata
import re
from pathlib import Path

def remover_acentos(texto):
    """Remove acentos de uma string."""
    if not isinstance(texto, str):
        return texto
    # Normaliza para forma NFD e remove caracteres de combinação (acentos)
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sem_acentos = ''.join(
        char for char in texto_normalizado
        if unicodedata.category(char) != 'Mn'
    )
    return texto_sem_acentos

def formatar_nome_coluna(nome):
    """
    Formata o nome da coluna seguindo as regras:
    1. Substituir espaços por underscores
    2. Remover acentos
    3. Manter Title_Case
    """
    if not isinstance(nome, str):
        nome = str(nome)
    
    # Remove acentos
    nome = remover_acentos(nome)
    
    # Substitui espaços por underscores
    nome = nome.replace(' ', '_')
    
    # Remove caracteres especiais (mantém letras, números e underscores)
    nome = re.sub(r'[^\w]', '_', nome)
    
    # Remove underscores duplicados
    nome = re.sub(r'_+', '_', nome)
    
    # Remove underscores no início e fim
    nome = nome.strip('_')
    
    # Aplica Title_Case em cada palavra separada por underscore
    partes = nome.split('_')
    partes_formatadas = [parte.capitalize() for parte in partes if parte]
    nome = '_'.join(partes_formatadas)
    
    return nome

def converter_excel_para_sqlite(excel_path, db_path):
    """Converte arquivo Excel para SQLite com colunas formatadas."""
    
    print(f"Lendo arquivo Excel: {excel_path}")
    
    # Lê o arquivo Excel
    df = pd.read_excel(excel_path, engine='openpyxl')
    
    print(f"\nColunas originais ({len(df.columns)}):")
    for col in df.columns:
        print(f"  - {col}")
    
    # Renomeia as colunas
    colunas_originais = df.columns.tolist()
    colunas_novas = [formatar_nome_coluna(col) for col in colunas_originais]
    
    # Cria mapeamento
    mapeamento = dict(zip(colunas_originais, colunas_novas))
    df.rename(columns=mapeamento, inplace=True)
    
    print(f"\nColunas formatadas ({len(df.columns)}):")
    for col in df.columns:
        print(f"  - {col}")
    
    print(f"\nTotal de linhas: {len(df)}")
    
    # Salva no SQLite
    conn = sqlite3.connect(db_path)
    df.to_sql('positivador_mtd', conn, if_exists='replace', index=False)
    conn.close()
    
    print(f"\nBanco de dados salvo em: {db_path}")
    
    return df

def main():
    base_dir = Path(__file__).parent
    excel_path = base_dir / "DBV Capital_Positivador (MTD).xlsx"
    csv_path = base_dir / "DBV_Capital_Positivador_MTD.csv"
    db_path = base_dir / "DBV Capital_Positivador (MTD).db"
    
    try:
        print(f"Lendo arquivo Excel: {excel_path}")
        
        # Lê o arquivo Excel
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        print(f"\nColunas originais ({len(df.columns)}):")
        for col in df.columns:
            print(f"  - {col}")
        
        # Salva CSV com colunas originais
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"\n✓ CSV salvo em: {csv_path}")
        
        # Renomeia as colunas para o SQLite
        colunas_originais = df.columns.tolist()
        colunas_novas = [formatar_nome_coluna(col) for col in colunas_originais]
        mapeamento = dict(zip(colunas_originais, colunas_novas))
        df.rename(columns=mapeamento, inplace=True)
        
        print(f"\nColunas formatadas ({len(df.columns)}):")
        for col in df.columns:
            print(f"  - {col}")
        
        print(f"\nTotal de linhas: {len(df)}")
        
        # Salva no SQLite
        conn = sqlite3.connect(db_path)
        df.to_sql('positivador_mtd', conn, if_exists='replace', index=False)
        conn.close()
        
        print(f"\n✓ Banco de dados salvo em: {db_path}")
        print("\n✓ Conversão concluída com sucesso!")
        print(f"  - Colunas: {len(df.columns)}")
        print(f"  - Linhas: {len(df)}")
    except Exception as e:
        print(f"\nErro durante a conversão: {str(e)}")
        raise

if __name__ == "__main__":
    main()
