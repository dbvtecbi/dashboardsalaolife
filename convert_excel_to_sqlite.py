import pandas as pd
import sqlite3
from pathlib import Path

def convert_excel_to_csv_and_sqlite(excel_file):
    # Define output filenames
    base_name = Path(excel_file).stem
    csv_file = f"{base_name}.csv"
    db_file = f"{base_name}.db"
    
    print(f"Reading Excel file: {excel_file}")
    
    # Read Excel file
    # Using read_excel with engine='openpyxl' for better handling of .xlsx files
    df = pd.read_excel(excel_file, engine='openpyxl')
    
    print(f"Original data shape: {df.shape}")
    print("\nFirst few rows of data:")
    print(df.head())
    
    # Save to CSV
    print(f"\nSaving to CSV: {csv_file}")
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    # Create SQLite database and save data
    print(f"Creating SQLite database: {db_file}")
    conn = sqlite3.connect(db_file)
    
    # Write the data to SQLite
    df.to_sql('capital_positivador', conn, if_exists='replace', index=False)
    
    # Verify the data was written correctly
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM capital_positivador")
    count = cursor.fetchone()[0]
    print(f"\nSuccessfully wrote {count} rows to SQLite database")
    
    # Print table info
    cursor.execute("PRAGMA table_info('capital_positivador')")
    columns = cursor.fetchall()
    print("\nTable columns:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    conn.close()
    print("\nConversion completed successfully!")
    print(f"CSV file: {csv_file}")
    print(f"SQLite database: {db_file}")

if __name__ == "__main__":
    excel_file = "DBV Capital_Positivador.xlsx"
    convert_excel_to_csv_and_sqlite(excel_file)
