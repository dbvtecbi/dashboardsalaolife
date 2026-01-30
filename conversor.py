import pandas as pd
import sqlite3

# Ler o arquivo Excel
df_transferencias = pd.read_excel('c:\\Users\\techb_gc46061\\Downloads\\Dash_Salão_Capital_Life\\DBV Capital_Transferências.xlsx')

# Salvar como CSV
df_transferencias.to_csv('c:\\Users\\techb_gc46061\\Downloads\\Dash_Salão_Capital_Life\\DBV Capital_Transferências.csv', index=False, encoding='utf-8-sig')

# Criar banco de dados SQLite
conn = sqlite3.connect('c:\\Users\\techb_gc46061\\Downloads\\Dash_Salão_Capital_Life\\DBV Capital_Transferências.db')
df_transferencias.to_sql('transferencias', conn, if_exists='replace', index=False)
conn.close()

print(f'Arquivo convertido com sucesso!')
print(f'Linhas: {len(df_transferencias)}')
print(f'Colunas: {len(df_transferencias.columns)}')
print(f'Colunas: {list(df_transferencias.columns)}')


# Ler o arquivo Excel
df_feebased = pd.read_excel('c:\\Users\\techb_gc46061\\Downloads\\Dash_Salão_Capital_Life\\DBV Capital_FeeBased.xlsx')

# Salvar como CSV
df_feebased.to_csv('c:\\Users\\techb_gc46061\\Downloads\\Dash_Salão_Capital_Life\\DBV Capital_FeeBased.csv', index=False, encoding='utf-8-sig')

# Criar banco de dados SQLite
conn = sqlite3.connect('c:\\Users\\techb_gc46061\\Downloads\\Dash_Salão_Capital_Life\\DBV Capital_FeeBased.db')
df_feebased.to_sql('feebased', conn, if_exists='replace', index=False)
conn.close()

print(f'Arquivo convertido com sucesso!')
print(f'Linhas: {len(df_feebased)}')
print(f'Colunas: {len(df_feebased.columns)}')
print(f'Colunas: {list(df_feebased.columns)}')
