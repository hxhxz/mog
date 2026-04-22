# @mog/shared

前后端共享契约。

- `pipelines.schema.json` — 9 个 Pipeline 的输入输出 JSON Schema（PRD §4.1/§4.2）
- `context.schema.json` — 项目级 Context 结构（PRD §3.3）

## 生成类型

后续可用 `json-schema-to-typescript` 生成 TS 类型，用 `datamodel-code-generator` 生成 Pydantic 类，避免前后端契约漂移。
