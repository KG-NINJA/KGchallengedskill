import csv
import os
from datetime import datetime

def analyze_visibility_log():
    """visibility_log.csvからデータを読み取り、正確に分析する"""
    
    log_file = 'visibility_log.csv'
    
    if not os.path.exists(log_file):
        print(f"❌ Error: {log_file} not found.")
        return
    
    print(f"📊 Running Composite Index Analysis from {log_file}...")
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # まずヘッダーを確認
            first_line = f.readline().strip()
            print(f"📋 Detected columns: {first_line}")
            
            # ファイルの先頭に戻る
            f.seek(0)
            
            reader = csv.DictReader(f)
            rows = list(reader)
            
            if not rows:
                print("❌ Error: CSV file is empty or has no data rows.")
                return
            
            # 実際の列名を表示
            actual_columns = list(rows[0].keys())
            print(f"✅ Found {len(actual_columns)} columns: {', '.join(actual_columns)}")
            print(f"✅ Total {len(rows)} data rows found.\n")
            
            # キーワード列を探す（柔軟に対応）
            keyword_columns = []
            for col in actual_columns:
                col_lower = col.lower()
                if 'keyword' in col_lower or 'term' in col_lower or 'query' in col_lower:
                    keyword_columns.append(col)
            
            if not keyword_columns:
                print("⚠️  No keyword columns found. Showing all available data:")
                print("\n--- First 5 rows of data ---")
                for i, row in enumerate(rows[:5], 1):
                    print(f"\nRow {i}:")
                    for key, value in row.items():
                        if value:  # 空でない値のみ表示
                            print(f"  {key}: {value}")
                return
            
            print(f"🔍 Keyword columns found: {', '.join(keyword_columns)}\n")
            
            # 各キーワード列のデータを分析
            for kw_col in keyword_columns:
                print(f"\n{'='*60}")
                print(f"Analysis for column: {kw_col}")
                print('='*60)
                
                # データを集計
                keyword_data = {}
                for row in rows:
                    keyword = row.get(kw_col, '').strip()
                    if not keyword:
                        continue
                    
                    if keyword not in keyword_data:
                        keyword_data[keyword] = {
                            'count': 0,
                            'positions': [],
                            'dates': []
                        }
                    
                    keyword_data[keyword]['count'] += 1
                    
                    # 順位データがあれば収集
                    for col in actual_columns:
                        if 'position' in col.lower() or 'rank' in col.lower():
                            pos = row.get(col, '')
                            if pos:
                                try:
                                    keyword_data[keyword]['positions'].append(int(pos))
                                except ValueError:
                                    pass
                    
                    # 日付データがあれば収集
                    for col in actual_columns:
                        if 'date' in col.lower() or 'time' in col.lower():
                            date = row.get(col, '')
                            if date:
                                keyword_data[keyword]['dates'].append(date)
                
                # 結果を表示
                print(f"\n📈 Summary for {kw_col}:")
                print(f"Total unique keywords: {len(keyword_data)}")
                
                if keyword_data:
                    print("\n--- Top Keywords by Frequency ---")
                    sorted_keywords = sorted(keyword_data.items(), 
                                           key=lambda x: x[1]['count'], 
                                           reverse=True)
                    
                    for keyword, data in sorted_keywords[:10]:
                        print(f"\n🔑 {keyword}")
                        print(f"   Occurrences: {data['count']}")
                        
                        if data['positions']:
                            avg_pos = sum(data['positions']) / len(data['positions'])
                            best_pos = min(data['positions'])
                            print(f"   Average Position: {avg_pos:.1f}")
                            print(f"   Best Position: {best_pos}")
                        
                        if data['dates']:
                            print(f"   First seen: {data['dates'][0]}")
                            print(f"   Last seen: {data['dates'][-1]}")
            
            # 全データの統計
            print(f"\n{'='*60}")
            print("Overall Statistics")
            print('='*60)
            print(f"Total rows analyzed: {len(rows)}")
            print(f"Date range: {rows[0].get('date', 'N/A')} to {rows[-1].get('date', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Analysis complete.")

if __name__ == "__main__":
    analyze_visibility_log()
