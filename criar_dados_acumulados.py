import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Criar dados simulados baseados na estrutura solicitada pelo usuário
# Vamos criar uma tabela com as colunas mencionadas: Data, Cap Objetivo (ano), Cap Acumulado, AUC Objetivo (Ano), AUC Acumulado, Cap Diário (ANO)

def criar_dados_simulados():
    """Cria dados simulados para testar a nova lógica"""
    
    # Data de referência (data de atualização do dashboard)
    data_ref = datetime(2026, 1, 19)  # Exemplo: 19/01/2026
    
    # Criar dataframe com dados diários para 2026
    datas = []
    cap_objetivo_ano = 183_600_000  # Valor do banco de objetivos para 2026
    auc_objetivo_ano = 694_000_000   # Valor do banco de objetivos para 2026
    
    # Valores iniciais
    cap_acumulado_inicial = 453_052_907  # AUC Initial de 2026
    auc_acumulado_inicial = 453_052_907
    
    cap_diario_medio = cap_objetivo_ano / 365  # Média diária para captação
    auc_diario_medio = (auc_objetivo_ano - auc_acumulado_inicial) / 365  # Média diária para AUC
    
    dados = []
    cap_acumulado = 0
    auc_acumulado = auc_acumulado_inicial
    
    # Gerar dados para cada dia de 2026
    for dia in range(1, 32):  # Janeiro
        data = datetime(2026, 1, dia)
        
        # Simular valores diários com alguma variação
        cap_diario = cap_diario_medio * np.random.uniform(0.8, 1.2)
        auc_diario = auc_diario_medio * np.random.uniform(0.9, 1.1)
        
        cap_acumulado += cap_diario
        auc_acumulado += auc_diario
        
        dados.append({
            'Data': data.strftime('%d/%m/%Y'),
            'Cap Objetivo (ano)': cap_objetivo_ano,
            'Cap Acumulado': cap_acumulado,
            'AUC Objetivo (Ano)': auc_objetivo_ano,
            'AUC Acumulado': auc_acumulado,
            'Cap Diário (ANO)': cap_diario
        })
    
    df = pd.DataFrame(dados)
    return df

def criar_tabela_objetivos_pj1():
    """Cria a tabela Objetivos_PJ1 no banco de dados"""
    
    # Conectar ao banco de dados existente
    conn = sqlite3.connect('DBV Capital_Objetivos.db')
    cursor = conn.cursor()
    
    # Criar a tabela Objetivos_PJ1
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS "Objetivos_PJ1" (
        "Data" TEXT,
        "Cap Objetivo (ano)" REAL,
        "Cap Acumulado" REAL,
        "AUC Objetivo (Ano)" REAL,
        "AUC Acumulado" REAL,
        "Cap Diário (ANO)" REAL
    )
    ''')
    
    # Gerar e inserir dados
    df = criar_dados_simulados()
    
    # Inserir dados no banco
    df.to_sql('Objetivos_PJ1', conn, if_exists='replace', index=False)
    
    # Verificar inserção
    cursor.execute("SELECT COUNT(*) FROM Objetivos_PJ1")
    total_registros = cursor.fetchone()[0]
    print(f"Tabela Objetivos_PJ1 criada com {total_registros} registros")
    
    # Mostrar primeiros registros
    df_verificacao = pd.read_sql_query("SELECT * FROM Objetivos_PJ1 LIMIT 5", conn)
    print("\nPrimeiros 5 registros:")
    print(df_verificacao)
    
    conn.commit()
    conn.close()
    
    print("\n✅ Tabela Objetivos_PJ1 criada com sucesso!")

if __name__ == "__main__":
    criar_tabela_objetivos_pj1()
