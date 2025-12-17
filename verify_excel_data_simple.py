import pandas as pd
import sqlite3
from datetime import datetime

def verify_excel_data():
    excel_file = "DBV Capital_Positivador.xlsx"
    db_file = "DBV Capital_Positivador.db"
    
    print(f"Reading Excel file: {excel_file}")
    
    # Read Excel file
    df_excel = pd.read_excel(excel_file, engine='openpyxl')
    
    # Get basic info about Excel data
    print("\n=== Excel File Info ===")
    print(f"Total rows: {len(df_excel):,}")
    print(f"Total columns: {len(df_excel.columns)}")
    
    # Check 'Data Posição' in Excel
    if 'Data Posição' in df_excel.columns:
        print("\n=== 'Data Posição' in Excel ===")
        print(f"Unique dates: {df_excel['Data Posição'].nunique()}")
        
        # Convert to string to avoid comparison issues
        date_str = df_excel['Data Posição'].astype(str)
        print("\nSample dates:")
        print(date_str.value_counts().head(10))
        
        # Try to find the most recent date
        try:
            # Try to convert to datetime
            df_excel['parsed_date'] = pd.to_datetime(df_excel['Data Posição'], errors='coerce')
            print(f"\nMost recent date (parsed): {df_excel['parsed_date'].max()}")
            print(f"Earliest date (parsed): {df_excel['parsed_date'].min()}")
        except Exception as e:
            print(f"Error parsing dates: {e}")
    
    # Connect to SQLite database
    print("\n=== SQLite Database Info ===")
    conn = sqlite3.connect(db_file)
    
    # Get row count from SQLite
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM capital_positivador")
    db_row_count = cursor.fetchone()[0]
    print(f"Total rows in SQLite: {db_row_count:,}")
    
    # Get date info from SQLite
    cursor.execute("""
        SELECT [Data Posição], COUNT(*) as count
        FROM capital_positivador
        GROUP BY [Data Posição]
        ORDER BY [Data Posição] DESC
        LIMIT 5
    """)
    print("\nTop dates in SQLite:")
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]:,} records")
    
    # Check for date format issues in SQLite
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN [Data Posição] LIKE '__/__/____' THEN 1 ELSE 0 END) as brazilian_format,
            SUM(CASE WHEN [Data Posição] LIKE '____-__-__%' THEN 1 ELSE 0 END) as iso_format
        FROM capital_positivador
    """)
    total, brazilian_fmt, iso_fmt = cursor.fetchone()
    print(f"\nDate formats in SQLite:")
    print(f"- Total records: {total:,}")
    print(f"- Brazilian format (DD/MM/YYYY): {brazilian_fmt:,}")
    print(f"- ISO format (YYYY-MM-DD): {iso_fmt:,}")
    
    conn.close()
    
    print("\n=== Comparison ===")
    print(f"Excel rows: {len(df_excel):,}")
    print(f"SQLite rows: {db_row_count:,}")
    
    if len(df_excel) != db_row_count:
        print(f"\nWARNING: Mismatch in row count! Excel has {len(df_excel):,} rows but SQLite has {db_row_count:,} rows.")
    
    # Check for any date parsing issues in Excel
    if 'Data Posição' in df_excel.columns:
        date_parse_issues = df_excel[df_excel['Data Posição'].isna()]
        if not date_parse_issues.empty:
            print(f"\nWARNING: Found {len(date_parse_issues)} rows with null dates in Excel")

if __name__ == "__main__":
    verify_excel_data()
