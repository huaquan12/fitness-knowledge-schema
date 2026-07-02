#!/bin/bash
# sync-skill.sh — 同步仓库中的 SKILL.md 到 CatPaw Skill 部署目录
# Usage: bash scripts/sync-skill.sh [--workspace]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
SOURCE_FILE="$REPO_DIR/SKILL.md"

# 默认部署到全局 Skill 目录
TARGET_DIR="$HOME/.catpaw/skills/fitness-knowledge-schema"

# 如果传入 --workspace，部署到项目级 Skill 目录
if [[ "${1:-}" == "--workspace" ]]; then
  TARGET_DIR="$REPO_DIR/.catpaw/skills/fitness-knowledge-schema"
fi

if [[ ! -f "$SOURCE_FILE" ]]; then
  echo "❌ 源文件不存在: $SOURCE_FILE"
  exit 1
fi

mkdir -p "$TARGET_DIR"
cp "$SOURCE_FILE" "$TARGET_DIR/SKILL.md"
echo "✅ SKILL.md 已同步到: $TARGET_DIR/SKILL.md"
echo "   版本: $(grep '^version:' "$SOURCE_FILE" | head -1 | awk '{print $2}')"
