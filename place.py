import csv
import sys
import time
from datetime import datetime
from collections import Counter

DATA_FILE_PATH = '2022_place_canvas_history.csv'

def analyze_rplace(start_str, end_str, file_path=DATA_FILE_PATH):
    # Parse input times into datetime objects
    try:
        start_time = datetime.strptime(start_str, "%Y-%m-%d %H")
        end_time = datetime.strptime(end_str, "%Y-%m-%d %H")
    except ValueError:
        print("Error: Use format 'YYYY-MM-DD HH'")
        return

    if end_time <= start_time:
        print("Error: End hour must be after start hour.")
        return

    # Begin performance timing, initialize counters, and row tracking
    start_perf = time.perf_counter_ns()
    color_counts = Counter()
    pixel_counts = Counter()
    rows_matched = 0
    total_rows_processed = 0 
    # Track progress through the massive file so I know it's not frozen

    try:
        # utf-8-sig handles potential BOM from Windows/Excel
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            print(f"Starting full scan of {file_path}...")
            
            for row in reader:
                total_rows_processed += 1
                
                # Progress bar: Prints every 5 million rows so you know it's not frozen
                if total_rows_processed % 5000000 == 0:
                    print(f"Progress: {total_rows_processed // 1000000}M rows scanned...")

                try:
                    ts_hour_part = row['timestamp'][:13]
                    row_time = datetime.strptime(ts_hour_part, "%Y-%m-%d %H")

                    if start_time <= row_time < end_time:
                        color_counts[row['pixel_color']] += 1
                        pixel_counts[row['coordinate']] += 1
                        rows_matched += 1
                    
                    # Should not assume sorted data; hence, no early break
                    # elif row_time >= end_time:
                    #     break
                        
                except (ValueError, KeyError):
                    continue

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return

    # Calculate total execution time
    execution_time_ms = (time.perf_counter_ns() - start_perf) // 1_000_000

    print(f"\n--- Final Results ---")
    print(f"Timeframe: {start_str} to {end_str}")
    print(f"Execution Time: {execution_time_ms} ms")
    print(f"Total Rows Scanned: {total_rows_processed}")
    print(f"Rows Matched: {rows_matched}")
    
    if rows_matched > 0:
        most_pixel_raw = pixel_counts.most_common(1)[0][0]
        clean_index = int(most_pixel_raw.replace(',', ''))
        
        # Convert to (X, Y) assuming 2000px canvas width
        width = 2000
        x = clean_index % width
        y = clean_index // width
        
        formatted_pixel = f"({x}, {y})"
        
        print(f"Most Placed Color: {color_counts.most_common(1)[0][0]}")
        print(f"Most Placed Pixel Location: {formatted_pixel}")
        # Making sure the counters are properly keeping track of top colors and coords
        print(f"Top 3 Colors: {color_counts.most_common(3)}")
        print(f"Top 3 Raw Indices: {pixel_counts.most_common(3)}")
    else:
        print("No data found. Ensure your dates are within the data.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python place.py 2022-04-04 00 2022-04-04 01")
    else:
        start_arg = f"{sys.argv[1]} {sys.argv[2]}"
        end_arg = f"{sys.argv[3]} {sys.argv[4]}"
        analyze_rplace(start_arg, end_arg)