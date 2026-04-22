# mog 架构文档

## 数据流 (PRD §5.2)

```
用户输入 (前端)
    ↓ WebSocket /api/v1/agent/ws/{project_id}
FastAPI (services/api)
    ↓ HTTP → services/agent (smolagents)
    ↓   LLM 意图分类 → Template Tool 调用 (首选) / Pipeline Tool 调用 (兜底)
    ↓ HTTP ← TemplateService.invoke(template_id, materials)
    ↓          → _apply_materials(workflow, materials)   # 将素材注入 ComfyUI workflow JSON
    ↓          → JobService.submit(pipeline, inputs={workflow,...}, priority)
    ↓ DB: 写 pipeline_jobs 行
    ↓ Celery apply_async → queue_realtime | queue_background
services/worker
    ↓ run_pipeline(job_id) → 读 job.inputs.workflow → pipeline_client.submit_workflow(workflow)
    ↓ POST ComfyUI /prompt → 写 本地存储
    ↓ notifier.progress/status → Redis Pub/Sub "chan:project:*"
services/api WSManager 订阅 → broadcast → 前端预览区更新
```

## 用户旅程时序图
```mermaid
sequenceDiagram
    actor User
    participant Web
    participant API
    participant Agent
    participant Worker
    participant ComfyUI
    participant DB

    User->>Web: 创建 Project
    Web->>API: POST /projects
    API->>DB: 插入 Project + 6 条 ProjectStep(PENDING)

    rect rgb(230, 240, 255)
    Note over User,DB: Step 1-2:SCRIPT / STORYBOARD(Agent 生成 → 人工 REVIEW)
    User->>Web: 开始 SCRIPT
    Web->>API: POST /projects/{id}/steps/script/start
    API->>Agent: /agent/infer (intent=script)
    Agent->>Agent: LLM 生成剧本
    Agent-->>API: outputs
    API->>DB: step.status = REVIEW
    API-->>Web: 200 outputs
    User->>Web: 确认
    Web->>API: POST .../script/confirm
    API->>DB: step.status = DONE
    Note over Web,DB: STORYBOARD 同上模式
    end

    rect rgb(255, 245, 230)
    Note over User,DB: Step 3-6:流水线生成(Celery + ComfyUI)
    User->>Web: 开始 TEXT2IMAGE
    Web->>API: POST .../text2image/start
    API->>DB: 创建 PipelineJob(chain_id)
    API->>Worker: Celery apply_async(mog.pipeline.run)
    Worker->>ComfyUI: POST /prompt (template workflow)
    loop 轮询
        Worker->>ComfyUI: GET /history/{id}
        Worker-->>Web: WebSocket progress
    end
    ComfyUI-->>Worker: outputs
    Worker->>DB: PipelineJob.DONE + step.outputs
    Worker->>Worker: mog.chain.advance_children
    Note over Worker,DB: 依次触发 IMAGE2VIDEO → CONCAT → AUDIO<br/>(parent_job_id DAG)
    end

    rect rgb(255, 230, 230)
    Note over User,DB: 修改分支:级联重置下游
    User->>Web: modify(storyboard)
    Web->>API: POST .../storyboard/modify
    API->>DB: storyboard.outputs 更新<br/>text2image/image2video/concat/audio → PENDING
    API-->>Web: 全量 6 步状态
    end
```


## 数据模型

```mermaid
erDiagram
    PROJECT ||--o{ PROJECT_STEP : "1:6"
    PROJECT ||--o{ PIPELINE_JOB : has
    PROJECT ||--o{ CHARACTER : has
    PROJECT ||--o{ SEGMENT : has
    PROJECT ||--o{ ASSET : produces
    TEMPLATE ||--o{ PIPELINE_JOB : instantiates
    PIPELINE_JOB ||--o{ PIPELINE_JOB : "parent_job_id (DAG)"

    PROJECT {
        uuid id PK
        string title
        jsonb context_json
        string style_lora
        string audio_track
        datetime created_at
    }
    PROJECT_STEP {
        uuid id PK
        uuid project_id FK
        enum step "SCRIPT|STORYBOARD|TEXT2IMAGE|IMAGE2VIDEO|CONCAT|AUDIO"
        enum status "PENDING|RUNNING|REVIEW|DONE|FAILED"
        jsonb outputs_json
        string chain_id
    }
    PIPELINE_JOB {
        uuid id PK
        uuid project_id FK
        uuid template_id FK "nullable"
        enum pipeline "9 种 P0/P1"
        enum status
        float progress
        uuid parent_job_id FK "自引用"
        string chain_id
        jsonb inputs_json
        jsonb outputs_json
    }
    TEMPLATE {
        uuid id PK
        enum pipeline
        jsonb workflow_json
        jsonb materials_schema
        string category
        bool published
    }
    CHARACTER {
        uuid id PK
        uuid project_id FK
        string name
        string reference_image_url
        string lora_id
    }
    SEGMENT {
        uuid id PK
        uuid project_id FK
        int order
        text content
        string image_url
        string video_url
    }
    ASSET {
        uuid id PK
        uuid project_id FK
        enum kind "image|video|audio"
        string url
        jsonb meta_json
    }
```

