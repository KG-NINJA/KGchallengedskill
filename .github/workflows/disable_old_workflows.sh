#!/bin/bash
# =======================================================
# 🧩 AIEO Workflow Cleaner
# 旧版AIEOワークフローを自動で無効化（disabled: true追記）
# 対象: aieo_*.yml / AIEO_*.yml
# =======================================================

set -e

TARGET_DIR=".github/workflows"

echo "🔍 Searching for old workflows in $TARGET_DIR..."

for file in "$TARGET_DIR"/*.yml; do
  filename=$(basename "$file")

  # 残すべきファイルを除外
  if [[ "$filename" == "aieo_master_pipeline.yml" ]] || \
     [[ "$filename" == "noroshi"* ]] || \
     [[ "$filename" == "pages-build-deployment"* ]]; then
    echo "✅ Skipping (keep active): $filename"
    continue
  fi

  # 既に無効化済みならスキップ
  if grep -q "^disabled:" "$file"; then
    echo "⚠️ Already disabled: $filename"
    continue
  fi

  # 先頭に disabled: true を追記
  echo "🚫 Disabling: $filename"
  sed -i '1i disabled: true' "$file"
done

# Git commit & push
echo "🌀 Committing changes..."
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"
git add .github/workflows/*.yml
git commit -m "🧹 Auto-disabled old AIEO workflows" || echo "No changes to commit"
git push

echo "✅ Completed: All legacy workflows safely disabled."
