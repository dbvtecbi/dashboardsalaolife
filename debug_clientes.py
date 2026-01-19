import sys
sys.path.append(r'c:\Users\techb_gc46061\Downloads\Dash_Salão_Capital_Life\pages')

from Dashboard_Salão_Atualizado import carregar_dados_positivador_mtd
import pandas as pd

print('Verificando dados para Clientes Ativos...')

# Carregar dados
df = carregar_dados_positivador_mtd()
if df.empty:
    print('DataFrame vazio!')
    exit()

print(f'Dados carregados: {df.shape}')
print(f'Colunas: {list(df.columns)}')

# Verificar se tem coluna Cliente
if 'Cliente' not in df.columns:
    print('ERRO: Coluna "Cliente" não encontrada!')
    print('Colunas disponíveis:', list(df.columns))
else:
    print(f'Coluna Cliente encontrada: {df["Cliente"].nunique()} valores únicos')
    print(f'Amostra de clientes: {df["Cliente"].dropna().unique()[:5]}')

# Verificar valores de Net_Em_M
print(f'\nNet_Em_M - Estatísticas:')
print(f'Mínimo: {df["Net_Em_M"].min()}')
print(f'Máximo: {df["Net_Em_M"].max()}')
print(f'Positivos: {(df["Net_Em_M"] > 0).sum()}')
print(f'Negativos: {(df["Net_Em_M"] < 0).sum()}')
print(f'Zeros: {(df["Net_Em_M"] == 0).sum()}')

# Simular a lógica de clientes positivos
if not df.empty and 'Data_Posicao' in df.columns:
    df["ano_mes"] = pd.to_datetime(df["Data_Posicao"]).dt.strftime("%Y-%m")
    
    # Lógica 1: Clientes com Net_Em_M > 0
    df_clientes_positivo = (
        df[df["Net_Em_M"] > 0]
        .groupby("ano_mes")
        .size()
        .reset_index(name="clientes_positivo")
    )
    
    print(f'\nClientes positivos por mês (Net_Em_M > 0):')
    print(df_clientes_positivo.to_string(index=False))
    
    # Lógica 2: Clientes únicos
    if 'Cliente' in df.columns:
        df_clientes_unicos = (
            df.groupby("ano_mes")["Cliente"]
            .nunique()
            .reset_index(name="clientes_unicos")
        )
        
        print(f'\nClientes únicos por mês:')
        print(df_clientes_unicos.to_string(index=False))
    else:
        print('\nColuna Cliente não encontrada para calcular clientes únicos')
