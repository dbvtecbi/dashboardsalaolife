import pandas as pd
import sqlite3
from pathlib import Path

def convert_excel_to_db():
    # File paths
    excel_file = Path("DBV Capital_Positivador.xlsx")
    csv_file = excel_file.with_suffix('.csv')
    db_file = excel_file.with_suffix('.db')
    
    print(f"Reading Excel file: {excel_file}")
    
    try:
        # Read the Excel file
        print("Reading all sheets from Excel...")
        xl = pd.ExcelFile(excel_file)
        
        # Convert each sheet to CSV and store in SQLite
        with sqlite3.connect(db_file) as conn:
            for sheet_name in xl.sheet_names:
                print(f"Processing sheet: {sheet_name}")
                
                # Read the sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name, dtype=str)
                
                # Save to CSV
                if len(xl.sheet_names) > 1:
                    sheet_csv = excel_file.stem + f'_{sheet_name}.csv'
                else:
                    sheet_csv = csv_file
                
                # Clean sheet name for SQL table
                table_name = f"{sheet_name}".replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
                
                # Save to SQLite
                df.to_sql(name=table_name, con=conn, if_exists='replace', index=False)
                print(f"  - Added to database as table: {table_name}")
                
                # Save to CSV
                df.to_csv(sheet_csv, index=False, encoding='utf-8-sig')
                print(f"  - Saved to CSV: {sheet_csv}")
        
        print(f"\nConversion completed successfully!")
        print(f"- Database file: {db_file.absolute()}")
        print(f"- CSV file(s) created in the same directory")
        
    except Exception as e:
        print(f"\nError during conversion: {str(e)}")
        raise

if __name__ == "__main__":
    convert_excel_to_db()
