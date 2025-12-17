import sqlite3
import pandas as pd
from pathlib import Path

# Carregar transferencias
conn = sqlite3.connect('DBV Capital_Transferências.db')
df_trans = pd.read_sql_query("SELECT * FROM Planilha1 WHERE Cliente = 'Externo'", conn)
conn.close()

print(f'Total transferencias externas: {len(df_trans)}')
print(f'Colunas: {df_trans.columns.tolist()}')

# Verificar assessores com transferencias
if 'Código Assessor Destino' in df_trans.columns and 'PL' in df_trans.columns:
    df_trans['PL_num'] = pd.to_numeric(df_trans['PL'], errors='coerce').fillna(0)
    top = df_trans.groupby('Código Assessor Destino')['PL_num'].sum().sort_values(ascending=False).head(5)
    print()
    print('Top 5 assessores por transferencias:')
    print(top)
