import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Configuration ---
INPUT_LOG_FILE = 'visibility_log.csv'
OUTPUT_LOG_FILE = 'aieo_composite_log.csv'
OUTPUT_CHART_FILE = 'aieo_composite_chart.png'

# 各キーワードの重み付け (Composite Index算出のため)
# AIEOの核となるキーワードに高い重みを与えます。
WEIGHTS = {
    'AIEO': 1.8,          # 最も重要
    'KGNINJA AI': 1.5,    # AI連携で重要
    'KGNINJA': 1.0,       # ベースとなる認知度
    'FuwaCoco': 0.5,      # 関連性の高いエンティティ
    'Psycho-Frame': 0.1   # 競合/コンテキストとしての参照用（低く設定）
}
COMPOSITE_COLUMN = 'AIEO_Composite_Index'

def calculate_composite_index():
    """
    Visibilityログを読み込み、重み付けに基づいて複合インデックスを計算し、
    結果を新しいログファイルに保存します。
    """
    print(f"📊 Running Composite Index Analysis from {INPUT_LOG_FILE}...")
    try:
        # CSVファイルを読み込む。on_bad_lines='skip'で破損した行をスキップし、堅牢性を確保。
        df = pd.read_csv(INPUT_LOG_FILE, on_bad_lines='skip')

        # --- 修正: Timestamp列の堅牢性向上 ---
        # 小文字の 'timestamp' が存在する場合、大文字の 'Timestamp' にリネームする
        if 'timestamp' in df.columns and 'Timestamp' not in df.columns:
            df.rename(columns={'timestamp': 'Timestamp'}, inplace=True)
        
        # 必要な 'Timestamp' 列が存在するか確認
        if 'Timestamp' not in df.columns:
            raise KeyError("The required 'Timestamp' column is missing or incorrectly named in the log file.")
        # -----------------------------------

        # タイムスタンプをdatetime型に変換
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        # 複合インデックスの計算ロジック
        # (重み * totalResults) の合計を計算します。
        df[COMPOSITE_COLUMN] = 0
        
        # DataFrameの列に存在するキーワードのみを処理対象とする
        active_weights = {k: v for k, v in WEIGHTS.items() if k in df.columns}

        if not active_weights:
            print("❌ Error: None of the required keyword columns were found in the log file.")
            # エラー発生時の戻り値を修正し、Noneを2つ返さないように修正
            return None

        for term, weight in active_weights.items():
            # 検索ヒット数を数値型に変換し、NaNを0として扱う
            df[term] = pd.to_numeric(df[term], errors='coerce').fillna(0)
            df[COMPOSITE_COLUMN] += df[term] * weight
            
        print(f"✅ Composite Index calculated using {len(active_weights)} terms.")
        
        # タイムスタンプと複合インデックスのみを抽出
        df_composite = df[['Timestamp', COMPOSITE_COLUMN]].copy()

        # 複合インデックスログを保存
        df_composite.to_csv(OUTPUT_LOG_FILE, index=False)
        print(f"✅ Composite Index saved to {OUTPUT_LOG_FILE}")

        return df_composite

    except FileNotFoundError:
        print(f"❌ Error: Input log file '{INPUT_LOG_FILE}' not found. Aborting analysis.")
        return None
    except KeyError as e:
        # KeyErrorを捕獲し、元のエラーメッセージをより分かりやすくする
        print(f"❌ Data Structure Error: Check the column names in the CSV. {e}")
        return None
    except Exception as e:
        print(f"❌ An unexpected error occurred during composite calculation: {e}")
        return None

def plot_composite_index(df_composite):
    """複合インデックスの時系列グラフを生成します。"""
    if df_composite is None or df_composite.empty:
        print("❌ Cannot plot: Composite data is empty or missing.")
        return

    print("📈 Generating Composite Index Chart...")

    plt.figure(figsize=(12, 6))
    
    # 複合インデックスの値をプロット
    plt.plot(df_composite['Timestamp'], df_composite[COMPOSITE_COLUMN], 
             marker='o', linestyle='-', color='indigo', linewidth=2)
    
    plt.title('AIEO Composite Visibility Index Over Time', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Weighted Visibility Score (Composite Index)', color='indigo', fontsize=12)
    
    # グリッドとレイアウト調整
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    try:
        plt.savefig(OUTPUT_CHART_FILE)
        print(f"✅ Chart saved as {OUTPUT_CHART_FILE}")
    except Exception as e:
        print(f"❌ Error saving chart: {e}")


def main():
    """メイン実行関数"""
    # 1. 複合インデックスの計算
    df_composite = calculate_composite_index()
    
    # 2. グラフのプロット
    if df_composite is not None:
        plot_composite_index(df_composite)
        
    print("\nAnalysis complete.")

if __name__ == "__main__":
    main()
