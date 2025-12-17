import pandas as pd
import sqlite3
from pathlib import Path

# Define file paths
excel_file = 'DBV Capital_NPS.xlsm'
csv_file = 'DBV_Capital_NPS.csv'
db_file = 'DBV_Capital_NPS.db'
table_name = 'nps_data'

# Read the Excel file (including all sheets)
print(f"Reading Excel file: {excel_file}")
xls = pd.ExcelFile(excel_file)

# Read the first sheet (or specify sheet name if needed)
# If you need to read a specific sheet, replace 0 with the sheet name
df = pd.read_excel(excel_file, sheet_name=0)

# Save to CSV
print(f"Converting to CSV: {csv_file}")
df.to_csv(csv_file, index=False, encoding='utf-8')

# Create SQLite database and save data
print(f"Creating SQLite database: {db_file}")
conn = sqlite3.connect(db_file)
df.to_sql(table_name, conn, if_exists='replace', index=False)

# Verify the data was saved correctly
cursor = conn.cursor()
cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
count = cursor.fetchone()[0]
print(f"Successfully saved {count} rows to SQLite database")

# Close the connection
conn.close()

print("Conversion completed successfully!")
print(f"CSV file: {Path(csv_file).resolve()}")
print(f"SQLite DB: {Path(db_file).resolve()}")