## 模板层

```
管理员 / 前端
    POST /api/v1/templates          # 导入 ComfyUI workflow JSON
    PATCH /api/v1/templates/{id}    # 更新元数据（名称/分类/is_mcp_exposed）
    DELETE /api/v1/templates/{id}

Agent / 前端
    GET  /api/v1/templates          # 列出所有 published 模板
    GET  /api/v1/templates/{id}     # 获取含 workflow JSON 的详情
    POST /api/v1/templates/{id}/invoke
         body: { project_id, materials: {"6.inputs.text": "..."}, priority }
         → TemplateService._apply_materials() 覆写 workflow 节点 inputs
         → JobService.submit() 投递 Celery 任务
```

### Template 数据结构

```json
{
  "id": "tpl_abc123",
  "name": "古装国风人物立绘",
  "pipeline": "text2image",
  "workflow": { "/* ComfyUI /prompt API JSON 原样存储 */": {} },
  "input_nodes": ["6", "12"],
  "is_mcp_exposed": true
}
```

`workflow` 字段由 ComfyUI 定义，平台不自定义 schema。
workflow示例如下：
![alt text](image.png)
`input_nodes` 仅用于 Agent/前端展示"此模板需要哪些输入"，执行时实际合并由 `_apply_materials` 完成。

### materials 合并规则

key 格式：`"{node_id}.inputs.{field}"`

```python
# 例：覆写 node 6 的正向 prompt + node 12 的参考图
materials = {
    "6.inputs.text":  "一个身着汉服的古装女子，背景是竹林",
    "12.inputs.image": "oss://bucket/ref/character_01.png",
}
```

## MCP Server

```
services/agent
├── app/mcp_server.py    — FastMCP 工具定义
└── app/mcp_main.py      — uvicorn 入口，端口 8101
```

端口 8101 暴露 HTTP/SSE MCP 协议，任何 MCP 客户端均可连接。

**固定工具**：
| Tool | 说明 |
|---|---|
| `list_templates` | 列出模板（可按 pipeline/category 过滤） |
| `invoke_template` | 用 template_id + materials 提交任务 |
| `get_job_status` | 查询任务进度 |

**动态工具**：启动时从 API 拉取 `is_mcp_exposed=true` 的模板，每个模板生成
`use_{template_id}(project_id, materials, priority)` 工具，让 Agent 可按模板名直接调用。

**Claude Desktop 接入配置**：
```json
{
  "mcpServers": {
    "mog-templates": {
      "transport": "sse",
      "url": "http://localhost:8101/sse"
    }
  }
}
```

## 任务队列管理

### 状态机

```
          ┌────────────────┐
          │  pending       │
          └───────┬────────┘
                  │ submit
     ┌────────────┼────────────┐
     ▼                          ▼
waiting_parent              queued ──────► running
     │                          │             │
     │ parent success           │             ├─► success
     └──► queued                │             ├─► failed
                                │             └─► canceling ──► canceled
                                ▼
                             canceled (直接取消 queued)
```

### 队列路由

| 队列 | 并发 | 典型 Pipeline |
|---|---|---|
| `queue_realtime` | GPU 卡数 × 1.0 | text2image / character2image / image2video / keyframe2video / talk2video / concat / tts_align / inpainting |
| `queue_background` | GPU 卡数 × 0.5 | upscale / character_lora_training / postprocess |

### DAG 示例 (PRD §4.3)

广告创作链：
```
text2image (3 张分镜)
    ↓
character2image (修正脸)    ← 仅当用户说「脸不对」
    ↓
inpainting (改背景)          ← 仅当用户说「背景太杂」
    ↓
image2video × 3  ─────────┐
    ↓                      │
keyframe2video (转场衔接) ──┤
    ↓                      │
upscale × 3 (background) ──┤
    ↓                      │
concat + tts_align ─────────┘
```

JobService.chain() 一次性创建所有 job，按 `depends_on` 自动调度。

## 服务端口一览

| 服务 | 端口 | 说明 |
|---|---|---|
| web | 5173 | React 前端 |
| api | 8000 | FastAPI 主服务 |
| agent | 8100 | smolagents chat 服务 |
| mcp | 8101 | MCP SSE server（模板工具） |
| comfyui | 8188 | ComfyUI（MVP 为 nginx 占位） |
| flower | 5555 | Celery 监控 |
| postgres | 5432 | PostgreSQL |
| redis | 6379 | Redis broker + Pub/Sub |
