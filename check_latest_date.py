import sqlite3

def get_latest_date():
    # Connect to the SQLite database
    db_file = "DBV Capital_Positivador.db"
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Query to get the most recent date from 'Data Posição' column
    cursor.execute("SELECT MAX([Data Posição]) FROM capital_positivador")
    latest_date = cursor.fetchone()[0]
    
    # Count total records and count of non-null dates
    cursor.execute("SELECT COUNT(*) FROM capital_positivador")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM capital_positivador WHERE [Data Posição] IS NOT NULL")
    records_with_date = cursor.fetchone()[0]
    
    # Get date range
    cursor.execute("SELECT MIN([Data Posição]), MAX([Data Posição]) FROM capital_positivador WHERE [Data Posição] IS NOT NULL")
    min_date, max_date = cursor.fetchone()
    
    conn.close()
    
    print(f"Database: {db_file}")
    print(f"Total records: {total_records:,}")
    print(f"Records with date: {records_with_date:,} ({(records_with_date/total_records*100):.1f}%)")
    print(f"Date range in 'Data Posição': {min_date} to {max_date}")
    print(f"Most recent date in 'Data Posição': {latest_date}")

if __name__ == "__main__":
    get_latest_date()
