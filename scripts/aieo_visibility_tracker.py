import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import random
import os

# --- Configuration ---
LOG_FILE = 'aieo_visibility_log.csv'
SEARCH_TERMS = {
    'KGNINJA': 'KGNINJA',
    'KGNINJA AI': 'KGNINJA AI',
    'FuwaCoco': 'FuwaCoco',
    'Psycho-Frame': 'Psycho-Frame',
    'AIEO': 'AIEO'
}
COLUMNS = ['Timestamp'] + list(SEARCH_TERMS.keys()) + ['Duration', 'Status', 'Notes']

# --- Simulated Data Generation ---
def run_search_pulse():
    """Simulates the search process and returns a dictionary of results."""
    print("🚀 Running AIEO Visibility Pulse (Ultra Enhanced Mode)")
    
    results = {}
    start_time = time.time()
    
    # Simulate search results and logging
    for term, query in SEARCH_TERMS.items():
        # Generate some hits and duration (simulated)
        hits = random.randint(100, 20000000)
        duration = round(random.uniform(0.2, 0.4), 2)
        
        # Print the success message as seen in your output
        print(f"✅ {term}: {hits:,} hits ({duration}s)")
        
        results[term] = hits
        
    end_time = time.time()
    total_duration = round(end_time - start_time, 2)
    
    return results, total_duration

def append_to_log(results, duration):
    """Appends the latest search results to the CSV log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create the data row
    data_row = [timestamp] + [results[term] for term in SEARCH_TERMS] + [duration, 'Success', 'Automated Check']
    
    # Format the row as a single comma-separated string
    log_line = ','.join(map(str, data_row)) + '\n'

    # Check if file exists to decide on writing headers
    write_header = not os.path.exists(LOG_FILE)
    
    with open(LOG_FILE, 'a') as f:
        if write_header:
            f.write(','.join(COLUMNS) + '\n')
        f.write(log_line)
    
    print(f"\nLog updated in {LOG_FILE}")
    # Print the AIEO log line to match your original output format
    print(f"✅ {'AIEO':<10}: {results.get('AIEO', 0):,} hits ({duration}s)")


# --- Main Logic (The function that failed in your traceback) ---
def plot_dual_axis_chart():
    """
    Reads the log file and plots a dual-axis chart.
    Contains the fix for the pandas.errors.ParserError.
    """
    print(f"\n📊 Generating chart from {LOG_FILE}...")
    try:
        # --- FIX FOR ParserError ---
        # The 'on_bad_lines='skip'' argument handles rows with too many/few columns,
        # preventing the "Expected 9 fields in line 7, saw 12" error.
        df = pd.read_csv(LOG_FILE, on_bad_lines='skip')
        # ---------------------------

        # Convert Timestamp to datetime objects for plotting
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # --- Data Preparation ---
        primary_columns = ['Psycho-Frame', 'AIEO']
        secondary_columns = ['KGNINJA', 'KGNINJA AI', 'FuwaCoco']
        
        # --- Plotting ---
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Primary Axis (ax1) - Visibility terms with large counts
        ax1.set_xlabel('Date')
        ax1.set_ylabel('High Visibility (Hits)', color='tab:blue')
        
        for col in primary_columns:
            ax1.plot(df['Timestamp'], df[col], label=col, marker='o')
            
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Secondary Axis (ax2) - Visibility terms with small counts
        ax2 = ax1.twinx()  # Shared x-axis
        ax2.set_ylabel('Low Visibility (Hits)', color='tab:red')
        
        for col in secondary_columns:
            ax2.plot(df['Timestamp'], df[col], label=col, marker='x', linestyle='--')
            
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # --- Final Touches ---
        fig.tight_layout() 
        plt.title('AIEO Visibility Tracker Over Time')
        
        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # Save and show the plot
        plt.savefig('aieo_visibility_tracker.png')
        print("✅ Chart saved as aieo_visibility_tracker.png")
        
    except FileNotFoundError:
        print(f"❌ Error: Log file '{LOG_FILE}' not found. Run the script once to create it.")
    except Exception as e:
        print(f"❌ An unexpected error occurred during plotting: {e}")


def main():
    """Main execution function."""
    # 1. Run the simulated search process
    results, duration = run_search_pulse()

    # 2. Append the results to the log file
    append_to_log(results, duration)
    
    # 3. Generate the chart (This is the section that was failing)
    plot_dual_axis_chart()

if __name__ == "__main__":
    main()
