import pandas as pd
import sqlite3
from datetime import datetime

def fix_date_formats():
    # File paths
    db_file = "DBV Capital_Positivador.db"
    backup_db = "DBV_Capital_Positivador_backup.db"
    
    print("Connecting to the database...")
    
    # Create a backup of the original database
    import shutil
    shutil.copy2(db_file, backup_db)
    print(f"Created backup at: {backup_db}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    
    # Read the data into a pandas DataFrame
    print("Reading data from SQLite...")
    df = pd.read_sql_query("SELECT * FROM capital_positivador", conn)
    
    # Check and fix date formats in 'Data Posição'
    if 'Data Posição' in df.columns:
        print("\n=== Before Fixing Dates ===")
        print("Date formats in 'Data Posição':")
        print(df['Data Posição'].str[:10].value_counts().head())
        
        # Convert '08/12/2025' to '2025-12-08 00:00:00'
        mask = df['Data Posição'].str.match(r'^\d{2}/\d{2}/\d{4}$', na=False)
        print(f"\nFound {mask.sum()} dates in DD/MM/YYYY format")
        
        if mask.any():
            # Convert to datetime and then to string in the desired format
            df.loc[mask, 'Data Posição'] = pd.to_datetime(
                df.loc[mask, 'Data Posição'], 
                format='%d/%m/%Y'
            ).dt.strftime('%Y-%m-%d 00:00:00')
            
            print("\n=== After Fixing Dates ===")
            print("Date formats in 'Data Posição':")
            print(df['Data Posição'].str[:10].value_counts().head())
            
            # Update the database
            print("\nUpdating the database...")
            conn.execute("DROP TABLE IF EXISTS capital_positivador")
            df.to_sql('capital_positivador', conn, index=False)
            print("Database updated successfully!")
        else:
            print("No dates in DD/MM/YYYY format found to convert.")
    
    # Verify the changes
    cursor = conn.cursor()
    
    # Get date range
    cursor.execute("""
        SELECT 
            MIN([Data Posição]) as min_date,
            MAX([Data Posição]) as max_date,
            COUNT(*) as total_rows,
            COUNT(DISTINCT [Data Posição]) as unique_dates
        FROM capital_positivador
    """)
    
    min_date, max_date, total_rows, unique_dates = cursor.fetchone()
    
    print("\n=== Final Verification ===")
    print(f"Total rows: {total_rows:,}")
    print(f"Unique dates: {unique_dates}")
    print(f"Date range: {min_date} to {max_date}")
    
    # Get the most recent date
    cursor.execute("""
        SELECT [Data Posição], COUNT(*) as count
        FROM capital_positivador
        GROUP BY [Data Posição]
        ORDER BY [Data Posição] DESC
        LIMIT 5
    """)
    
    print("\nMost recent dates:")
    for date, count in cursor.fetchall():
        print(f"{date}: {count:,} records")
    
    conn.close()
    print("\nProcess completed successfully!")
    print(f"Original database was backed up to: {backup_db}")
    print(f"Updated database: {db_file}")

if __name__ == "__main__":
    fix_date_formats()
