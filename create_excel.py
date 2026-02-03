#!/usr/bin/env python3
try:
    import pandas as pd
    
    # Read the CSV file
    df = pd.read_csv('FNC_Dropped_Breaks.csv')
    
    # Create Excel writer
    excel_file = 'FNC_Dropped_Breaks.xlsx'
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Get unique dates
        unique_dates = sorted(df['Date'].unique())
        
        # Create a sheet for each date
        for date in unique_dates:
            # Filter data for this date
            date_data = df[df['Date'] == date]
            
            # Write to sheet named with the date
            sheet_name = date.replace('/', '-')
            date_data.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Also create an "All" sheet with all data
        df.to_excel(writer, sheet_name='All Dates', index=False)
    
    print(f"✓ Excel file created: {excel_file}")
    print(f"✓ Created sheets for dates: {', '.join(unique_dates)}")
    print(f"✓ Plus 'All Dates' sheet with complete data")
except Exception as e:
    print(f"Error: {e}")

