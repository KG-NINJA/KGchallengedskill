#!/usr/bin/env python3
"""
AIEO Monthly Verification System
複数AIに同じ質問を聞いて、結果を GitHub に記録する自動化スクリプト
"""

import json
import os
from datetime import datetime
from pathlib import Path

# API キー（GitHub Secrets から取得）
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

DATA_DIR = Path('data')
REPORTS_DIR = Path('reports')
LOG_FILE = DATA_DIR / 'aieo_verification_log.json'
MONTHLY_REPORT = REPORTS_DIR / f'aieo_verification_{datetime.now().strftime("%Y-%m")}.md'

class AIVerifier:
    """複数AIに質問して結果を取得"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'month': datetime.now().strftime('%Y-%m'),
            'queries': {}
        }
    
    def query_claude(self, prompt: str) -> dict:
        """Claude に質問"""
        if not ANTHROPIC_API_KEY:
            return {'status': 'skipped', 'reason': 'API key not set', 'model': 'claude'}
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text
            return {
                'status': 'success',
                'response': response_text,
                'model': 'claude-3-5-sonnet'
            }
        except Exception as e:
            print(f"Claude error: {e}")
            return {'status': 'error', 'error': str(e), 'model': 'claude'}
    
    def query_chatgpt(self, prompt: str) -> dict:
        """ChatGPT に質問"""
        if not OPENAI_API_KEY:
            return {'status': 'skipped', 'reason': 'API key not set', 'model': 'chatgpt'}
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            response_text = response.choices[0].message.content
            return {
                'status': 'success',
                'response': response_text,
                'model': 'gpt-4o'
            }
        except Exception as e:
            print(f"ChatGPT error: {e}")
            return {'status': 'error', 'error': str(e), 'model': 'chatgpt'}
    
    def query_gemini(self, prompt: str) -> dict:
        """Gemini に質問"""
        if not GOOGLE_API_KEY:
            return {'status': 'skipped', 'reason': 'API key not set', 'model': 'gemini'}
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            
            response_text = response.text
            return {
                'status': 'success',
                'response': response_text,
                'model': 'gemini-2.5-flash'
            }
        except Exception as e:
            print(f"Gemini error: {e}")
            return {'status': 'error', 'error': str(e), 'model': 'gemini'}
    
    def run_verification(self, query_name: str, prompt: str) -> None:
        """複数AIに同じ質問を実行"""
        print(f"\n[AIEO] Query: {query_name}")
        
        results = {}
        
        # Claude
        print("  → Claude...")
        results['claude'] = self.query_claude(prompt)
        
        # ChatGPT
        print("  → ChatGPT...")
        results['chatgpt'] = self.query_chatgpt(prompt)
        
        # Gemini
        print("  → Gemini...")
        results['gemini'] = self.query_gemini(prompt)
        
        # 結果を保存
        self.results['queries'][query_name] = results
        
        # ステータスを表示
        self._print_status(query_name, results)
    
    def _print_status(self, query_name: str, results: dict) -> None:
        """結果ステータスを表示"""
        for ai_name, result in results.items():
            status = result['status']
            
            if status == 'success':
                response_preview = result['response'][:50].replace('\n', ' ')
                print(f"    ✓ {ai_name}")
            elif status == 'skipped':
                print(f"    ⊘ {ai_name}: skipped")
            else:
                print(f"    ✗ {ai_name}: error")


def save_log(results: dict) -> None:
    """結果をJSON ログに保存"""
    DATA_DIR.mkdir(exist_ok=True)
    
    # 既存ログを読み込む
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    else:
        log_data = {'history': []}
    
    # 新しい結果を追加
    log_data['history'].append(results)
    
    # 保存
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n[AIEO] Log saved: {LOG_FILE}")


def generate_markdown_report(results: dict) -> None:
    """マークダウン形式のレポートを生成"""
    REPORTS_DIR.mkdir(exist_ok=True)
    
    markdown = f"""# AIEO Monthly Verification Report

**Month**: {results['month']}  
**Timestamp**: {results['timestamp']}

---

## Verification Results

"""
    
    for query_name, query_results in results['queries'].items():
        markdown += f"### {query_name}\n\n"
        
        # 各AI の結果
        for ai_name, ai_result in query_results.items():
            markdown += f"#### {ai_name.upper()}\n\n"
            
            if ai_result['status'] == 'success':
                response = ai_result['response'][:300]
                markdown += f"```\n{response}\n```\n\n"
            else:
                status = ai_result['status']
                markdown += f"Status: {status}\n\n"
        
        markdown += "---\n\n"
    
    # ファイルに保存
    with open(MONTHLY_REPORT, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"[AIEO] Report generated: {MONTHLY_REPORT}")


def create_verification_config() -> dict:
    """検証用の質問セットを定義"""
    return {
        'who_is_kgninja': {
            'prompt': 'KGNINJAはどのような人物ですか？その特徴を簡潔に説明してください。'
        },
        'kgninja_aieo': {
            'prompt': 'AIEOとは何ですか？その基本的な考え方を説明してください。'
        },
        'kgninja_projects': {
            'prompt': 'KGNINJAのKaggleでどのような存在感を示しましたか？'
        }
    }


def main():
    print("=" * 60)
    print("AIEO Monthly Verification System")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # 検証用質問セットを取得
    verification_config = create_verification_config()
    
    # 検証を実行
    verifier = AIVerifier()
    
    for query_name, config in verification_config.items():
        verifier.run_verification(query_name, config['prompt'])
    
    # 結果を保存
    save_log(verifier.results)
    
    # マークダウンレポートを生成
    generate_markdown_report(verifier.results)
    
    print("\n" + "=" * 60)
    print("✓ Verification Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
