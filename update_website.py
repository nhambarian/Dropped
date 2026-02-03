#!/usr/bin/env python3
"""
Broadcast Tracker Auto-Update Script
Reads from FNC_Dropped_Breaks.csv and automatically updates broadcast_tracker.html
"""

import csv
import re
import os
from datetime import datetime

def parse_csv(file_path):
    """Parse CSV file and extract broadcast entries"""
    entries = []
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {}
            
            # Map CSV columns to entry fields
            if row.get('Channel'):
                entry['channel'] = row['Channel'].strip()
            if row.get('Date'):
                entry['date'] = row['Date'].strip()
            if row.get('Time'):
                # Convert 1000ET to 10:00 AM, 1100ET to 11:00 AM, etc.
                time_str = row['Time'].replace('ET', '').strip()
                if len(time_str) == 4:
                    hour = int(time_str[:2])
                    minute = time_str[2:]
                    period = 'AM' if hour < 12 else 'PM'
                    if hour > 12:
                        hour -= 12
                    elif hour == 0:
                        hour = 12
                    entry['time'] = f"{hour}:{minute} {period}"
                else:
                    entry['time'] = time_str
            if row.get('Program'):
                entry['program'] = row['Program'].strip()
            if row.get('Break Dropped/Busted'):
                entry['breakDropped'] = row['Break Dropped/Busted'].strip()
            if row.get('Topic'):
                entry['topic'] = row['Topic'].strip()
            if row.get('Director'):
                entry['director'] = row['Director'].strip()
            if row.get('Producer'):
                entry['producer'] = row['Producer'].strip()
            
            # Only add if we have the essential fields
            if 'date' in entry and 'program' in entry and 'breakDropped' in entry:
                # Convert date format from 1/28/26 to 2026-01-28
                date_parts = entry['date'].split('/')
                if len(date_parts) == 3:
                    month, day, year = date_parts
                    year = f"20{year}" if len(year) == 2 else year
                    entry['date_formatted'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                
                entries.append(entry)
    
    return entries

def generate_javascript_data(entries):
    """Generate JavaScript data array from entries"""
    js_lines = []
    js_lines.append("        const broadcastData = [")
    
    for i, entry in enumerate(entries):
        js_lines.append("            {")
        js_lines.append(f"                date: \"{entry.get('date_formatted', '2026-01-28')}\",")
        js_lines.append(f"                time: \"{entry.get('time', 'N/A')}\",")
        js_lines.append(f"                program: \"{entry.get('program', 'N/A')}\",")
        js_lines.append(f"                channel: \"{entry.get('channel', 'N/A')}\",")
        js_lines.append(f"                breakDropped: \"{entry.get('breakDropped', 'N/A')}\",")
        js_lines.append(f"                topic: \"{entry.get('topic', 'N/A')}\"")
        
        if i < len(entries) - 1:
            js_lines.append("            },")
        else:
            js_lines.append("            }")
    
    js_lines.append("        ];")
    
    return "\n".join(js_lines)

def get_unique_dates(entries):
    """Extract unique dates from entries and sort them"""
    dates = set()
    for entry in entries:
        if 'date_formatted' in entry:
            dates.add(entry['date_formatted'])
    return sorted(list(dates))

def generate_table_rows(entries):
    """Generate HTML table rows from entries"""
    rows = []
    
    for entry in entries:
        row = f"""                    <tr>
                        <td>{entry.get('time', 'N/A')}</td>
                        <td>{entry.get('program', 'N/A')}</td>
                        <td>{entry.get('channel', 'N/A')}</td>
                        <td><span class="break-badge">{entry.get('breakDropped', 'N/A')}</span></td>
                        <td>{entry.get('topic', 'N/A')}</td>
                    </tr>"""
        rows.append(row)
    
    return "\n".join(rows)

def update_html(html_file, entries):
    """Update the HTML file with new data"""
    with open(html_file, 'r') as f:
        html_content = f.read()
    
    # Generate new JavaScript data
    new_js_data = generate_javascript_data(entries)
    
    # Find and replace the broadcastData array
    pattern = r'const broadcastData = \[[\s\S]*?\];'
    html_content = re.sub(pattern, new_js_data, html_content)
    
    # Generate new table rows
    new_table_rows = generate_table_rows(entries)
    
    # Find and replace table body content
    # Match everything between <tbody id="breaksTableBody"> and </tbody>
    pattern = r'<tbody id="breaksTableBody">[\s\S]*?</tbody>'
    replacement = f'<tbody id="breaksTableBody">\n{new_table_rows}\n                </tbody>'
    html_content = re.sub(pattern, replacement, html_content)
    
    with open(html_file, 'w') as f:
        f.write(html_content)

def main():
    """Main function"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, 'FNC_Dropped_Breaks.csv')
    html_file = os.path.join(script_dir, 'broadcast_tracker.html')
    
    # Check if files exist
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found!")
        return
    
    # Parse entries
    entries = parse_csv(csv_file)
    
    if not entries:
        print("No broadcast entries found in FNC_Dropped_Breaks.csv")
        return
    
    # Get unique dates
    unique_dates = get_unique_dates(entries)
    first_date = unique_dates[0] if unique_dates else "2026-01-28"
    
    # Update HTML
    update_html(html_file, entries)
    
    # Update the default date in HTML to first available date
    with open(html_file, 'r') as f:
        html_content = f.read()
    
    # Update the default date in the date picker
    html_content = re.sub(
        r'<input type="date" id="filterDate" value="[^"]*">',
        f'<input type="date" id="filterDate" value="{first_date}">',
        html_content
    )
    
    # Update the reset button to use first date
    html_content = re.sub(
        r'document\.getElementById\(\'filterDate\'\)\.value = "[^"]*";\s*updateTally\("[^"]*"\);',
        f'document.getElementById(\'filterDate\').value = "{first_date}";\n            updateTally("{first_date}");',
        html_content
    )
    
    # Update the initialization to use first date
    html_content = re.sub(
        r'// Initialize with default date\s*updateTally\("[^"]*"\);',
        f'// Initialize with default date\n        updateTally("{first_date}");',
        html_content
    )
    
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    # Print results
    print(f"✓ Successfully updated broadcast_tracker.html")
    print(f"✓ Parsed {len(entries)} broadcast entries from FNC_Dropped_Breaks.csv")
    print(f"✓ Found {len(unique_dates)} unique dates: {', '.join(unique_dates)}")
    print(f"✓ Default date set to: {first_date}")
    print(f"✓ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nEntries found:")
    for i, entry in enumerate(entries, 1):
        print(f"  {i}. {entry.get('program', 'Unknown')} - {entry.get('breakDropped', 'Unknown')}")

if __name__ == "__main__":
    main()
