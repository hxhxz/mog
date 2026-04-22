"""MCP server — 将模板库暴露为 MCP tools.

运行方式（SSE，供 Claude Desktop / Cursor / 任何 MCP 客户端连接）：
    python -m app.mcp_server          # stdio 模式
    MCP_TRANSPORT=sse uvicorn app.mcp_server:asgi_app --port 8101  # HTTP/SSE 模式

工具清单（固定）：
    list_templates   — 列出所有公开模板（可按 pipeline / category 过滤）
    invoke_template  — 用指定模板 + materials 提交生成任务
    get_job_status   — 查询任务进度

模板工具在运行时动态注册：每个 is_mcp_exposed=True 的模板自动生成一个
`use_{template_id}(project_id, materials, priority)` 工具，
让 Agent 可以直接说「用古装国风立绘模板生成」而不需要知道 template_id。
"""
from __future__ import annotations
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

API_BASE = os.environ.get("API_BASE_URL", "http://api:8000")
TEMPLATES_URL = f"{API_BASE}/api/v1/templates"
JOBS_URL = f"{API_BASE}/api/v1/jobs"

mcp = FastMCP("mog-templates", instructions=(
    "You are connected to the mog video generation platform. "
    "Use list_templates to discover available ComfyUI templates, "
    "then invoke_template to start a generation job."
))


# ─────────────────────────── Fixed tools ───────────────────────────

@mcp.tool()
async def list_templates(pipeline: str = "", category: str = "") -> list[dict[str, Any]]:
    """List available generation templates.

    Args:
        pipeline: Filter by pipeline name (e.g. text2image, image2video). Leave empty for all.
        category: Filter by category (e.g. 人物立绘/古装). Leave empty for all.
    """
    params: dict[str, str] = {}
    if pipeline:
        params["pipeline"] = pipeline
    if category:
        params["category"] = category
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(TEMPLATES_URL, params=params)
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def invoke_template(
    template_id: str,
    project_id: str,
    materials: dict[str, Any],
    priority: str = "realtime",
) -> dict[str, Any]:
    """Invoke a template to start a generation job.

    Args:
        template_id: Template ID from list_templates.
        project_id: Project this job belongs to.
        materials: Node input overrides in ComfyUI format.
                   Keys use "{node_id}.inputs.{field}", e.g. {"6.inputs.text": "古装女子"}.
        priority: "realtime" (user-facing) or "background" (silent, e.g. upscale).
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{TEMPLATES_URL}/{template_id}/invoke",
            json={"project_id": project_id, "materials": materials, "priority": priority},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
async def get_job_status(job_id: str) -> dict[str, Any]:
    """Get current status and progress of a generation job.

    Args:
        job_id: Job ID returned by invoke_template.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{JOBS_URL}/{job_id}/progress")
        resp.raise_for_status()
        return resp.json()


# ─────────────────── Dynamic per-template tools ───────────────────

async def _register_template_tools() -> None:
    """Fetch published templates and register one tool per template.

    Called at startup. Failures are non-fatal — fixed tools remain available.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(TEMPLATES_URL)
            if resp.status_code != 200:
                return
            templates = resp.json()
    except Exception:
        return

    for tpl in templates:
        if not tpl.get("is_mcp_exposed", True):
            continue
        _make_template_tool(tpl)


def _make_template_tool(tpl: dict[str, Any]) -> None:
    tpl_id: str = tpl["id"]
    tpl_name: str = tpl["name"]
    tpl_desc: str = tpl.get("description") or tpl_name
    tool_name = f"use_{tpl_id.replace('-', '_')}"

    async def _tool(project_id: str, materials: dict[str, Any], priority: str = "realtime") -> dict[str, Any]:
        return await invoke_template(tpl_id, project_id, materials, priority)

    _tool.__name__ = tool_name
    _tool.__doc__ = (
        f"{tpl_desc}\n\n"
        f"Pipeline: {tpl.get('pipeline', '')}\n"
        f"Input nodes: {', '.join(tpl.get('input_nodes', []))}\n\n"
        "Args:\n"
        "    project_id: Project this job belongs to.\n"
        "    materials: Node input overrides, keys like '{node_id}.inputs.{field}'.\n"
        "    priority: 'realtime' or 'background'.\n"
    )
    mcp.tool()(_tool)


# ─────────────────── Entry points ───────────────────

def run_stdio() -> None:
    """Run MCP server in stdio mode (for Claude Desktop local config)."""
    import asyncio
    asyncio.get_event_loop().run_until_complete(_register_template_tools())
    mcp.run(transport="stdio")


# ASGI app for HTTP/SSE mode (mounted by uvicorn or docker-compose)
asgi_app = mcp.get_asgi_app()


if __name__ == "__main__":
    run_stdio()
