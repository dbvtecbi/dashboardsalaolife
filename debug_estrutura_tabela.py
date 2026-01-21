import sqlite3
import pandas as pd

# Conectar ao banco de dados
conn = sqlite3.connect('DBV Capital_Objetivos.db')

# Verificar estrutura da tabela
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(Objetivos_PJ1);")
columns = cursor.fetchall()

print("Estrutura da tabela Objetivos_PJ1:")
for col in columns:
    print(f"- {col[1]} ({col[2]})")

# Verificar dados reais
df = pd.read_sql_query("SELECT * FROM Objetivos_PJ1 LIMIT 3", conn)
print(f"\nColunas encontradas: {list(df.columns)}")
print("\nPrimeiros 3 registros:")
print(df)

conn.close()
