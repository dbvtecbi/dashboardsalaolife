import sqlite3

def get_latest_nps_date():
    # Connect to the SQLite database
    db_file = "DBV_Capital_NPS.db"
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in database: {[t[0] for t in tables]}")
        
        # Assuming the table is named 'nps_data' (from our conversion script)
        table_name = 'nps_data'
        
        # Get column names to help identify date columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\nColumns in {table_name}: {columns}")
        
        # Try to find date columns (case insensitive)
        date_columns = [col for col in columns if 'data' in col.lower() or 'date' in col.lower()]
        
        if not date_columns:
            print("\nNo date columns found. Here's a sample of the data:")
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            print(cursor.fetchone())
            return
            
        print(f"\nFound potential date columns: {date_columns}")
        
        # Check each date column
        for col in date_columns:
            try:
                # Get min and max dates
                cursor.execute(f'SELECT MIN([{col}]), MAX([{col}]) FROM {table_name} WHERE [{col}] IS NOT NULL')
                min_date, max_date = cursor.fetchone()
                if min_date and max_date:
                    print(f"\nDate range in column '{col}':")
                    print(f"Earliest: {min_date}")
                    print(f"Latest: {max_date}")
                    print(f"Total records: {cursor.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]}")
                    print(f"Records with dates: {cursor.execute(f'SELECT COUNT(*) FROM {table_name} WHERE [{col}] IS NOT NULL').fetchone()[0]}")
            except sqlite3.Error as e:
                print(f"\nError checking column '{col}': {e}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    get_latest_nps_date()
