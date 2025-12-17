import sqlite3
import pandas as pd

def analyze_date_column():
    # Connect to the SQLite database
    db_file = "DBV Capital_Positivador.db"
    conn = sqlite3.connect(db_file)
    
    # Query to get all dates from 'Data Posição' column
    query = "SELECT DISTINCT [Data Posição] FROM capital_positivador ORDER BY [Data Posição] DESC"
    
    # Read into pandas for better date handling
    df = pd.read_sql_query(query, conn)
    
    # Display the first 10 dates to check formats
    print("\nFirst 10 unique dates (descending order):")
    print(df.head(10).to_string(index=False))
    
    # Check for different date formats
    print("\nDate format analysis:")
    df['date_length'] = df['Data Posição'].astype(str).str.len()
    format_counts = df['date_length'].value_counts().sort_index()
    
    for length, count in format_counts.items():
        example = df[df['date_length'] == length]['Data Posição'].iloc[0]
        print(f"Length {length} (format: {example}): {count} records")
    
    # Get min and max dates as strings to see the exact values
    min_date = df['Data Posição'].min()
    max_date = df['Data Posição'].max()
    
    print(f"\nDate range as strings:")
    print(f"Earliest date: {min_date}")
    print(f"Latest date: {max_date}")
    
    # Try to convert to datetime to see if there are any parsing issues
    try:
        df['parsed_date'] = pd.to_datetime(df['Data Posição'], errors='coerce')
        null_dates = df['parsed_date'].isna().sum()
        print(f"\nSuccessfully parsed {len(df) - null_dates} out of {len(df)} dates")
        if null_dates > 0:
            print(f"Could not parse {null_dates} dates. Examples:")
            print(df[df['parsed_date'].isna()]['Data Posição'].head().to_string(index=False))
        
        print("\nDate range after parsing:")
        print(f"Earliest date: {df['parsed_date'].min()}")
        print(f"Latest date: {df['parsed_date'].max()}")
    except Exception as e:
        print(f"\nError parsing dates: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    analyze_date_column()
