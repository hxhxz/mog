"""smolagents 模板工具 — 运行时从 API 拉取模板列表，动态生成 @tool 函数."""
from __future__ import annotations
import os
from typing import Any

import httpx

API_BASE = os.environ.get("API_BASE_URL", "http://api:8000")


def load_template_tools() -> list:
    """拉取 published 模板并返回 smolagents tool 函数列表.

    在 agent 启动时调用一次。API 不可用时返回空列表，不中断 agent 启动。
    """
    try:
        from smolagents import tool as smolagents_tool
    except ImportError:
        return []

    try:
        resp = httpx.get(f"{API_BASE}/api/v1/templates", timeout=5.0)
        templates: list[dict[str, Any]] = resp.json() if resp.status_code == 200 else []
    except Exception:
        templates = []

    tools = []
    for tpl in templates:
        if not tpl.get("is_mcp_exposed", True):
            continue
        tools.append(_make_smolagents_tool(tpl, smolagents_tool))
    return tools


def _make_smolagents_tool(tpl: dict[str, Any], smolagents_tool):
    tpl_id = tpl["id"]
    tpl_name = tpl["name"]
    tpl_desc = tpl.get("description") or tpl_name
    pipeline = tpl.get("pipeline", "")
    input_nodes = tpl.get("input_nodes", [])

    def _invoke(project_id: str, materials: dict[str, Any], priority: str = "realtime") -> dict[str, Any]:
        resp = httpx.post(
            f"{API_BASE}/api/v1/templates/{tpl_id}/invoke",
            json={"project_id": project_id, "materials": materials, "priority": priority},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()

    _invoke.__name__ = f"use_{tpl_id.replace('-', '_')}"
    _invoke.__doc__ = (
        f"{tpl_desc}\n"
        f"Pipeline: {pipeline}. Input nodes: {', '.join(input_nodes)}.\n"
        "Args:\n"
        "    project_id (str): 所属项目 ID。\n"
        "    materials (dict): ComfyUI 节点覆写，key 格式 '{node_id}.inputs.{field}'。\n"
        "    priority (str): 'realtime' 或 'background'。\n"
    )

    return smolagents_tool(_invoke)
