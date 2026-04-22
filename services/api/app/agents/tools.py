"""每个 Pipeline 对应一个 smolagents @tool 定义（薄封装，实际 agent 在 services/agent）.

这里定义的是 **JSON Schema 契约**，services/agent 侧用 smolagents `@tool` 装饰器把它们转成可调用工具。
"""
from app.pipelines.registry import PIPELINE_REGISTRY


def list_tool_schemas() -> list[dict]:
    """返回所有 Pipeline 的工具描述，供 Agent 启动时注册."""
    return [
        {
            "name": name,
            "description": (cls.__doc__ or "").strip().split("\n")[0],
            "endpoint": cls.endpoint,
            "priority": cls.default_priority,
        }
        for name, cls in PIPELINE_REGISTRY.items()
    ]
