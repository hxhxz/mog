#!/usr/bin/env bash
# mog 开发环境初始化脚本
# 用法：bash scripts/bootstrap.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "[1/4] 准备 .env"
if [ ! -f "infra/env/.env" ]; then
  cp infra/env/.env.example infra/env/.env
  echo "  → 已从 .env.example 生成 infra/env/.env，请按需修改 OSS / LLM 密钥"
else
  echo "  → infra/env/.env 已存在，跳过"
fi

echo "[2/4] 构建 Docker 镜像"
docker compose -f infra/docker-compose.yml --env-file infra/env/.env build

echo "[3/4] 启动依赖服务 (postgres / redis)"
docker compose -f infra/docker-compose.yml --env-file infra/env/.env up -d postgres redis

echo "[4/4] 执行 DB 迁移 + 种子数据"
docker compose -f infra/docker-compose.yml --env-file infra/env/.env run --rm api alembic upgrade head
docker compose -f infra/docker-compose.yml --env-file infra/env/.env run --rm api python -m scripts.seed

echo ""
echo "✔ bootstrap 完成。运行 'make up' 启动全栈，或直接访问："
echo "    - 前端:   http://localhost:5173"
echo "    - API:    http://localhost:8000/docs"
echo "    - Flower: http://localhost:5555"
