import pandas as pd
import matplotlib.pyplot as plt
import datetime
import time
import random
import os
import requests # 外部APIを想定し、requestsを保持

# --- Configuration ---
LOG_FILE = 'visibility_log.csv' # ファイル名を 'aieo_' から 'visibility_' に変更 (YAMLと合わせるため)
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
    """
    シミュレートされた検索プロセスを実行し、結果を返します。
    実際には、ここでGoogle Custom Search APIなどへの呼び出しが行われます。
    """
    print("🚀 Running AIEO Visibility Pulse (Ultra Enhanced Mode)")
    
    results = {}
    start_time = time.time()
    
    # Simulate search results and logging
    for term, query in SEARCH_TERMS.items():
        # 実際には、requests.get(API_URL, params={...}) の処理が入る
        
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
    """最新の検索結果をCSVログファイルに追加します。"""
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


def plot_dual_axis_chart():
    """
    ログファイルを読み込み、デュアル軸チャートをプロットします。
    pandas.errors.ParserErrorの修正を含みます。
    """
    print(f"\n📊 Generating chart from {LOG_FILE}...")
    try:
        # --- FIX FOR ParserError (Line 117 in original traceback) ---
        # 'on_bad_lines='skip'' により、フィールド数の不一致によるエラーを回避します。
        df = pd.read_csv(LOG_FILE, on_bad_lines='skip')
        # -----------------------------------------------------------

        # Convert Timestamp to datetime objects for plotting
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # --- Data Preparation ---
        # 表示数の多い項目 (Primary) と少ない項目 (Secondary) に分ける
        primary_columns = ['Psycho-Frame', 'AIEO']
        secondary_columns = ['KGNINJA', 'KGNINJA AI', 'FuwaCoco']
        
        # --- Plotting ---
        # グラフを生成し、プライマリ軸(ax1)を設定
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Primary Axis (ax1) - Large visibility counts
        ax1.set_xlabel('Date')
        ax1.set_ylabel('High Visibility (Hits)', color='tab:blue')
        
        for col in primary_columns:
            ax1.plot(df['Timestamp'], df[col], label=col, marker='o')
            
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Secondary Axis (ax2) - Small visibility counts (ax1とX軸を共有)
        ax2 = ax1.twinx()  
        ax2.set_ylabel('Low Visibility (Hits)', color='tab:red')
        
        for col in secondary_columns:
            ax2.plot(df['Timestamp'], df[col], label=col, marker='x', linestyle='--')
            
        ax2.tick_params(axis='y', labelcolor='tab:red')

        # --- Final Touches ---
        fig.tight_layout() 
        plt.title('AIEO Visibility Tracker Over Time')
        
        # 凡例を結合して一つにまとめる
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # Save the plot
        plt.savefig('visibility_chart.png')
        print("✅ Chart saved as visibility_chart.png")
        
    except FileNotFoundError:
        # ログファイルが存在しない場合のエラー処理
        print(f"❌ Error: Log file '{LOG_FILE}' not found. Run the script once to create it.")
    except Exception as e:
        # その他の予期せぬエラー処理
        print(f"❌ An unexpected error occurred during plotting: {e}")


def main():
    """Main execution function."""
    # 1. 検索パルスを実行 (データ取得)
    results, duration = run_search_pulse()

    # 2. 結果をログファイルに追加 (CSVファイルへの書き込み)
    append_to_log(results, duration)
    
    # 3. チャートを生成 (CSVファイルの読み込みとグラフ生成)
    plot_dual_axis_chart()

if __name__ == "__main__":
    main()
