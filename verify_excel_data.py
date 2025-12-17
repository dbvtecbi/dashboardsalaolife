import pandas as pd
import sqlite3

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
    print("\nFirst 5 rows of Excel data:")
    print(df_excel.head().to_string())
    
    # Check 'Data Posição' in Excel
    if 'Data Posição' in df_excel.columns:
        print("\n=== 'Data Posição' in Excel ===")
        print(f"Unique dates: {df_excel['Data Posição'].nunique()}")
        print(f"Date range: {df_excel['Data Posição'].min()} to {df_excel['Data Posição'].max()}")
        print("\nValue counts:")
        print(df_excel['Data Posição'].value_counts().sort_index(ascending=False).head(10))
    
    # Connect to SQLite database
    print("\n=== SQLite Database Info ===")
    conn = sqlite3.connect(db_file)
    
    # Get row count from SQLite
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM capital_positivador")
    db_row_count = cursor.fetchone()[0]
    print(f"Total rows in SQLite: {db_row_count:,}")
    
    # Check 'Data Posição' in SQLite
    cursor.execute("SELECT COUNT(DISTINCT [Data Posição]) FROM capital_positivador")
    db_unique_dates = cursor.fetchone()[0]
    print(f"Unique dates in SQLite: {db_unique_dates}")
    
    # Get date range from SQLite
    cursor.execute("""
        SELECT MIN([Data Posição]), MAX([Data Posição])
        FROM capital_positivador
        WHERE [Data Posição] IS NOT NULL
    """)
    min_date, max_date = cursor.fetchone()
    print(f"Date range in SQLite: {min_date} to {max_date}")
    
    # Get top dates from SQLite
    print("\nTop dates in SQLite:")
    cursor.execute("""
        SELECT [Data Posição], COUNT(*) as count
        FROM capital_positivador
        GROUP BY [Data Posição]
        ORDER BY [Data Posição] DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]:,} records")
    
    conn.close()
    
    # Compare row counts
    print("\n=== Comparison ===")
    print(f"Excel rows: {len(df_excel):,}")
    print(f"SQLite rows: {db_row_count:,}")
    
    if len(df_excel) != db_row_count:
        print(f"\nWARNING: Mismatch in row count! Excel has {len(df_excel):,} rows but SQLite has {db_row_count:,} rows.")
    
    # Check for any date parsing issues
    if 'Data Posição' in df_excel.columns:
        date_parse_issues = df_excel[df_excel['Data Posição'].isna()]
        if not date_parse_issues.empty:
            print(f"\nWARNING: Found {len(date_parse_issues)} rows with null dates in Excel")

if __name__ == "__main__":
    verify_excel_data()
