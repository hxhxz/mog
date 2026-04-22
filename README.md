# AI 短剧视频生成平台 (mog)

Monorepo for the AI-driven short drama / ad video generation platform.
详细产品需求见 [docs/视频生成平台_PRD_v1.0_2.docx](docs/视频生成平台_PRD_v1.0_2.docx)。

## 目录结构

```
apps/web/            # React 前端（三栏布局：导航 / 对话 / 预览）
services/
  api/               # FastAPI 主服务（api/services/repositories/models/schemas 分层）
  worker/            # Celery Worker（双队列：realtime / background）
  agent/             # smolagents Agent 服务（工具调用 + 意图理解）
  comfyui/           # ComfyUI 工作流 JSON + 占位镜像
packages/shared/     # 前后端共享 Pipeline / Context schema
infra/               # docker-compose + 环境变量模板
scripts/             # bootstrap / seed
docs/                # PRD + 架构文档
```

## 快速开始

```bash
cp infra/env/.env.example infra/env/.env
make up                    # 启动全栈
# 或: docker compose -f infra/docker-compose.yml up --build
```

服务端口：

| 服务 | 端口 | 说明 |
|---|---|---|
| web | 5173 | Vite 开发服务器 |
| api | 8000 | FastAPI |
| postgres | 5432 | 数据库 |
| redis | 6379 | Celery broker + WS Pub/Sub |
| comfyui | 8188 | 占位，实际调用时走 API |

## 健康检查

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/pipelines    # 列出 9 个 Pipeline
```

## 核心概念

- **Pipeline**：一个 ComfyUI 工作流的封装（9 个，见 PRD §4.1/§4.2）
- **Context**：项目级结构化上下文（`style_lora / characters[] / segments[] / audio_track`）
- **Job**：一次 Pipeline 调用的任务记录，带优先级、DAG、进度、取消
- **Chain**：一组关联的 Job 组成的 DAG（对应 PRD §4.3 场景）

## 开发命令

```bash
make fmt           # 前后端格式化
make test          # 跑全部单测
make migrate       # 执行 alembic 迁移
make logs          # 跟随日志
make down          # 停止所有服务
```
